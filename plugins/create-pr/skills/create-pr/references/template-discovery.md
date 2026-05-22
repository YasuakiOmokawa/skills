# PR テンプレート検索 (Step 0a)

カレントブランチが属するリポジトリのテンプレートを動的に検索する。**固定パスを書かない**。

## 手順

1. `git rev-parse --show-toplevel` でリポジトリルート `<repo>` を取得
2. 以下の優先順位で最初に存在するファイルを採用:
   1. `<repo>/.github/PULL_REQUEST_TEMPLATE/engineer.md`
   2. `<repo>/.github/PULL_REQUEST_TEMPLATE/default.md`
   3. `<repo>/.github/PULL_REQUEST_TEMPLATE/` 配下の最初の `*.md`（アルファベット順）
   4. `<repo>/.github/PULL_REQUEST_TEMPLATE.md`
   5. `<repo>/.github/pull_request_template.md`
   6. `<repo>/docs/PULL_REQUEST_TEMPLATE.md`
   7. `<repo>/PULL_REQUEST_TEMPLATE.md`
3. 見つかったパスを控え、Step 6 で `Read` してセクション構成を把握
4. どれも見つからない場合はフォールバック構成（`## やったこと` / `## なぜやるのか` / `## 動作確認結果`）を使用

## ベースブランチ確定 (Step 0b)

- 引数 `[base-branch]` 指定があればそれを使用
- 無ければデフォルトブランチを取得:
  1. `gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`（主手段）
  2. 失敗時 `git symbolic-ref refs/remotes/origin/HEAD --short | sed 's@^origin/@@'`
  3. いずれも失敗で `main` フォールバック
- 以降の手順の `[base-branch]` はこの値に置換
