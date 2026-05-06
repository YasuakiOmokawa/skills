---
allowed-tools: Read, Write, Glob, Bash(mkdir *), Bash(ls *), Bash(git *), AskUserQuestion
description: omokawa-skills を使うリポジトリ用の設定値を docs/agents/*.md に生成する初期セットアップ
argument-hint: ""
model: inherit
---

# Setup Omokawa Skills

omokawa-skills プラグインに含まれる create-jira-issues / set-jira-story-points / create-pr などのスキル/コマンドが必要とする**プロジェクト固有の設定値**を、対話的に質問して `docs/agents/*.md` に書き出す。

このコマンドはプロジェクトごとに**1回だけ**実行する。次回以降は生成された `docs/agents/*.md` を直接編集すれば調整できる。

## 出力するファイル

- `docs/agents/jira.md` — Jira Cloud ID, プロジェクトキー, MCP プレフィックス
- `docs/agents/release-labels.md` — Productivity/AI Contribution/Release Level ラベル定義 + 根幹機能リスト
- `docs/agents/environments.md` — integration 環境名リスト（rollback 対象）

## ワークフロー

### Step 1: 既存状態の確認

```
git rev-parse --show-toplevel  # リポジトリルート取得
ls docs/agents/ 2>/dev/null    # 既存ファイル確認
```

既に `docs/agents/jira.md` などが存在する場合は、各セクションで「現在の値」を提示し「上書きするか」を1つずつ確認。

### Step 2: 質問を3セクションに分けて順に進める

**1セクションずつ提示**。全部一気に聞かない（mattpocock 流）。各セクションは「短い説明 → 質問 → 推奨デフォルト」の順。

#### Section A — Jira 設定

> Jira を使うか聞く。Jira を使わないなら `docs/agents/jira.md` は生成しない。

`AskUserQuestion` で以下を確認:

1. **Jira を使うか？** (yes/no)
   - no なら Section A をスキップして Section B へ
2. **Jira Cloud ID** (UUID 形式 36文字)
   - 不明なら「`mcp__<atlassian-mcp>__getAccessibleAtlassianResources` で取得できる」と案内
   - 入力された値が UUID 形式 (`[a-f0-9-]{36}`) かバリデーション
3. **Jira プロジェクトキー** (例: `PROJ`, `XPROJ`)
4. **Jira MCP プレフィックス** (例: `fdev-jira`, `atlassian`, `claude_ai_Atlassian`)
   - デフォルト: 利用者の MCP 環境にあるものを `ToolSearch("+jira")` で確認して提示
5. **Atlassian MCP プレフィックス** (例: `fdev-atlassian-v2`, `atlassian`)
   - デフォルト: `ToolSearch("+atlassian")` で確認して提示

#### Section B — リリースラベル

> Issue tracker のラベル運用を聞く。ラベルが未設定の組織なら `release-labels.md` の生成自体をスキップしてもよい。

1. **Productivity ラベルを使うか？** (yes/no)
   - yes なら、ラベル名を5つ列挙してもらう（推奨デフォルト: `1.Feature development`, `2.Bugfix & Maintenance`, `3.Tech investment`, `4.Quality improvement`, `5.Others`）
2. **AI Contribution ラベルを使うか？** (yes/no)
   - yes なら、4段階のラベル名を聞く（推奨デフォルト: `ai-contribution-level:0` 〜 `ai-contribution-level:3`）
3. **Release Level ラベルを使うか？** (yes/no)
   - yes なら、4段階のラベル名を聞く（推奨デフォルト: `ReleaseLevel-1` 〜 `ReleaseLevel-4`）
4. **プロジェクトの根幹機能** (複数行入力、改行区切り)
   - 「契約締結・署名」「決済処理」「認証」など、ドメインを2〜5項目で列挙
   - 不明なら空欄でも可（その場合は CLAUDE.md / README.md から推定する旨を `release-labels.md` に書く）

#### Section C — Integration 環境

> 本番/staging 以外に、デプロイ対象となる「integration 環境」があるか聞く。無ければ `environments.md` の生成自体をスキップ。

1. **Integration 環境はあるか？** (yes/no)
   - no ならスキップ
2. **環境名リスト** (改行区切り、例: `dev1`, `dev2`, `qa-stage`)
   - rollback 手順に列挙される名前

### Step 3: 内容のプレビューと最終確認

3ファイルの**ドラフト全文**を `Read` の代わりにユーザーに見せ、`AskUserQuestion` で「この内容で書き込んでよいか」を確認する。「No」なら該当セクションを再質問。

### Step 4: ファイル書き込み

`Write` ツールで以下を順に作成:

#### `docs/agents/jira.md` のテンプレート

```markdown
# Jira 設定

omokawa-skills の create-jira-issues / set-jira-story-points / map-user-stories が参照する設定値。

## 設定値

- cloud_id: <ユーザー入力>
- project_key: <ユーザー入力>
- jira_mcp: <ユーザー入力>
- atlassian_mcp: <ユーザー入力>
- story_points_field: customfield_10005  # Jira 標準

## 使い方

スキル本体は `<atlassian-mcp>` / `<jira-mcp>` プレースホルダーを使う。実行時に上記の値で展開すること。
```

#### `docs/agents/release-labels.md` のテンプレート

```markdown
# リリースラベル設定

omokawa-skills の create-pr コマンドが参照するラベル定義。

## productivity_labels

- <ラベル1>: <説明>
- ...

## ai_contribution_labels

- <ラベル1>: <説明>
- ...

## release_level_labels

- <ラベル1>: <説明>
- ...

## core_features

プロジェクトの根幹機能（ReleaseLevel 高レベル判定に使用）:

- <機能1>
- <機能2>
- ...
```

#### `docs/agents/environments.md` のテンプレート

```markdown
# 環境設定

omokawa-skills の create-pr コマンドが Revert 手順に列挙する環境名。

## rollback_targets

production / sandbox / staging に追加して列挙する integration 環境:

- <env1>
- <env2>
- ...
```

### Step 5: 完了報告

書き込んだファイル一覧を表示し、次のアクションを案内:

```
✅ 設定完了。以下を生成しました:
- docs/agents/jira.md
- docs/agents/release-labels.md
- docs/agents/environments.md

次の操作:
- /create-jira-issues でJiraチケットを作成
- /create-pr でPRを作成（ラベルが自動付与される）
- 値を変更したい場合は上記ファイルを直接編集
```

## エラーハンドリング

- ユーザーが Section A〜C をすべて「使わない」と答えた場合 → 「設定するものがありません」と表示して終了
- リポジトリ外で実行された場合 → `git rev-parse --show-toplevel` が失敗するので、`カレントディレクトリ`に作成するか聞く
- 既存ファイルが存在する場合 → 各セクション開始時に「上書きする/スキップする/マージする」を確認

## 注意事項

- このコマンドは**ファイル書き込みのみ**。Jira API などへの実通信はしない
- 入力された Cloud ID は UUID 形式バリデーションのみ。実在性は確認しない
- 設定後は `docs/agents/*.md` をリポジトリにコミットすることを推奨（チーム全員で共有する値）
