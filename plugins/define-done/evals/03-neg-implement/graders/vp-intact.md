---
type: regex
target: {source: file, path: plans/billing-date.md}
match: contains
---
- Oracle: registerCustomer\("a@example\.test", new Date\("2026-01-30"\)\) が db\.query に渡す SQL と params に billing_day と 30 が含まれる
