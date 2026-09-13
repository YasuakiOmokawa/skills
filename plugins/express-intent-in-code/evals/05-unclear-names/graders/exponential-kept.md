---
type: regex
target: {source: file, path: src/backoff.ts}
match: contains
flags: m
---
2 \*\* |Math\.pow\(2|<< 
