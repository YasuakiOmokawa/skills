---
type: regex
target: trace
match: contains
flags: s
---
seal: [0-9a-f]{40}.*?"type":"text","text":"(?:[^"\\]|\\.)*?R-1\b(?:[^"\\]|\\.)*?「(?:[^"\\]|\\.)*?".*?"type":"tool_use"
