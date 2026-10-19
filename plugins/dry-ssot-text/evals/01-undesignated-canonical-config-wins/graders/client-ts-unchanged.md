---
type: regex
target: {source: file, path: src/db/client.ts}
match: contains
---
new pg\.Pool\(\)
