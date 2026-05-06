---
name: create-jira-issues
description: ユーザーストーリーマップやタスク分解プランからJiraチケットを一括作成する場合に使用。ストーリーマップ完成後のチケット化、プランファイルからの一括作成、計画済みストーリー・タスクのJiraへの移行が必要な場合にトリガーされる。
---

# create-jira-issues

## Quick Reference — APIパターン早見表

⚠️ **MCP プレフィックスは環境依存**: 以下の優先順位で取得
  1. `~/.claude/skills-config/jira.md` の `jira_mcp` / `atlassian_mcp` フィールド（`/setup-omokawa-skills` で生成）
  2. `ToolSearch("+jira")` または `ToolSearch("+atlassian")` で実環境のプレフィックスを確認

下表の `<jira-mcp>` / `<atlassian-mcp>` はプレースホルダー。実環境のプレフィックス例: `fdev-jira` / `atlassian` / `claude_ai_Atlassian`。

| 操作 | <jira-mcp> | Atlassian MCP (環境例) |
|------|-----------|---------------|
| チケット作成 | `mcp__<jira-mcp>__create_issue` | `mcp__<atlassian-mcp>__createJiraIssue` |
| チケット更新 | ❌ 権限エラーで失敗（CLAUDE.md既知問題） | `mcp__<atlassian-mcp>__editJiraIssue` (任意フィールド) |
| コメント追加 | `mcp__<jira-mcp>__add_comment` | `mcp__<atlassian-mcp>__addCommentToJiraIssue` |
| issueType一覧 | `mcp__<jira-mcp>__list_jira_issue_types` | `mcp__<atlassian-mcp>__getJiraProjectIssueTypesMetadata` |
| フィールドID取得 | — | `mcp__<atlassian-mcp>__getJiraIssueTypeMetaWithFields` |
| カスタムフィールド設定 | ❌ 不可 | ✅ editJiraIssue の fields で設定 |
| issueリンク作成 | ❌ 不可 | ❌ 専用ツール無し（手動設定リストへ） |
| cloudId取得 (Atlassian専用) | — | `mcp__<atlassian-mcp>__getAccessibleAtlassianResources` |

## ワークフロー

### Step 0: MCPプロバイダ検出

```
ToolSearch("+<jira-mcp>")
  → 見つかった場合: <jira-mcp>用フロー
  → 見つからなかった場合:
    ToolSearch("+atlassian jira")
      → 見つかった場合: Atlassian MCP用フロー
      → 見つからなかった場合:
        「エラーが発生しました。Jira MCPを利用可能にしてください」
        → 停止
```

⚠️ **2系統を無条件に混在使用しない**。検出結果に基づいて1系統のみ使用する。

### Step 1: プランファイル解析

入力プランファイルから以下をパース:

1. `## Phase N:` ヘッダー直下のMarkdownテーブル → US一覧
2. `## タスクリスト` ヘッダー直下の ` ```tsv ` コードフェンス → タスク一覧

**パース契約**:
- USテーブル必須カラム: `US_ID | ユーザー | ストーリー | 受入条件 | 依存US | Jira | 技術メモ`
- タスクTSV必須カラム: `US_ID	Task_ID	タスク名	説明	依存タスク	Jira	備考`

パース失敗時: 「プランファイルのフォーマットが map-user-stories の出力契約と一致しません」 → 停止

### Step 2: Jira設定確認

以下を確認:
- **プロジェクトキー** (例: XPROJ)
- **Epic（親チケット）** (例: XPROJ-50)
- **issueType名** → 実環境で確認して選択

issueType 確認手順（必ず実行）:
1. **<jira-mcp> 経路**: `list_jira_issue_types` を呼ぶ。権限エラー/存在エラーなら skill のフォールバック値「ストーリー」「サブタスク」を採用し、ユーザーに「issueType 一覧取得失敗 → 既定値で継続してよいか」を1行で確認してから進む
2. **Atlassian 経路**: `getJiraProjectIssueTypesMetadata(projectKey=...)` を呼ぶ。同じくフォールバック値と確認プロンプト
3. **cloudId（Atlassian 経路のみ必須）**: `getAccessibleAtlassianResources` を呼んで取得。値はユーザー入力不要、以降の全 Atlassian 呼び出しに付ける
4. **customfield ID（Atlassian 経路のみ、Team 等を設定する場合）**: `getJiraIssueTypeMetaWithFields(projectKey, issueTypeId)` でフィールド ID を取得。取得失敗時は手動設定リストに回す

⚠️ **issueType名の罠**: 「タスク」はストーリーと同じhierarchyLevel → 親子関係を作れない。サブタスクには必ず「サブタスク」(hierarchyLevel: -1) を使う。

```
Epic (hierarchyLevel: 1)
  └── ストーリー (hierarchyLevel: 0)  ← issueType: "ストーリー"
        └── サブタスク (hierarchyLevel: -1)  ← issueType: "サブタスク"
