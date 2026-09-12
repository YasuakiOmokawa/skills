---
type: regex
target: {source: file, path: design.md}
match: contains
flags: m
---
^## Ground Review\n(?:(?!## )[^\n]*\n)*## Acceptance Criteria
