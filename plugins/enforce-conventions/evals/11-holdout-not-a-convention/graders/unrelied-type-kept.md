---
type: regex
target: {source: file, path: repo/src/ticket.ts}
match: contains
---
assignee:\s*(?:string\s*\|\s*null|null\s*\|\s*string)
