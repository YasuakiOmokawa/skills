---
type: llm
focus: {source: file, path: repo/plans/webhook.md}
---
計画の `## MECE Review` と `## Verification Plan` を見る。対象は、4xx で再試行しないこと、同一 `webhookId` の同時実行が最大 1 件であること、`subscriptions` を変えないことの 3 つの基準である。次のどちらかなら pass。

- (a) `## MECE Review` の Gate が ready でなく、その理由に、固定時間の待機では不在・並行性・非影響を示せないこと (またはその検証の手段が欠けていること) を挙げている。
- (b) `## Verification Plan` の 3 つの基準のエントリがそれぞれ、対象経路が完了したことを示す肯定的な観測 (`deliver` の完了の待ち合わせ、`transport.post` の呼び出し回数、同時実行中の最大数、開始前後の `db.snapshotSubscriptions()` の比較など) を `- Oracle:` か `- Required effects:` に書くか、その観測手段が無いことを `- Prerequisites:` に未解決として書いている。

Gate を ready にしたうえで、「N 秒待って何も起きないことを確認する」のような固定時間の待機だけを完了の根拠にしたエントリが 1 つでもあれば fail。固定待機が不十分だと説明していること、肯定的な観測に加えて待機を併用することは fail としない。
