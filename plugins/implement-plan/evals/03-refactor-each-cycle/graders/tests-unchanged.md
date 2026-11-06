---
type: regex
target: {source: file, path: repo/test/shipping.acceptance.test.js}
match: contains
---
assert\.equal\(shippingFee\('okinawa', 5000\), 0\)
