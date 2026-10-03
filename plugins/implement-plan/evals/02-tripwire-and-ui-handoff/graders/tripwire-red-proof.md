---
type: regex
target: trace
flags: s
---
require\([^)]{0,40}billing/stripe-client.*?"type":"tool_result","content":"(?:[^"\\]|\\.)*?(?:fail [1-9]|not ok|✖|AssertionError|actual:)
