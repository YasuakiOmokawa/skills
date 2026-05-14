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
- 例: `plans/feature-xxx.md` → `plans/feature-xxx.analysis.md`

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

### Step 2: 4並列サブエージェント起動

Task ツール（`subagent_type: "general-purpose"`）で以下を**同一メッセージ内で並列起動**。各 agent ファイル（`agents/*.md`）を読み込ませ、プランファイルの内容を渡すこと。

| Agent | ファイル | 入力 |
|-------|---------|------|
| branch-planner | `agents/branch-planner.md` | プラン |
| pr-splitter | `agents/pr-splitter.md` | プラン |
| manual-qa-planner | `agents/manual-qa-planner.md` | プラン + ${AC_CONTENT} + ${MECE_CONTENT} |
| auto-qa-planner | `agents/auto-qa-planner.md` | プラン + ${AC_CONTENT} + ${MECE_CONTENT} |

**QA系エージェントへのプロンプト例:**

```
~/.claude/skills/finalize-plan/agents/manual-qa-planner.md を読み込み、
以下のプランとAC・MECE分析結果に基づいて手動QA手順を策定してください:

## プラン:
[プランファイルの内容]

## 受け入れ条件（AC）:
[${AC_CONTENT} — 存在する場合]

## MECE分析結果:
[${MECE_CONTENT} — 存在する場合]
```

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

**環境**: http://localhost:3250
**対象AC**: N項目（正常系X / 異常系Y / エッジZ / 非影響W）
[Chrome DevTools MCP で実行可能な手順を記載]

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
