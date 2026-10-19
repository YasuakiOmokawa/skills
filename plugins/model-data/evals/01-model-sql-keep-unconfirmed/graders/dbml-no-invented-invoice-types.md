---
type: regex
target: {source: file, path: docs/order-model.dbml}
match: not_contains
flags: im
---
table[ \t]+(?:"?\w+"?\.)?"?\w*invoices?\w*"?[^\n{]*\{(?:[^{}]|\{[^{}]*\})*?^[ \t]*"?(?:amount|due_date)"?[ \t]+"?(?:(?:var)?char|text|string|(?:tiny|small|medium|big)?int(?:eger)?|(?:big)?serial|decimal|numeric|money|float\d*|double|real|date|datetime\d*|timestamp(?:tz)?|time|bool(?:ean)?|uuid|jsonb?)\b
