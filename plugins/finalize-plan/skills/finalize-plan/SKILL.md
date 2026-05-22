---
name: finalize-plan
description: プランモードで設計が確定した後、実装に移る直前に使用。分析ファイルからAC・MECE結果を読み込み、プランファイルにブランチ・PR分割・QA手順を追記する。
---

# finalize-plan

**入出力ルール**: 分析ファイル（`.analysis.md`）からAC・MECE結果を読み込み、結果はプランファイルに追記する。

## Arguments

- `$ARGUMENTS`: プランファイルパス（省略可）
  - 指定あり: 指定されたファイルを使用
  - 指定なし: 会話コンテキストの `Plan File Info:` からパスを取得。プランモードでない場合はエラー

## Workflow

### Step 1: プランファイル特定

引数 or `Plan File Info:` からパスを抽出。見つからない場合はユーザーに確認。

### Step 1.5: 分析ファイルからAC・MECE分析結果の抽出

**分析ファイルパス**: プランファイルの拡張子前に `.analysis` を挿入する。
- 例: `~/.claude/plans/feature-xxx.md` → `~/.claude/plans/feature-xxx.analysis.md` (プランファイルは `~/.claude/plans/` 配下を推奨)

分析ファイルから以下のセクションを抽出し、QA系エージェントへのinputとする。

```
抽出対象:
- `## 受け入れ条件` セクション → ${AC_CONTENT}
  - 正常系 / 異常系 / エッジケース / 非影響確認 の各チェック項目
  - 検討観点（どの軸で分析したか）
- `## MECE分析結果` セクション → ${MECE_CONTENT}
  - ACカバレッジ検証結果
  - `[MECE追加]` タグ付きのAC追加提案
  - Critical/Important指摘
```

**必須条件:**
- 分析ファイルが存在し、AC・MECE分析結果の**両方**が含まれていること
- 分析ファイルが存在しない、またはいずれかのセクションが欠けている場合、以下のメッセージを表示して**即座に中断**する:

```
⛔ 分析ファイル（{分析ファイルパス}）にACまたはMECE分析結果が見つかりません。

/finalize-plan は AC と MECE分析結果を基にQA手順・テスト仕様を生成します。
inputなしでは品質を保証できないため、先に以下を実行してください:

1. /define-acceptance-criteria → 受け入れ条件を定義
2. /mece-plan-review → MECE完全性検証を実施

