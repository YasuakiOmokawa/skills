---
type: regex
target: {source: file, path: repo/lint.config.json}
match: contains
flags: s
---
\{[^{}]*"files":\s*"(?:\./)?src/domain/?"[^{}]*"forbidden":\s*"(?:\./)?src/infra/?"[^{}]*\}|\{[^{}]*"forbidden":\s*"(?:\./)?src/infra/?"[^{}]*"files":\s*"(?:\./)?src/domain/?"[^{}]*\}
