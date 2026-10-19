---
type: regex
target: {source: file, path: docs/adr/0003-manual-review.md}
match: not_contains
---
(?<![（(])(青箱ルート|手確)
