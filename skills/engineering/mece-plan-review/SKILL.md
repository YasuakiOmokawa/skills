---
name: mece-plan-review
description: プランファイルの受け入れ条件（AC）に対しMECE完全性検証を実施し、ユースケース漏れ・技術的対応漏れ・ACの改善点を検出して分析ファイルに記録する。プランにACが定義済みで実装前にMECE検証が必要な時に使用。事前に /define-acceptance-criteria でACを定義しておくこと。
---

# MECE Plan Review

## Overview

プランファイルを3視点でMECE分析し、結果を分析ファイルに記録する。プランファイル本文は変更しない。

```
メインエージェント（あなた）: 初期化 + Red Teamレビュー + プラン修正
├─ QA Analyst     Devin wiki + コード裏取りでユースケースMECE検証 [Task subagent]
└─ Tech Analyst   コードベース独立調査で技術的対応漏れ検出 [Task subagent]
```

```
Step 0: 初期化（引数パース、AC抽出、リポ取得）
         │
Step 1: 並列分析（2 Task subagent を同一メッセージで起動）
         │  QA Analyst: Devin wiki → spec/ + プロダクションコード → ギャップ分析
         │  Tech Analyst: プランから独立にコード調査 → 技術的対応漏れ
         │
Step 2: Red Teamレビュー（メインエージェントが実行）
         │  事前分析 → QA/Tech結果のクロスリファレンス → 統合評価
         │
Step 3: 分析結果出力
         │  全指摘（Critical含む） → 分析ファイルに記録
         │  ACブラッシュアップ → 分析ファイルで [MECE追加] タグ付き
         │  サマリー1行 → プランファイルの品質検証セクション
```

## 重要ルール

1. **分析ファイルへの記録はメインエージェント（あなた）のみ**が行う
2. **Critical=0なら「MECE OK」**、1件以上なら「要修正」→ 分析ファイルに記録（プラン本文は変更しない）
3. **QA AnalystとTech Analystは独立分析**（互いの結果を参照しない）

## 進捗チェックリスト

以下をコピーして進捗を追跡:

```
MECE分析 進捗:
- [ ] Step 0: 初期化（プラン読み込み、AC抽出、リポ取得）
- [ ] Step 1: 並列分析（QA + Tech Analyst 起動）
- [ ] Step 1: 両分析結果受信
- [ ] Step 2: Red Teamレビュー（事前分析 + クロスリファレンス）
- [ ] Step 3-1: 全指摘の分析ファイル記録
- [ ] Step 3-2: ACブラッシュアップ（分析ファイル）
- [ ] Step 3-3: MECE分析結果セクション追記（分析ファイル）
- [ ] Step 3-4: プランファイルにサマリー1行追記
```

## Arguments

- `$ARGUMENTS`: プランファイルのパス
  - パス指定なし時: システムプロンプトの Plan File Info から取得
  - 例: `/mece-plan-review path/to/plan.md`

## Step 0: 初期化

### 0-1: 引数パースとプランファイル特定

`$ARGUMENTS` からプランファイルパスを取得（省略時はシステムプロンプトの Plan File Info から取得）。
プランファイル全文を Read で読み込む。

### 0-2: 分析ファイルから受け入れ条件（AC）の抽出【必須】

**分析ファイルパス**: プランファイルの拡張子前に `.analysis` を挿入する。
- 例: `plans/feature-xxx.md` → `plans/feature-xxx.analysis.md`

分析ファイルから `## 受け入れ条件` セクションを抽出する。

- **ACあり**: 検証ターゲットとして Step 1 の各サブエージェントに配布。ACの各項目に対するカバレッジ検証が分析の主軸になる。
- **分析ファイルが存在しない or ACなし**: **即座に中断**。以下のメッセージをユーザーに表示して終了する:

```
⛔ 受け入れ条件（AC）が見つかりません。

分析ファイル（{分析ファイルパス}）にACが定義されている必要があります。
MECEは「何に対して漏れがないか」を検証するプロセスです。
検証ターゲットなしでは分析の精度が保証できないため、先にACを定義してください。

👉 /define-acceptance-criteria を実行してACを定義した後、再度 /mece-plan-review を実行してください。
```

### 0-3: リポジトリ名取得

```bash
git remote get-url origin | sed 's/.*github.com[:/]\(.*\)\.git/\1/'
```

### 0-4: 関連リポジトリ取得（オプション）

```bash
gh repo list <YOUR_GITHUB_ORG> --limit 200 --json name,description --jq '.[] | "\(.name)\t\(.description)"'
```

取得したリポジトリ一覧とプラン内容を照合し、関連性の高いリポジトリを5〜10件選定する。
選定基準: プランで言及されている機能・サービス・モデルに関連するリポジトリ名・description。

**⚠️ 重要**: 選定したリポジトリ名は `<YOUR_GITHUB_ORG>/<リポジトリ名>` 形式で保持する（例: `acme/main-app`）。Devin wiki の `repoName` 引数にそのまま渡せる形式にしておく。

## Step 1: 並列分析

### 1-1: プロンプト読み込み

```
qa_prompt = Read("~/.claude/skills/mece-plan-review/references/qa-analyst-prompt.md")
tech_prompt = Read("~/.claude/skills/mece-plan-review/references/tech-analyst-prompt.md")
```

### 1-2: 2つのTask subagentを同一メッセージ内で並列起動

