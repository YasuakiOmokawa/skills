---
type: regex
target: {source: file, path: docs/order-model.dbml}
match: contains
flags: i
---
(?=[\s\S]*\btable[ \t]+(?:\w+\.)?"?customers"?\b)(?=[\s\S]*\btable[ \t]+(?:\w+\.)?"?orders"?\b)(?=[\s\S]*\btable[ \t]+(?:\w+\.)?"?order_items"?\b)(?=[\s\S]*\btable[ \t]+(?:\w+\.)?"?\w*invoices?\w*"?[ \t\n\[{])
