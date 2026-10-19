---
type: regex
target: {source: file, path: docs/order-model.dbml}
match: contains
flags: im
weight: 0.5
---
(?=[\s\S]*^(?![ \t]*//)[^\n]*\bcustomer_id\b[^\n]*\bnot null\b)(?=[\s\S]*^(?![ \t]*//)[^\n]*\border_id\b[^\n]*\bnot null\b)
