---
type: regex
target: {source: file, path: billing/retry/design-doc.md}
match: not_contains
---
pull/(?!4[12]\b)\d+
