---
type: regex
target: files
match: not_contains
flags: m
---
^(?!docs/requirements\.md$|db/(?:schema|queries)\.sql$|docs/order-model\.dbml$|docs/order-model-review\.md$).+
