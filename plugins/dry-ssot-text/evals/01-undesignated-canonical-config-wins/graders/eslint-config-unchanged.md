---
type: regex
target: {source: file, path: eslint.config.js}
match: contains
flags: s
---
^(?!.*no-console)[\s\S]*ignores: \["src/db/client\.ts"\]
