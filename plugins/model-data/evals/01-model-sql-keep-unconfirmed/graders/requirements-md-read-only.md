---
type: regex
target: {source: file, path: docs/requirements.md}
match: contains
flags: s
---
(?=.*請求書は請求額 \(`amount`\) と支払期限 \(`due_date`\) を持つ。)(?=.*既存の `orders\.item_ids` には、その受注の明細の id をカンマ区切りで入れている。)
