---
type: regex
target: {source: file, path: pr-body.md}
match: contains
flags: m
---
^\|\s*C1\s*\|\s*NG\s*\|.*src/report\.js
