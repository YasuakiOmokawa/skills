---
type: regex
target: {source: file, path: pr-body.md}
match: contains
flags: s
---
<!-- check-pr:start -->.*<!-- check-pr:end -->
