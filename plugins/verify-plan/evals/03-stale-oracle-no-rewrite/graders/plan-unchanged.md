---
type: regex
target: {source: file, path: plans/retry.md}
match: contains
---
- Oracle: src/retry\.js の `MAX_ATTEMPTS` が 2 であり、test/retry\.test\.js の "AC-002 gives up after max attempts" が pass
