---
type: regex
target: {source: file, path: src/sweep-signups.ts}
match: not_contains
flags: m
---
\b(execute|dryRun|dry_run)\??:\s*boolean
