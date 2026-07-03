# Agent orchestration (Step 2A / 2B)

全体構成: **直列 (Step 2A: branch-planner → pr-splitter) → 並列 (Step 2B: manual-qa + auto-qa)**。1 直列 + 2 並列。

## Step 2A: branch-planner → pr-splitter (直列)

両 agent は軽量で順序依存 (pr-splitter は branch-planner の base ブランチ名を `<base>-<suffix>` で派生に使う) のため、並列起動の旨味がなく直列実行する。

```
1. Task(subagent_type="general-purpose", prompt="""
   ${CLAUDE_PLUGIN_ROOT}/skills/finalize-plan/agents/branch-planner.md を読み込み、
   以下のプランに基づいてベースブランチを策定してください:

   ## プラン:
   ${PLAN_CONTENT}
   """)
   → 結果を ${BRANCH_RESULT} として保持

2. Task(subagent_type="general-purpose", prompt="""
   ${CLAUDE_PLUGIN_ROOT}/skills/finalize-plan/agents/pr-splitter.md を読み込み、
   以下のプランとベースブランチ名に基づいて PR 分割計画を策定してください:

   ## プラン:
   ${PLAN_CONTENT}

   ## ベースブランチ (branch-planner 結果):
   ${BRANCH_RESULT}
   """)
   → 結果を ${PR_SPLIT_RESULT} として保持
```

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

subagent として動作中 / tool deferred / dispatch 権限なしの場合:

1. 4 agent 定義 (`agents/{branch-planner,pr-splitter,manual-qa-planner,auto-qa-planner}.md`) を Read で順次読込
2. 本 agent 自身が各 agent の判定基準・出力フォーマットを適用し、各サブセクション (ブランチ戦略 / PR 分割 / 手動 QA / 自動 QA) を内部生成 (中間出力なし)
3. Step 3 の「実装準備」追記時に、`## 実装準備` 見出しの直後 (見出し → 空行 1 つ → 備考 blockquote の順で、本文サブセクションより前) に次の備考を必ず挿入:

   ```
   > **備考**: 本実行は Task ツール利用不可のため in-context 代替モードで実行 (4 agent 定義をメイン agent が逐次適用)。
   ```

QA-ID トレーサビリティ・PR ガイドライン (≤2 commits / ≤5 files) は通常モードと同じ。
