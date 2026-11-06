---
type: regex
target: {source: file, path: repo/plans/secret-rotation.md}
match: not_contains
flags: m
---
^- (?:\[[ xX]\] )?AC-\d+:.*\((?:出典|根拠): [^)]*\bD\d+\b
