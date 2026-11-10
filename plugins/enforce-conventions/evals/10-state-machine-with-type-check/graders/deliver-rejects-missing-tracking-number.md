---
type: llm
focus: {source: file, path: repo/src/shipment.ts}
---
repo/src/shipment.ts の deliver を評価する。deliver の第 1 引数の型が、trackingNumber が null でありうる shipment を受け付けない定義になっていれば pass。手段は問わない。deliver が trackingNumber に null を許す shipment を受け付ける型のままなら fail。
