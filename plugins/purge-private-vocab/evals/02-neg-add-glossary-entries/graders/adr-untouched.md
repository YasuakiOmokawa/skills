---
type: regex
target: {source: file, path: docs/adr/0003-manual-review.md}
match: contains
flags: s
---
(?=.*審査に失敗した請求書は青箱ルートへ送り、手確が済むまで仕訳を作らない。)(?=.*手確の担当者が増えても、保留箱の使い方は変わらない。)(?=.*赤橋が止まる)
