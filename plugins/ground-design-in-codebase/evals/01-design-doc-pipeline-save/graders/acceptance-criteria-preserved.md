---
type: regex
target: {source: file, path: design.md}
match: count:1
flags: m
---
^- AC-2: 有効な token で GET /api/export が 200 と CSV を返す。$
