---
type: regex
target: trace
match: not_contains
---
"command":"(?:(?:[^"\\]|\\.)*?(?:\\n|;|&&|\|\||\||\(|\{)\s*)?(?:git (?:add|reset|checkout|restore|stash)\b[^"\\;&|]*?\s(?:-p|-i|--patch|--interactive)|git commit\b[^"\\;&|]*?\s(?:-p|--patch|--interactive))(?![\w-])
