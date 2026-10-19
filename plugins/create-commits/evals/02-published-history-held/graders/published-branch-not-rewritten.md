---
type: regex
target: {source: file, path: repo.gitdir/logs/refs/heads/feature/order-retry}
match: not_contains
flags: m
---
^(?!.*\t(?:branch: Created from HEAD|commit: )).+$