```

### Step 3: USストーリー一括作成

全USを**順次**作成し、作成されたキーを**即時記録**:

```
【<jira-mcp>】
  mcp__<jira-mcp>__create_issue(
    project_key, issue_type: "ストーリー",
    summary: "US-XXX: {ストーリー要約}",
    description: "{ストーリー全文 + 受入条件}",
    parent_issue_key: {Epic}
  )
  → 返却キーを記録
  → Teamフィールド設定不可 → 以下 2 つの処理は **どちらか一方** を選ぶ:
    (a) add_commentで "Team: {チーム名}" を残す（将来の検索用、任意）
    (b) 手動設定リスト 1 行に追記（推奨、ユーザーが Jira UI で設定できる）
    ※ 両方同時には書かない（二重管理を避ける）。本 skill の既定は (b) のみ。

【Atlassian MCP (例: mcp__<atlassian-mcp>__)】
  # 前提: Step 2 で cloudId と Team customfield ID は取得済み
  createJiraIssue(
    cloudId: {取得済み},
    projectKey, issueTypeName: "ストーリー",
    summary: "US-XXX: {ストーリー要約}",
    description: "{ストーリー全文 + 受入条件}",
    parent: {Epic}
  )
  → 返却キーを記録
  → Team を customfield で設定する場合:
    editJiraIssue(cloudId, issueIdOrKey, fields: { "{team_customfield_id}": "{チーム名}" })
    ※ customfield ID が未取得なら手動設定リストに回す（擬似 ID を仮置きしない）
```

### Step 4: サブタスク一括作成

全タスクを**順次**作成（parent: 対応するUSストーリーのキー）:

```
【<jira-mcp>】
  mcp__<jira-mcp>__create_issue(
    project_key, issue_type: "サブタスク",
    summary: "{タスク名}",
    description: "{説明}",
    parent_issue_key: {USストーリーのキー}
  )

【Atlassian MCP (例: mcp__<atlassian-mcp>__)】
  createJiraIssue(
    cloudId: {取得済み},
    projectKey, issueTypeName: "サブタスク",
    summary, description,
    parent: {USストーリーのキー}
  )
```

各作成後に**プランファイルのJira列を即時更新**（インクリメンタル記録）。

⚠️ **プラン書き戻しを忘れない**。

### Step 5: 手動設定リスト出力

MCPで自動設定できない項目を明確なリストとして出力:

```
【<jira-mcp> の場合】

## 手動設定が必要な項目

### Teamフィールド設定（{N}件）
以下のチケットにTeamフィールドを手動設定してください:
- XPROJ-501 (US-001)
- XPROJ-502 (US-002)
- ...

### タスク間依存リンク（{N}件）
以下の "is blocked by" リンクを手動設定してください:
- XPROJ-510 is blocked by XPROJ-508
- XPROJ-511 is blocked by XPROJ-508, XPROJ-509
- ...
```

⚠️ **手動設定リストを省略しない**。description内埋込ではなく、コピペ可能なリスト形式で出力する。

### Step 6: 結果レポート

```
## 作成結果

### 作成済みチケット（{N}件）
| US_ID/Task_ID | Jiraキー | summary |
|...|...|...|

### 未作成（{N}件）
| US_ID/Task_ID | 理由 |
|...|...|

### 手動設定が必要な項目
（Step 5の内容を再掲）
```

プランファイルのJira列を最終更新。

## エラーハンドリング

```
◆ Jira MCP利用不可
  → 「エラーが発生しました。Jira MCPを利用可能にしてください」と出力して停止
  → フォールバックなし

◆ 作成途中で失敗
  → 「エラーが発生しました」と出力して停止
  → 作成済みチケット一覧をプランファイルのJira列に記録済み（インクリメンタル記録のため）
  → ユーザーが問題解決後、未作成分のみ手動で再指示
```

