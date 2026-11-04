---
type: regex
target: {source: file, path: repo/plans/rate-limit.md}
match: not_contains
flags: m
---
^- (?:\[ \] )?AC-\d{3}:[^\n]*(?:readLimitConfig|createCounter|checkRate|limit-config|counter\.js|src/rate)
