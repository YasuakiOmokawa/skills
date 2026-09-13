---
type: regex
target: {source: file, path: src/backoff.ts}
match: not_contains
flags: m
---
function calc\(|function s\(|\bv\b|\bc\b
