# PR description 更新と `--body-file` 使用時の規約

## 作成後に PR description を更新する場合

同一手順は Step 10 で対象ブランチに既存 PR が見つかった場合の本文更新にも適用する (その場合の `<PR_NUMBER>` は `gh pr list` で取得した既存 PR 番号)。

**まず `gh pr edit --body-file <file>` を試す** (gh 2.90.0 以降は成功が確認されている)。**Projects Classic deprecation エラーが出た場合のみ** GitHub REST API (`gh api ... --method PATCH -F body=@<file>`) にフォールバックする。本 skill は npx skills add で配布され gh バージョンを仮定できないため、try-then-fallback が新旧両 gh で堅牢。固定パス禁止 / `mktemp` 規約 (下記) はどちらの経路でも維持する。

## 前提: 固定パス (`/tmp/pr-body.md` 等) を使わない

body の一時ファイルは `mktemp` で作り、コマンド終了後に削除する。固定パスや既存ファイルを再利用しない。

## 手順

```bash
# 1. body を一時ファイルに書き出す（mktemp でユニークパス生成）
PR_BODY_FILE=$(mktemp --suffix=.md)
cat <<'EOF' > "$PR_BODY_FILE"
## やったこと
...
EOF

# 2. Projects Classic deprecation のときだけ REST API にフォールバック
PR_NUMBER=<作成した PR 番号>
if ! EDIT_ERROR=$(gh pr edit "$PR_NUMBER" --body-file "$PR_BODY_FILE" 2>&1); then
  case "$EDIT_ERROR" in
    *"Projects (classic)"*|*"Projects Classic"*)
      REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
      gh api "repos/${REPO}/pulls/${PR_NUMBER}" --method PATCH -F "body=@${PR_BODY_FILE}"
      ;;
    *) printf '%s\n' "$EDIT_ERROR" >&2; exit 1 ;;
  esac
fi

# 3. 一時ファイル削除
rm "$PR_BODY_FILE"
```

## 補足

- `-F "body=@<path>"` はファイル内容をリクエストボディの文字列値として送信する gh CLI 機能（`--field` の `@` プレフィックスと同じ）
- description 更新は `gh pr edit --body-file` を第一手とし、deprecation エラー時のみ REST API へ切替える
- 同じ `mktemp` 規約は Step 10 (`gh pr create`) で `--body` ではなく `--body-file` を選ぶ場合にも適用する
