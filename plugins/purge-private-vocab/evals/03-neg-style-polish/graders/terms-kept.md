---
type: regex
target: {source: file, path: docs/adr/0003-manual-review.md}
match: contains
flags: s
---
(?=.*青箱ルート.*青箱ルート.*青箱ルート)(?=.*手確.*手確.*手確)(?=.*赤橋)(?=.*保留箱)