両方が完了した後、再度 /finalize-plan を実行してください。
```

### Step 1.7: AC を QA-ID 形式で事前 enumerate (main agent)

manual-qa-planner と auto-qa-planner は**同じ AC をそれぞれ独立に分類** していたため重複コストが発生していた。main agent が事前に 1 回だけ enumerate して両 planner に渡す形に再構成する。

`${AC_CONTENT}` の各 `- [ ]` 項目を以下のルールで QA-ID 付与する:

```
正常系:       QA-H-01, QA-H-02, ...  (Happy path)
異常系:       QA-E-01, QA-E-02, ...  (Error)
エッジケース: QA-D-01, QA-D-02, ...  (eDge case)
非影響確認:   QA-R-01, QA-R-02, ...  (Regression)
[MECE追加]:   QA-M-01, QA-M-02, ...  (Mece)
```

**0 件カテゴリの扱い**: 該当 AC が 0 件のカテゴリは **QA-ID を発行しない** (例: 非影響確認 0 件なら QA-R-* は生成しない)。Step 3 の出力テンプレで対象 AC 行に `非影響0` と件数のみ表記する (詳細は Step 3 の `0 件カテゴリの表記` 規則を参照)。

```
${ENUMERATED_QA_AC} の生成例:
- QA-H-01 (正常系): req_form: 本人が PATCH /api/users/123 → 200 OK
- QA-H-02 (正常系): permission: 管理者が PATCH /api/users/123 → 200 OK
- QA-E-01 (異常系): req_form: 本文なしで PATCH → 400 Bad Request
- QA-D-01 (エッジ): permission [境界値: 未ログイン]: PATCH /api/users/:id → 401
- QA-R-01 (非影響): /api/health が変更前と同じ挙動
- QA-M-01 ([MECE追加]): observability: 監査ログに変更前後の差分が記録される
```

これを `${ENUMERATED_QA_AC}` 変数として保持し、manual-qa-planner と auto-qa-planner の両方に渡す (各 planner は自前で再分類しない、main agent の分類結果を信頼)。

**Step 1.7 失敗時 (main agent 側 fallback)**:
- AC セクションが空 / 全項目分類不能 → AskUserQuestion で「AC が分類できません。`/define-acceptance-criteria` を再実行するか、AC を手動で正常系/異常系/エッジ/非影響/[MECE追加] にラベル付けしてください」と確認
- 一部 AC のみ不明 → 不明項目を `QA-X-NN` で enumerate し、両 planner に「QA-X-* は分類不能、推測してフォロー + Self-report 明示」と注釈付与

### Step 2A: branch-planner → pr-splitter を直列実行

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

### Step 2B: manual-qa + auto-qa を並列実行 (enumerated AC を共有)

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

**実行構成 (Step 2A + 2B)**:
- Step 2A 完了後に Step 2B を起動 (直列)
- Step 2B 内では manual-qa + auto-qa を**同一メッセージ内で並列起動**
- 全体として「直列 (branch → pr-splitter) → 並列 (manual-qa + auto-qa)」の 1 直列 + 2 並列構成

**Task ツールが利用不可な環境** (subagent として動作中 / tool deferred / dispatch 権限なし):
1. 4 agent 定義 (`agents/{branch-planner,pr-splitter,manual-qa-planner,auto-qa-planner}.md`) を Read で順次読込
2. 本 agent 自身が各 agent の判定基準・出力フォーマットを適用し、各サブセクション (ブランチ戦略 / PR 分割 / 手動 QA / 自動 QA) を内部生成 (中間出力なし)
3. Step 3 の「実装準備」追記時に、`## 実装準備` 見出しの**直下 1 行目**として `> **備考**: 本実行は Task ツール利用不可のため in-context 代替モードで実行 (4 agent 定義をメイン agent が逐次適用)。` を必ず挿入。AC トレーサビリティ・PR ガイドライン (≤2 commits / ≤5 files) は通常モードと同じ

### Step 3: 結果統合

各エージェントの結果を統合し、プランファイルに「実装準備」セクションとして追記する。

追記フォーマット:

```markdown
---

## 実装準備

### ブランチ戦略

git checkout -b feature/xxx

命名理由: [理由]
既存ブランチ確認: [重複なし | 重複あり → 連番付与]

### PR分割計画

| PR | スコープ | ファイル数目安 | 依存 |
|----|----------|----------------|------|
| PR1 | ... | 3-5 | - |
| PR2 | ... | 3-5 | PR1 |

**PRチェーン図**:
develop
  └── feature/main (PR1)
        └── feature/main-frontend (PR2)

### 手動QA手順

**環境**: {BASE_URL}（QA 実行時にユーザーから取得。例: ローカル / staging 等）
**対象AC**: N項目（正常系X / 異常系Y / エッジZ / 非影響W / MECE追加V）
[Chrome DevTools MCP で実行可能な手順を記載]

**0 件カテゴリの表記**: 該当 AC が 0 件のカテゴリも `0/0` と明示する (例: `非影響0 / MECE追加1`)。「カテゴリごと省略」は読み手が「忘れた」のか「該当ゼロ」のか区別できないため禁止。

### 自動QA（テストコード仕様）

[RSpec/Vitestのテスト仕様を記載]
```

## Quality Standards

- **PRガイドライン準拠**: 2コミット以内、ファイル数5以下
- **実行可能性**: Chrome DevTools MCPで実行可能な手動QA手順
- **ACトレーサビリティ**: 全AC項目が手動QAまたは自動QAのいずれかでカバーされていること

## 併用推奨 skill

- `/define-acceptance-criteria` — 入力となる AC を定義する
- `/mece-plan-review` — AC の網羅性を 3 視点で検証してから本スキルに引き継ぐ
- `/qa-ui` — 実装完了後、本スキルで定めた QA 手順を用いて UI 検証する
- `/create-pr` — finalize で固めた PR 分割をもとに PR を作成する
