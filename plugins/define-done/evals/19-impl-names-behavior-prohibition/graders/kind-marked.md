---
type: regex
target: {source: file, path: repo/plans/rate-limit.md}
match: not_contains
flags: m
weight: 0.5
---
^- (?:\[ \] )?AC-\d{3}: (?!\[(?:規則|非影響)\] )
