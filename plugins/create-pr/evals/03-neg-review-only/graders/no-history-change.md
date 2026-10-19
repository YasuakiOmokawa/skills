---
type: regex
target: {source: file, path: gitdir/repo/logs/HEAD}
match: not_contains
---
\t(?:commit(?! \(initial\))(?!: (?:feat|docs): )|reset|rebase|cherry-pick|merge|pull)
