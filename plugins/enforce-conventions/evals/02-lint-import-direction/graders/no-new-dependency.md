---
type: regex
target: {source: file, path: repo/package.json}
match: count:1
---
"[\w@/.-]+":\s*"\d+\.\d+\.\d+"
