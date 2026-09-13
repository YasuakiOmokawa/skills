---
type: regex
target: {source: file, path: src/backoff.test.ts}
match: not_contains
flags: m
---
import \{[^}]*\b(calc|s)\b[^}]*\}
