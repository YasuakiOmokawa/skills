---
type: regex
target: {source: file, path: repo/plans/webhook.md}
match: not_contains
---
src/webhook/(?![\w-]+\.test\.ts|db\.ts|transport\.ts|deliver\.ts)[\w./-]+
