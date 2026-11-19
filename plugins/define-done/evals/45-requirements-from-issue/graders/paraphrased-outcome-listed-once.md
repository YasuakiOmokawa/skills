---
type: regex
target: {source: file, path: repo/plans/tags.md}
match: not_contains
flags: m
---
^- R-\d+:(?![^\n]*1 回だけ)[^\n]*重複なく
