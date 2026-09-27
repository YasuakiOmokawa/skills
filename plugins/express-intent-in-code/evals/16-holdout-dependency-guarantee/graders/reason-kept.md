---
type: regex
target: {source: file, path: src/order-id.ts}
match: contains
flags: m
---
^\s*//.*(19 桁|2\^53|丸ま)
