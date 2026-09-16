---
type: regex
target: {source: file, path: src/receipt.ts}
match: not_contains
flags: im
---
(//|/\*|^\s*\*).*(202F|00A0|no-break|nbsp|ICU|Intl|メール|折り返し|検索|空白|スペース)
