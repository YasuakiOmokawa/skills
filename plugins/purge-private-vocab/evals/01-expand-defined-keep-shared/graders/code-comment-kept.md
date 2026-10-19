---
type: regex
target: {source: file, path: src/review/router.ts}
match: contains
---
// 審査に失敗した請求書は青箱ルートへ送る。手確が済むまで仕訳は作らない。
