---
type: regex
target: {source: file, path: repo/src/payment.test.ts}
match: contains
flags: s
---
assert\.throws.*assert\.throws
