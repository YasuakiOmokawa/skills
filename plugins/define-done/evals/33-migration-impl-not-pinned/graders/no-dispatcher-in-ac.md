---
type: regex
target: {source: file, path: repo/plans/invite.md}
match: not_contains
flags: m
---
^- (?:\[ \] )?AC-\d{3}:[^\n]*(?:runtimeForPath|runtime-for-path|MODERN_PATHS)
