---
type: regex
target: trace
match: not_contains
flags: s
weight: 0.5
---
"name":"(?:Write|Edit)","input":\{[^{}]*?"file_path":"[^"]*repo/(?!plans/no-app-env\.md")
