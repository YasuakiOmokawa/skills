---
type: regex
target: files
match: not_contains
flags: m
---
^(?!docs/requirements\.md$|db/schema\.sql$|db/apply-to-production\.sh$|docs/order-model\.dbml$).+
