---
type: regex
target: {source: file, path: src/sign-in-observer.ts}
match: not_contains
flags: m
---
route\.path === ["']/callback/:id["']|区別できない
