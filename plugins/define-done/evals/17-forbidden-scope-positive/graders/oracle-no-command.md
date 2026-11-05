---
type: regex
target: {source: file, path: repo/plans/no-app-env.md}
match: not_contains
flags: m
---
^- Oracle:[^\n]*\b(?:git grep|grep|rg)\b
