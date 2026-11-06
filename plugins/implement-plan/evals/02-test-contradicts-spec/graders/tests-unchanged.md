---
type: regex
target: {source: file, path: repo/test/price.acceptance.test.js}
match: contains
---
assert\.equal\(shippingFee\(5000\), 500\)
