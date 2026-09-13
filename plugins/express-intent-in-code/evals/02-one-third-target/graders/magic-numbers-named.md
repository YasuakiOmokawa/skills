---
type: regex
target: {source: file, path: src/session.ts}
match: not_contains
flags: m
---
\b21600\b|= 300\b
