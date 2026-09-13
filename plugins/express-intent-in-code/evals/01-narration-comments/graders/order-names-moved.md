---
type: regex
target: {source: file, path: src/order.ts}
match: not_contains
flags: m
---
\btmp\b|\bx\b|\bs\b
