---
type: regex
target: {source: file, path: tsconfig.json}
match: contains
---
"exclude": \["src/\*\*/__tests__/\*\*"\]
