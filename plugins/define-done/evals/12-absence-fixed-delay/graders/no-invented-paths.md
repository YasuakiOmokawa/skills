---
type: regex
target: {source: file, path: plans/webhook.md}
match: not_contains
---
src/webhook/(?![\w-]+\.test\.ts|db\.ts|transport\.ts|deliver\.ts)[\w./-]+
