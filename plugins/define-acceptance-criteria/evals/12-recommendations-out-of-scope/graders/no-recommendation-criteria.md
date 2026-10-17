---
type: regex
target: {source: file, path: plans/confirm-on-post.md}
match: not_contains
flags: m
---
^## Acceptance Criteria[ \t]*\n(?:(?!## )[^\n]*\n)*?(?!## )[^\n]*(?:監査|レート|保存境界|保存時|フェイルクローズ|SMS|他人)
