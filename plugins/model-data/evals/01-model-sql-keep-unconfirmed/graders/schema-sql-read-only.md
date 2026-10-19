---
type: regex
target: {source: file, path: db/schema.sql}
match: contains
flags: s
---
^(?!.*FOREIGN KEY)(?!.*REFERENCES orders)(?=.*item_ids TEXT NOT NULL)(?=.*order_id BIGINT NOT NULL,)(?=.*ref_no VARCHAR\(20\) NOT NULL)
