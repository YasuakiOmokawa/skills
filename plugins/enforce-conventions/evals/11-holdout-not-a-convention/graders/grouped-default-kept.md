---
type: regex
target: {source: file, path: repo/src/ticket.ts}
match: contains
---
if \(status === "open"\) return "green";\s*return "gray";
