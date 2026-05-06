# Jira 設定（example）

## このファイルの使い方

このファイルを `~/.claude/skills-config/jira.md` にコピーし、自社の値で書き換えてください。`/setup-omokawa-skills` で対話生成も可能です。

omokawa-skills の `create-jira-issues` / `set-jira-story-points` / `map-user-stories` がこのファイルを Read して値を取得します。

## 設定値

- **cloud_id**: `<YOUR_JIRA_CLOUD_ID>`
  - Atlassian テナント ID（UUID 形式 36文字）
  - 不明な場合は `mcp__<atlassian-mcp>__getAccessibleAtlassianResources` で取得可能
- **project_key**: `PROJ`
  - Jira プロジェクトキー（例: `PROJ`, `XPROJ`, `ENG`）
- **jira_mcp**: `atlassian`
  - Jira 操作用 MCP のプレフィックス。実環境のプレフィックスを ToolSearch で確認
  - 例: `fdev-jira`, `atlassian`, `claude_ai_Atlassian`
- **atlassian_mcp**: `atlassian`
  - Atlassian 操作用 MCP のプレフィックス（`editJiraIssue` など）
  - 例: `fdev-atlassian-v2`, `atlassian`, `claude_ai_Atlassian`
- **story_points_field**: `customfield_10005`
  - Story Points のカスタムフィールド ID（Jira 標準は `customfield_10005`）

## 注意

- このファイルは**機密値ではない**前提（テナント識別子であり、漏洩しても直接攻撃にはならない）
- 真に機密な API トークンなどは `.env` に保管し、このファイルに混ぜないこと
- 配置先は `~/.claude/skills-config/jira.md`（**マシンユーザーごとのグローバル設定**）。dotfiles で管理する場合はこの場所を symlink にする運用を推奨
