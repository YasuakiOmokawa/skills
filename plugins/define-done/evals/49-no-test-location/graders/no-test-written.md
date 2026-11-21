---
type: regex
target: trace
match: not_contains
flags: s
---
"name":"(?:Write|Edit)","input":\{[^{}]*?"file_path":"[^"]*repo/(?!plans/reset\.md")
