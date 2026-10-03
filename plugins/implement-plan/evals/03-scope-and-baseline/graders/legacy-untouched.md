---
type: regex
target: {source: file, path: src/legacy.js}
match: count:2
---
String\(d\.getUTCMonth\(\) \+ 1\)\.padStart\(2, "0"\)
