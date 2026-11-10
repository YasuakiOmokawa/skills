---
type: regex
target: {source: file, path: repo/src/company-state.ts}
match: not_contains
flags: m
---
loading:\s*boolean|unauthorized:\s*boolean|loadFailed:\s*boolean
