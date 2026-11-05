---
type: regex
target: {source: file, path: repo/plans/rename.md}
match: contains
flags: m
weight: 0.5
---
git grep[^\n`]*(?:--untracked|--no-index[^\n`]*--exclude-standard|--exclude-standard[^\n`]*--no-index)|^- Forbidden row: \{"pattern"
