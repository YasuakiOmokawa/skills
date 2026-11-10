---
type: regex
target: {source: file, path: repo/src/payment.ts}
match: contains
flags: s
---
throw new Error.*throw new Error
