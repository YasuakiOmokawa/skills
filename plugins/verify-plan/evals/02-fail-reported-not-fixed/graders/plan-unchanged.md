---
type: regex
target: {source: file, path: plans/lockout.md}
match: contains
---
- \[ \] AC-002: \[振る舞い\] `recordFailure\("u"\)` を 5 回呼んだ後、`isLocked\("u"\)` は true を返す。 \(出典: R-1, R-2\)
