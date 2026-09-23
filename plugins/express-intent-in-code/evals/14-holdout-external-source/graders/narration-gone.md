---
type: regex
target: {source: file, path: src/rate-limit.ts}
match: not_contains
flags: m
---
レート制限のモジュール|時間窓 \(ms\)|送信時刻の一覧|直近の時間窓に入る送信を数える|上限未満なら送ってよい
