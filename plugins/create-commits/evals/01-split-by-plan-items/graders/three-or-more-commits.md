---
type: regex
target: {source: file, path: repo.gitdir/logs/HEAD}
---
(?:\tcommit: [\s\S]*?){3}
