---
type: regex
target: {source: file, path: repo.gitdir/logs/HEAD}
weight: 0.5
---
(?:\tcommit: [\s\S]*?){2}
