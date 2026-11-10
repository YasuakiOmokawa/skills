---
type: llm
focus: {source: file, path: repo/src/shipment.ts}
---
repo/src/shipment.ts の型定義を評価する。次の 2 つの値を、どちらも型エラー無しには書けない定義なら pass。(1) status が "shipped" で trackingNumber が null の Shipment。(2) status が "delivered" で deliveredAt が null の Shipment。ほかの状態やほかの field が null を許していても構わない。手段も問わない。(1) か (2) のどちらかを型エラー無しに書けるなら fail。
