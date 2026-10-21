---
type: regex
target: {source: file, path: plans/billing-v2.md}
match: contains
weight: 0.5
---
- Gate: (?![`*]*ready\b)\S
