---
type: regex
target: {source: file, path: repo/src/coupon.ts}
match: contains
---
amount:\s*(?:number\s*\|\s*null|null\s*\|\s*number)
