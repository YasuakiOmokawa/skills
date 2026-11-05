---
type: regex
target: {source: file, path: repo/plans/webhook.md}
match: not_contains
---
(?m)^(?!- Violation sample:)[^\n]*(?:src/webhook/(?![\w-]+\.test\.ts|db\.ts|transport\.ts|deliver\.ts)[\w./-]+)
