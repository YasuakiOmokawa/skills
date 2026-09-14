---
type: regex
target: {source: file, path: src/handler.js}
match: contains
---
const \{ unusedHelper \} = require\("\./helpers"\);
