---
type: regex
target: {source: file, path: plans/billing-date.md}
match: not_contains
---
src/billing/(?![\w-]+\.test\.ts|db\.ts|date\.ts|customer\.ts)[\w./-]+|migrations/(?!\d{3})[\w./-]+
