---
type: llm
focus: {source: file, path: plans/webhook.md}
---
`## Verification Plan` の `### AC-002`、`### AC-003`、`### AC-004` の 3 entry だけを見る。

各 entry が次のどちらかなら pass。
- (a) `- Oracle:` または `- Required effects:` に、対象経路が完了したことを示す肯定的な観測 (例: `await deliver(...)` の解決、`transport.post` の呼び出し回数、同時実行中の最大数、開始前後の `db.snapshotSubscriptions()` の比較) を書いている。
- (b) その観測手段が無いことを `- Prerequisites:` に未解決として書いている。

「N 秒待って何も起きないことを確認する」のような固定時間の待機だけを完了の根拠にしている entry が 1 つでもあれば fail。固定待機が不十分だと説明していること、肯定的な観測に加えて待機を併用することは fail としない。