```
Task(subagent_type="general-purpose", name="qa-analyst", prompt="""
あなたはMECE分析のQA Analystです。以下のプロンプトに従い分析を実行してください。

${qa_prompt}

---
リポジトリ: ${REPO_NAME}
関連リポジトリ（Devin wiki の repoName にそのまま使用可能）:
${RELATED_REPOS}
プランファイル:
${PLAN_CONTENT}
受け入れ条件（検証ターゲット）:
${AC_CONTENT}

分析結果をMarkdown形式で返してください。
""")

Task(subagent_type="general-purpose", name="tech-analyst", prompt="""
あなたはMECE分析のTech Analystです。以下のプロンプトに従い分析を実行してください。
QA Analystの結果は参照せず、独立に調査してください。

${tech_prompt}

---
リポジトリ: ${REPO_NAME}
プランファイル:
${PLAN_CONTENT}
受け入れ条件（検証ターゲット）:
${AC_CONTENT}

分析結果をMarkdown形式で返してください。
""")
```

### 1-3: 両方の結果を受信

Task の戻り値として自動的に取得。変数 `${QA_RESULT}` と `${TECH_RESULT}` として保持。

## Step 2: Red Teamレビュー（メインエージェント実行）

### 2-1: チェックリスト読み込み

```
red_team_checklist = Read("~/.claude/skills/mece-plan-review/references/red-team-checklist.md")
```

### 2-2: 事前分析

`red-team-checklist.md` の「事前分析チェック観点」に従い、プラン単体を分析:

- [ ] 曖昧表現の洗い出し
- [ ] 責任の継ぎ目の特定
- [ ] 暗黙の前提の列挙
- [ ] ACとプランの乖離チェック
- [ ] スコープ外だが影響を受ける領域の確認
- [ ] 楽観的見積もりの根拠確認

### 2-3: クロスリファレンス分析

QA Analyst結果 × Tech Analyst結果を `red-team-checklist.md` の「クロスリファレンスチェック項目」に従い突合:

- [ ] **お見合い検出**: 両者がスキップした領域はないか
- [ ] **偽の合意検出**: 同結論だが異なる根拠に基づいていないか
- [ ] **根拠の弱さ**: 証拠不十分な主張はないか
- [ ] **スコープ漏れ**: 分析対象外の重要領域はないか
- [ ] 必要に応じてコードを直接 Read/Grep で裏取り

### 2-4: 統合評価レポート作成

`red-team-checklist.md` の統合評価レポートフォーマットに従い、全指摘を重要度別に集約。

## Step 3: 分析結果出力

**出力先ルール**: 全分析結果は **分析ファイル** に記録する。プランファイルにはサマリー1行のみ追記。プラン本文は一切変更しない。

### 3-1: 全指摘の分析ファイル記録

全指摘（Critical/Important/Nice-to-have）を **分析ファイル** に記録する。

- **🔴 Critical**: 分析ファイルに記録。プラン内の該当箇所（セクション名・内容）と推奨修正内容を併記する
- **🟡 Important / 🟢 Nice-to-have**: 分析ファイルに記録

### 3-2: ACブラッシュアップ

3つのインプットソースからAC改善点を収集・統合:

**QA Analyst → AC検証テーブル**
- 「不十分」（ACにあるがプラン未対応）→ 🔴
- 「過剰」（プランにあるがAC未記載）→ AC追加推奨
- 「ACにない発見」→ AC追加

**Tech Analyst → AC技術的実現性テーブル**
- 実現性「低」→ AC修正推奨（技術的制約を反映）
- 充足度「不十分」→ AC具体化推奨

**Red Team → AC↔プランの乖離テーブル + クロスリファレンス**
- ACにあるがプラン未対応 → 🔴
- プランにあるがAC未反映 → AC追加
- 「お見合い」で発見した領域 → AC追加

上記を統合し、**分析ファイル**の受け入れ条件セクションに対して以下のAC改善を実施:
- **新規AC項目追加**: `[MECE追加]` タグを付与し、元のACと区別
- **既存AC修正**: 曖昧・不十分だったAC項目の具体化
- **AC修正**: 技術的に実現不可能なACは理由付きで修正

### 3-3: MECE分析結果を分析ファイルに追記

[references/output-format.md](references/output-format.md) のフォーマットに従い、**分析ファイル**末尾に追記。

### 3-4: プランファイルにサマリーを追記

プランファイルの `## 品質検証` セクションに以下を追記する（セクションがなければ作成）:

```markdown
- MECE判定: [OK or 要修正（Critical N件）] / ACカバレッジ [N]/[M]項目 → [分析ファイル名]
```

## Error Handling

### Devin MCP 利用不可

```
ToolSearch("+devin") → 失敗
  → QA Analyst がローカル分析にフォールバック（Grep, Glob, Read）
  → 結果に [Devin未使用] タグ付与
```

### サブエージェント失敗

```
Task の戻り値がエラーまたはタイムアウト:
  → 該当ロールを [未取得] として記録
  → 残りの分析結果で Step 2-3 を続行
```

### プランファイル書き込み失敗

AskUserQuestion でパス確認を依頼。

## References

- [references/qa-analyst-prompt.md](references/qa-analyst-prompt.md) - QA Analyst 分析プロンプト
- [references/tech-analyst-prompt.md](references/tech-analyst-prompt.md) - Tech Analyst 分析プロンプト
- [references/red-team-checklist.md](references/red-team-checklist.md) - Red Team クロスリファレンスチェックリスト
- [references/output-format.md](references/output-format.md) - プラン修正・追記フォーマット
