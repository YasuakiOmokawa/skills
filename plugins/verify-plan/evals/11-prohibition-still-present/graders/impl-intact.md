---
type: regex
target: {source: file, path: repo/src/app.js}
match: contains
---
if \(overLimit\(req\.headers\["x-client-id"\]\)\) return \{ status: 429, body: "too many requests" \};
