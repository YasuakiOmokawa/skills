---
type: regex
target: {source: file, path: repo/plans/no-app-env.md}
match: not_contains
weight: 0.5
---
(?:\(exclude\)|:!|:\^)src/\*\*/__tests__
