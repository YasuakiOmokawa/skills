---
type: regex
target: {source: file, path: src/order-id.test.ts}
match: not_contains
flags: m
---
\d{16,}|2\s*\*\*\s*53|MAX_SAFE_INTEGER|9007199254740
