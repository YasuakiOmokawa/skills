---
name: set-jira-story-points
description: JiraキーとStory Pointsのマップデータを受け取り、Jiraチケットに一括でStory Pointsを設定する。「ストーリーポイント設定」「SP設定」「story points」などのキーワードでトリガーされる。
---

# set-jira-story-points

## Quick Reference

| 操作 | <jira-mcp> | Atlassian MCP |
|------|-----------|---------------|
| カスタムフィールド設定 | ❌ 不可 | ✅ `editJiraIssue` の fields で設定 |

⚠️ **Story Points（`customfield_10005`）は Atlassian MCP の `editJiraIssue` でのみ設定可能。`<jira-mcp>` は非対応。**

## 前提情報

- **Jira Cloud ID**: 以下の優先順位で取得（このスキル内にハードコードしない）
  1. プロジェクトの `docs/agents/jira.md` の `cloud_id` フィールド（`/setup-omokawa-skills` で生成）
  2. `~/.claude/CLAUDE.md` の `Jira Cloud ID:` 行（ユーザー個人値）
  3. 上記が無ければ `mcp__<atlassian-mcp>__getAccessibleAtlassianResources` で動的取得
- **Story Points フィールドID**: `customfield_10005`（Jira 標準）
- **MCP プレフィックス（`<atlassian-mcp>`）**: `docs/agents/jira.md` の `atlassian_mcp` フィールド、または `ToolSearch("+atlassian")` で実環境のプレフィックスを確認
- **使用ツール**: `mcp__<atlassian-mcp>__editJiraIssue`

## 入力仕様

ユーザーが以下のいずれかの形式でマップデータを渡す:

### 形式1: key: value

```
XPROJ-101: 3
XPROJ-102: 5
XPROJ-103: 2
```

### 形式2: Markdownテーブル

```
| Jiraキー | SP |
|----------|-----|
| XPROJ-101 | 3 |
| XPROJ-102 | 5 |
```

### パース規約
- キーは `^[A-Z]+-\d+$` に**完全一致**するもののみ採用（小文字・空白混入・他文字混在は拒否）
- SP は**正の整数**のみ採用（小数・0・負数・非数値は拒否）
- Markdown テーブルは**列名で識別**: ヘッダ行で「Jiraキー」「SP」列を見つけ、その値だけを抽出。それ以外の列（メモ、担当者など）は**無視**して構わない（テーブルの列数に制限なし）
- パース結果に応じた挙動:
  - **全件失敗（有効件数 = 0）**: 「入力データのフォーマットが不正です。`Jiraキー: SP` または Markdownテーブル形式で渡してください」→ 停止
  - **一部失敗（有効件数 > 0、不正分あり）**: 停止せず、有効分のみ Step 3 へ進める。不正分は Step 4 の「拒否（パースエラー）」セクションで報告

## ワークフロー

### Step 0: MCPプロバイダ検出

```
ToolSearch("+atlassian edit")
  → editJiraIssue が見つかった場合: 続行
  → 見つからなかった場合:
    「Story Pointsの設定にはAtlassian MCPが必要です。<jira-mcp>ではカスタムフィールドに対応していません。」
    → 停止
```

⚠️ <jira-mcp>へのフォールバックは不可（カスタムフィールド非対応のため）。

### Step 1: 入力パース

ユーザーの入力からJiraキーとSPのマップを抽出する:

```
入力テキスト
  → 正規表現で key:SP ペアを抽出
  → Map<string, number> を構築
  → 0件の場合: フォーマットエラーを出力して停止
```

### Step 2: Jira Cloud ID 確認

- 「## 前提情報」の優先順位で Cloud ID を取得
- すべて失敗した場合は `getAccessibleAtlassianResources` で取得し、結果をユーザーに確認

### Step 3: Story Points 一括設定

各チケットに対して**順次**実行:

```
mcp__<atlassian-mcp>__editJiraIssue(
  cloudId: "<Step 2 で取得した Cloud ID>",
  issueIdOrKey: "<Jiraキー>",
  fields: {"customfield_10005": <SP値>}
)
```

- 成功: 記録して次へ
- 失敗: エラー内容を記録して次へ（途中停止しない）

### Step 4: 結果レポート

全件完了後に以下のテーブルを出力する。**該当 0 件のセクションは、テーブル本体を出力せず見出しの直下に「なし」とだけ書く**（例は下の「失敗」「拒否」セクション参照）:

```
## Story Points 設定結果

### 成功（N件）
| Jiraキー | SP | 結果 |
|----------|-----|------|
| XPROJ-101 | 3 | 成功 |
| XPROJ-102 | 5 | 成功 |

### 失敗（N件）
| Jiraキー | SP | エラー |
|----------|-----|--------|
| XPROJ-103 | 2 | 権限エラー: ... |

### 拒否（パースエラー）（N件）
| 入力 | 拒否理由 |
|------|---------|
| `xproj-105: 2` | キーが `^[A-Z]+-\d+$` に不一致（小文字） |
| `XPROJ-102: abc` | SP が非数値 |
| `XPROJ-103: 0.5` | SP が小数（正の整数のみ） |
```

絵文字は使わず「成功」「失敗」のテキストで表記する。

## エラーハンドリング

```
◆ Atlassian MCP利用不可
  → 「Story Pointsの設定にはAtlassian MCPが必要です」と出力して停止
  → <jira-mcp>へのフォールバックなし

◆ 入力パース失敗（全件失敗のみ = 有効件数 0）
  → 停止メッセージは次の 2 点を含めること:
    1. 文言「入力データのフォーマットが不正です。`Jiraキー: SP` または Markdownテーブル形式で渡してください」
    2. 上記「入力仕様」の **形式 1（key: value）と 形式 2（Markdownテーブル）の具体例** をユーザーが修正しやすいよう再掲
  → **一部失敗**（有効件数 > 0）の場合は停止せず、有効分のみ Step 3 を実行し、不正分は Step 4 の「拒否（パースエラー）」セクションで報告する

◆ 個別チケット失敗
  → エラーを記録して次のチケットに進む（途中停止しない）
  → 全件完了後にまとめてレポート
```
