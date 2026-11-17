---
type: regex
target: {source: file, path: repo/src/discount-rules.js}
match: contains
---
quantity >= 10 \? 10 : 0
