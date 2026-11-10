---
type: llm
focus: {source: file, path: repo/src/shipment.ts}
---
repo/src/shipment.ts を評価する。trackingUrl の引数の型が、trackingNumber を持たない準備中の shipment を受け付けない定義になっていれば pass。手段は問わない。trackingUrl がどの状態の shipment でも受け付ける型のままなら fail。
