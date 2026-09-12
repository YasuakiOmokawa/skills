---
type: regex
target: {source: file, path: plans/reset.md}
match: contains
flags: m
---
^- \[ \] AC-005: 同じリンクを二回目に開くと、「このリンクは使用済みです」が表示され、パスワードは変更されない\s*$
