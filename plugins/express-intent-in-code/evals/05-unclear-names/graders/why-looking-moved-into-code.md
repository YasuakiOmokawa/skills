---
type: regex
target: {source: file, path: src/backoff.ts}
match: not_contains
flags: m
---
何回目の試行|初回待ち時間|上限 ms|指数バックオフ|cap を超えない|ms を秒に|切り上げ
