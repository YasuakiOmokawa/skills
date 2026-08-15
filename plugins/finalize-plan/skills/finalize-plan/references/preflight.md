# Preflight contract

プランと同じディレクトリで拡張子前へ `.preflight` を挿入する。

```markdown
## Preflight

| 項目 | 内容 |
|---|---|
| ベース URL | 未定 |
| ログイン手段 | 未定 |
| 必要な権限種別と用途 | 未定 |
| テストデータ準備手順 | 未定 |
| 起点ブランチ | main |
| サーバ・DB 起動コマンド | 未定 |
```

6候補値を上の順で `項目=内容` に正規化した SHA-256 を末尾へ `<!-- preflight source: <digest> -->` と記録する。同じ digest の再実行では user が更新した cell を保持する。digest が変わるか marker が無ければ、現在の plan / README から6行を再生成し、解決不能値を `未定` へ戻して古い値を流用しない。

- plan / README の値を転記し、推測しない。`{BASE_URL}` 等の placeholder は `未定`。
- 権限種別と用途は同じ plan の QA-ID から逆算可。特定不能なら権限名だけにする。
- パスワード、token、実アカウント、email は書かない。ログインは user が行い、自動ログインを提案・実行しない。
- cell は値だけ。機構が存在しないと確認できた項目は短い根拠付き `該当なし`。
- `未定` を含む artifact を先に Write する。不足値は一度に確認し、回答があれば cell を更新して source marker は保持する。同期的な質問ができない場合は最終報告へ列挙する。
- qa-ui は URL、権限、test data を参照する。server / DB を自動起動しない。
