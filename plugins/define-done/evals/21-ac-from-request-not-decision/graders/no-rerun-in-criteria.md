---
type: regex
target: {source: file, path: repo/plans/secret-rotation.md}
match: not_contains
flags: m
---
^- (?:\[ \] )?AC-\d{3}:[^\n]*(?:[Rr]e-?run|[Rr]erun|再実行|流し直|走らせ直)
