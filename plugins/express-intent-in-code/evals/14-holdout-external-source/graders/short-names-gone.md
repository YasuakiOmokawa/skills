---
type: regex
target: {source: file, path: src/rate-limit.ts}
match: not_contains
flags: m
---
function ok\(|const L =|const W =|const n =
