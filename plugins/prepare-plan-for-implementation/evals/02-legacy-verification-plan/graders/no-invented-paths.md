---
type: regex
target: {source: file, path: plans/notify.md}
match: not_contains
---
src/notify/(?![\w-]+\.test\.ts|send\.ts|transport\.ts|log\.ts)[\w./-]+
