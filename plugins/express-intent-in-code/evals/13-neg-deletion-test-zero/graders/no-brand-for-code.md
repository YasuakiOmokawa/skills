---
type: regex
target: {source: file, path: src/totp.ts}
match: not_contains
flags: im
---
unique symbol|&\s*\{\s*readonly|brand
