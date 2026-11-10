---
type: regex
target: {source: file, path: repo/lint.config.json}
match: contains
flags: s
---
\{[^{}]*"files":\s*"src/web"[^{}]*"forbidden":\s*"src/db"[^{}]*\}
