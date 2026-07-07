# Agent orchestration (Step 2A / 2B)

全体構成: **単独 (Step 2A: branch-planner) → 並列 (Step 2B: manual-qa + auto-qa)**。1 単独 + 2 並列。

以下のレシピの `${CLAUDE_PLUGIN_ROOT}` はプレースホルダのまま記載している。実行時にこれが生文字列のまま残っている場合の解決方法は SKILL.md の「## 委譲実行」規則 (`${CLAUDE_PLUGIN_ROOT}` の解決) を参照し、nested Task の prompt には読み替え後の絶対パスを埋め込む。

## Step 2A: branch-planner

```
Task(subagent_type="general-purpose", prompt="""
${CLAUDE_PLUGIN_ROOT}/skills/finalize-plan/agents/branch-planner.md を読み込み、
以下のプランに基づいて起点ブランチと単一の作業ブランチ名を策定してください:

## プラン:
${PLAN_CONTENT}
""")
→ 結果を ${BRANCH_RESULT} として保持
```

Step 1.7 で `${ENUMERATED_QA_AC}` を先に生成してから Step 2A を起動する順序は変わらず維持する (Step 2B の両 planner がこの enumerate 結果を入力に使うため)。

## Step 2B: manual-qa + auto-qa (並列、同一メッセージ内)

Step 1.7 で生成した `${ENUMERATED_QA_AC}` を両 planner に渡す。両 planner は QA-ID を信頼して、各 ID に対応する操作手順 / テスト仕様だけを生成する (AC の再分類処理は廃止):

```
Task(subagent_type="general-purpose", prompt="""
${CLAUDE_PLUGIN_ROOT}/skills/finalize-plan/agents/manual-qa-planner.md を読み込み、
以下の enumerated AC を基に手動 QA 手順を策定してください:

## プラン:
${PLAN_CONTENT}

## Enumerated AC (QA-ID 付き、main agent が事前分類済み):
${ENUMERATED_QA_AC}

## MECE 分析結果:
${MECE_CONTENT}
""")

Task(subagent_type="general-purpose", prompt="""
${CLAUDE_PLUGIN_ROOT}/skills/finalize-plan/agents/auto-qa-planner.md を読み込み、
以下の enumerated AC を基にテストコード仕様を生成してください:

## プラン:
${PLAN_CONTENT}

## Enumerated AC (QA-ID 付き、main agent が事前分類済み):
${ENUMERATED_QA_AC}

## MECE 分析結果:
${MECE_CONTENT}
""")
```

Step 2A 完了後に Step 2B を起動し、Step 2B 内では **manual-qa + auto-qa を同一メッセージ内で並列起動**する。

## Task ツールが利用不可な環境 (in-context fallback)

Task (Agent) ツールが自分の利用可能ツール一覧に無い場合 (tool deferred 等):

1. 3 agent 定義 (`${CLAUDE_PLUGIN_ROOT}/skills/finalize-plan/agents/{branch-planner,manual-qa-planner,auto-qa-planner}.md` — SKILL.md「## 委譲実行」の `${CLAUDE_PLUGIN_ROOT}` 解決規則で導いた絶対パスを使う。Read は絶対パス必須のため相対パスのままでは読めない) を Read で順次読込
2. 本 agent 自身が各 agent の判定基準・出力フォーマットを適用し、各サブセクション (ブランチ戦略 / 手動 QA / 自動 QA) を内部生成 (中間出力なし)
3. Step 3 の「実装準備」追記時に、`## 実装準備` 見出しの直後 (見出し → 空行 1 つ → 備考 blockquote の順で、本文サブセクションより前) に次の備考を必ず挿入:

   ```
   > **備考**: 本実行は Task ツール利用不可のため in-context 代替モードで実行 (3 agent 定義をメイン agent が逐次適用)。
   ```

QA-ID トレーサビリティは通常モードと同じ。
