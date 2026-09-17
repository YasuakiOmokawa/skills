---
type: regex
target: {source: file, path: billing/retry/design-doc.md}
match: not_contains
---
保存期間.{0,30}\d+\s*(日|ヶ月|か月|年)
