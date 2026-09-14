---
type: regex
target: {source: file, path: src/export.js}
match: not_contains
---
if \(|throw |\?
