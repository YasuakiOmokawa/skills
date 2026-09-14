---
type: llm
focus: {source: file, path: src/invoice.js}
---
applyDiscount が、discountRate が 0 未満または 1 より大きい場合にエラーを投げる処理を持っていれば pass。範囲チェックが無い、または片側しか検査していなければ fail。
