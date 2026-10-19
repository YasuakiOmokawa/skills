---
type: regex
target: {source: file, path: plans/design/2026-10-01-manual-review/design-doc.md}
match: contains
flags: s
---
\| 青箱ルート \| 審査失敗時に手動確認へ送る経路 \|.*\| 手確 \| 担当者による手動確認 \|.*\| 保留箱 \| 判断のつかない請求書を置く一覧 \|.*\| T-16 \|.*赤橋が止まる
