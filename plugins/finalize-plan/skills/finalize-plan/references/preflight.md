# Preflight contract

プランと同じディレクトリで拡張子前へ `.preflight` を挿入する。

```markdown
## Preflight

| 項目 | 内容 |
|---|---|
| ベース URL | 未定 |
| ログイン手段 | 未定 |
| 権限アカウント一覧 | 未定 |
| テストデータ準備手順 | 未定 |
| 起点ブランチ | main |
| サーバ・DB 起動コマンド | 未定 |
```

- plan / README の値を転記し、推測しない。`{BASE_URL}` 等の placeholder は `未定`。
- 権限の用途だけは同じ plan の QA-ID から逆算可。特定不能なら権限名だけにする。
- パスワード、token、実アカウント、email は書かない。ログインは user が行い、自動ログインを提案・実行しない。
- cell は値だけ。機構が存在しないと確認できた項目は短い根拠付き `該当なし`。
- 不足値は一度に確認する。AskUserQuestion 不可時は最終報告へ列挙する。
- qa-ui は URL、権限、test data を参照する。server / DB を自動起動しない。
