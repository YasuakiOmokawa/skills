---
type: regex
target: {source: file, path: repo/plans/tags.md}
match: not_contains
flags: ms
---
^- R-\d+:[^\n]*空の一覧.*^- R-\d+:[^\n]*空の一覧
