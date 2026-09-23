---
type: regex
target: {source: file, path: src/rate-limit.ts}
match: count:1
flags: m
---
^\s*(//|/\*)
