---
type: regex
target: {source: file, path: repo/plans/tags.md}
match: contains
flags: m
---
^- R-\d+:[^\n]*重複
