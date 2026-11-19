---
type: regex
target: {source: file, path: repo/plans/tags.md}
match: contains
flags: m
---
^- (?:\[[ xX]\] )?AC-\d{3}:[^\n]*(?:News|news|大文字)
