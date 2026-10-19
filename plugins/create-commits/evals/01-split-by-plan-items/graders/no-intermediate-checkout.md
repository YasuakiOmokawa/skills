---
type: regex
target: {source: file, path: repo.gitdir/logs/HEAD}
match: not_contains
flags: m
weight: 0.5
---
\tcheckout: moving from feature/mfa-rollout to (?:HEAD\S*|[0-9a-f]{7,40}|\S+[~^]\d*)$
