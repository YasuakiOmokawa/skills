---
type: regex
target: {source: file, path: src/invitation-mail.ts}
match: not_contains
flags: m
---
(sanitizeDisplayText|toDisplayText|\w+DisplayText)\(\s*(sanitizeDisplayText|toDisplayText|\w+DisplayText)\(
