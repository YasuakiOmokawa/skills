---
type: regex
target: trace
match: not_contains
---
git (?:-C \S+ )?(?:diff|format-patch)[^"\n]{0,200}?>\s*[^\s"\\]+\.patch
