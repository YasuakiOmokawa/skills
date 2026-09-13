---
type: regex
target: {source: file, path: src/pricing.ts}
match: not_contains
flags: m
---
\bv\b|\bp\b
