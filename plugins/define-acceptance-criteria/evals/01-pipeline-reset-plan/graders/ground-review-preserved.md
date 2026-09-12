---
type: regex
target: {source: file, path: plans/reset.md}
match: contains
flags: m
---
^- R1: `src/reset/consume\.ts` は利用済みトークンを削除せずフラグで管理する。
