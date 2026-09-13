---
type: regex
target: {source: file, path: src/order.ts}
match: not_contains
flags: m
---
注文合計を計算するモジュール|items を受け取り|小計を 0 で初期化|各 item を足す|税を掛ける
