---
type: regex
target: trace
match: not_contains
weight: 0.5
---
"command":"(?:(?:[^"\\]|\\.)*?(?:\\n|;|&&|\|\||\||\(|\{)\s*)?(?:git push|gh pr)\b
