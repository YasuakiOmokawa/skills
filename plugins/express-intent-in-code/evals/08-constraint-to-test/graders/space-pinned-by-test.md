---
type: llm
focus: {source: file, path: src/receipt.test.ts}
---
src/receipt.test.ts を評価する。formatEuro (または renderReceipt) の出力に no-break space (U+202F / U+00A0) が含まれず通常の空白 (U+0020) になることを固定するテストが 1 つ以上あれば pass。例: 通常の空白を含む文字列との厳密一致、` ` や ` ` を含まないことの assert、コードポイントの比較。fixture 由来の `.` を使った tolerant な正規表現 (`/^1.234,50.€$/`) だけでは fail。
