# 関連リポジトリ取得 (Step 0-4 詳細)

Wiki Researcher 用に `${RELATED_REPOS}` を確定する。

## GitHub org の解決手順 (必ずこの順序)

1. `~/.claude/skills-config/mece-plan-review.md` を Read し、`github_org:` フィールドを取得
2. 未設定 / ファイル無し → `git remote get-url origin` から `<org>/<repo>` を抽出し、`<org>` 部分を採用
3. ステップ 1-2 いずれも失敗 → 関連リポ収集を**スキップ**し、以下リテラルで確定して §0-5 へ進む (gh コマンド未実行):
   `${RELATED_REPOS}="なし (org 未解決のため関連リポ調査スキップ)"`

## org 解決成功時のみ実行

```bash
gh repo list ${GITHUB_ORG} --limit 200 --json name,description --jq '.[] | "\(.name)\t\(.description)"'
```

取得したリポジトリ一覧とプラン内容を照合し、関連性の高いリポジトリを 5〜10 件選定。**選定基準**: プラン本文の固有名詞 (サービス名 / モデル名 / API 名) と repo description のキーワード一致を優先。

**⚠️ 重要**: 選定したリポジトリ名は `${GITHUB_ORG}/<リポジトリ名>` 形式で保持する (Devin wiki の `repoName` 引数にそのまま渡す)。

## `${RELATED_REPOS}` の 3 状態と意味 (区別必須)

| 状態 | `${RELATED_REPOS}` の値 | Wiki Researcher 期待動作 |
|---|---|---|
| gh 成功 + 1 件以上選定 | `${GITHUB_ORG}/<repo1>\n${GITHUB_ORG}/<repo2>\n...` (改行区切り) | カレントリポ + 列挙された関連リポを Devin wiki で順次調査 |
| gh 成功 + 0 件選定 | `"なし"` リテラル | **カレントリポのみ調査** (関連リポは無いが調査自体は実施) |
| org 解決失敗 (gh 未実行) | `"なし (org 未解決のため関連リポ調査スキップ)"` リテラル | **カレントリポも含めて関連リポ調査スキップ** (org 未解決のため Devin wiki 経路全体が機能しない、`[Devin未使用]` タグ付与) |
