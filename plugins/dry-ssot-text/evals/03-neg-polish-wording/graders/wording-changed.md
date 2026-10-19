---
type: regex
target: {source: file, path: README.md}
match: not_contains
---
^(?=[\s\S]*ということができる)(?=[\s\S]*するところの)(?=[\s\S]*こととなっている)
