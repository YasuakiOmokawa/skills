---
type: regex
target: {source: file, path: repo/plans/discount.md}
match: contains
flags: m
---
^- (?:\[[ xX]\] )?AC-00[4-9]: \[規則\][^\n]*850
