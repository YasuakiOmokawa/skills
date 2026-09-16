---
type: regex
target: {source: file, path: src/receipt.ts}
match: not_contains
flags: m
---
明細行$|置換対象の文字|明細の合計を返す|amount を全部足す|金額をユーロ表記に|メール本文用のテキストに|改行で繋ぐ|最後に合計行
