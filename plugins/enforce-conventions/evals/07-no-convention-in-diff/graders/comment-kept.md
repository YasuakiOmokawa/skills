---
type: regex
target: {source: file, path: repo/src/domain/discount.ts}
match: contains
---
// 1 円未満は切り捨てる\n\s*return Math\.floor\(price \* \(1 - discountRate\)\);
