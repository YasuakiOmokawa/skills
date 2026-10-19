---
type: regex
target: trace
match: contains
flags: s
weight: 0.5
---
(?:"name":"(?:Write|Edit)","input":\{[^{}]*?"file_path":"[^"]*artifacts/figma-check\.md".*(?:"name":"(?:Read|Grep)","input":\{[^{}]*?figma-check\.md|"name":"Bash","input":\{[^{}]*?\b(?:cat|grep|head|tail|sed|wc|awk)\b[^{}]*?figma-check\.md))|(?:"name":"Bash","input":\{"command":"(?:[^"\\]|\\.)*?>\s*(?:\./)?artifacts/figma-check\.md(?:[^"\\]|\\.)*?(?:\\n|[\s;&|(])(?:cat|grep|head|tail|sed|wc|awk)\b(?:[^"\\]|\\.)*?figma-check\.md)
