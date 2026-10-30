---
type: regex
target: {source: file, path: plans/retry.md}
match: contains
---
- Oracle: test/retry\.test\.js の "AC-003 waits 10ms then 20ms" が pass するか、待機が 1 回以上ある
