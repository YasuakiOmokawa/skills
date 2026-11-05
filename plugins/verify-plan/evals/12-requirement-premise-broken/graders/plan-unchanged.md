---
type: regex
target: {source: file, path: plans/rotate.md}
match: contains
---
- \[ \] AC-002: \[振る舞い\] `API_KEY` を `k2` に回してから、同じ source で `release` を流し直すと、公開された secret が `k2` になる \(出典: R-3\)
