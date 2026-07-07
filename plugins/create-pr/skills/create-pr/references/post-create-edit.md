# PR description 更新と `--body-file` 使用時の規約

## 作成後に PR description を更新する場合

同一手順は Step 10 で対象ブランチに既存 PR が見つかった場合の本文更新にも適用する (その場合の `<PR_NUMBER>` は `gh pr list` で取得した既存 PR 番号)。

**まず `gh pr edit --body-file <file>` を試す** (gh 2.90.0 以降は成功が確認されている)。**Projects Classic deprecation エラーが出た場合のみ** GitHub REST API (`gh api ... --method PATCH -F body=@<file>`) にフォールバックする。本 skill は npx skills add で配布され gh バージョンを仮定できないため、try-then-fallback が新旧両 gh で堅牢。固定パス禁止 / `mktemp` 規約 (下記) はどちらの経路でも維持する。

## 前提: 固定パス (`/tmp/pr-body.md` 等) を使わない

過去セッションが同一パスに残した body 内容 (stale content) を読み込まずに `gh api -F body=@<file>` や `gh pr create --body-file <file>` に渡すと、無関係な PR 内容が投入される事故が発生する。Write の「File has not been read yet」エラーを軽視すると同様の事故になる。

**回避**: body をヒアドキュメントで一時ファイル化する場合、固定パスではなく `mktemp` でユニークパスを生成し、終了時に削除する。ランダム名のため衝突せず、rm し損ねても他セッションには影響しない。

## 手順

```bash
# 1. body を一時ファイルに書き出す（mktemp でユニークパス生成）
PR_BODY_FILE=$(mktemp --suffix=.md)
cat <<'EOF' > "$PR_BODY_FILE"
## やったこと
...
EOF

# 2. まず gh pr edit --body-file を試し、失敗時のみ REST API にフォールバック
PR_NUMBER=<作成した PR 番号>
if ! gh pr edit "$PR_NUMBER" --body-file "$PR_BODY_FILE"; then
  # Projects Classic deprecation エラー等で失敗した場合のみ
  REPO=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
  gh api "repos/${REPO}/pulls/${PR_NUMBER}" --method PATCH -F "body=@${PR_BODY_FILE}"
fi

# 3. 一時ファイル削除
rm "$PR_BODY_FILE"
```

## 補足

- `-F "body=@<path>"` はファイル内容をリクエストボディの文字列値として送信する gh CLI 機能（`--field` の `@` プレフィックスと同じ）
- タイトル・ラベル更新は `gh pr edit --title` / `gh pr edit --add-label` で動作する。description 更新も `gh pr edit --body-file` を第一手とし、deprecation エラー時のみ REST API へ切替える
- 同じ `mktemp` 規約は Step 10 (`gh pr create`) で `--body` ではなく `--body-file` を選ぶ場合にも適用する

## nested JSON が必要なケース

`-F dot.path=val` の dot 記法では nested object が確実に組み立たず 422 が返る。`--input -` + JSON heredoc を使う:

```bash
gh api -X PUT repos/.../branches/main/protection --input - <<'EOF'
{
  "required_status_checks": { "strict": true, "contexts": [...] },
  "required_pull_request_reviews": { "required_approving_review_count": 0 }
}
EOF
```
