---
type: regex
target: files
match: not_contains
flags: m
---
^(?!figma/button\.json$|src/Button\.css$|artifacts/figma-check\.md$).+
