---
type: regex
target: {source: file, path: repo/plans/rename.md}
match: contains
---
git grep[^\n`]*(?:--untracked|--no-index[^\n`]*--exclude-standard|--exclude-standard[^\n`]*--no-index)
