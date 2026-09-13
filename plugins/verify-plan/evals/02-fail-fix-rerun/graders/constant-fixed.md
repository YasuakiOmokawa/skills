---
type: regex
target: {source: file, path: src/lockout.js}
match: contains
---
MAX_ATTEMPTS\s*=\s*5\b
