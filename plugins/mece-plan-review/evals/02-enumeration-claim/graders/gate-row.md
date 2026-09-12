---
type: regex
target: {source: file, path: plans/mfa-policy.md}
match: contains
weight: 0.5
---
- Gate: (ready|blocked|unverified)
