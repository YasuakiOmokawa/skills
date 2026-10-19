---
type: regex
target: {source: file, path: db/queries.sql}
match: contains
flags: s
---
(?=.*LIKE '%,1002,%')(?=.*ref_no LIKE 'Q-%')(?=.*ref_no LIKE 'O-%')(?=.*GROUP BY order_id)
