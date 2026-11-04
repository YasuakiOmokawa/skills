---
type: regex
target: {source: file, path: repo/plans/rate-limit.md}
match: contains
flags: m
weight: 0.5
---
^- (?:\[ \] )?AC-\d{3}: \[(?:振る舞い|禁止)\]
