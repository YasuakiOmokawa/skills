---
type: regex
target: {source: file, path: billing/retry/design-doc.md}
match: contains
---
pull/41[\s\S]*pull/42|pull/42[\s\S]*pull/41
