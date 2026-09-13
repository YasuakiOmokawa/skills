---
type: regex
target: {source: file, path: src/pricing.ts}
match: not_contains
flags: m
---
export function roundDown|export \{[^}]*roundDown|export const roundDown
