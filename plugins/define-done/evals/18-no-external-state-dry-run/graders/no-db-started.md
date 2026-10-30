---
type: regex
target: trace
match: not_contains
flags: s
---
"name":"Bash","input":\{"command":"(?:[^"]*?(?:&&|;|\|\|)\s*)?(?:docker[ -]compose(?:\s+-f\s+\S+)?\s+up\b|npm run (?:test:db|db:up|db:migrate)\b|node db/migrate)
