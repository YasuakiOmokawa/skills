---
type: regex
target: {source: file, path: docs/order-model.dbml}
match: contains
flags: i
weight: 0.5
---
(?=[\s\S]*\bname[ \t]+"?varchar\(200\))(?=[\s\S]*\bsku[ \t]+"?varchar\(40\))
