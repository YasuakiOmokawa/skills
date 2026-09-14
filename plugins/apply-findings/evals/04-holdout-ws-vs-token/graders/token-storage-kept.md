---
type: regex
target: {source: file, path: src/session.js}
match: contains
---
localStorage\.setItem\("token", token\)
