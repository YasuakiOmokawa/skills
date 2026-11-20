---
type: regex
target: {source: file, path: repo/plans/discount.md}
match: contains
flags: m
---
^- R-\d+:[^\n]*「[^」\n]*15[^」\n]*」[^\n]*依頼\)
