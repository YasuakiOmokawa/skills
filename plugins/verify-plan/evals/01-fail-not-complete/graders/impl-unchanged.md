---
type: regex
target: {source: file, path: repo/src/price.js}
match: contains
---
amount > 5000 \? 0 : 500
