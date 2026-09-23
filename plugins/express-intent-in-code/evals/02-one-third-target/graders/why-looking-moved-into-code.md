---
type: regex
target: {source: file, path: src/session.ts}
match: not_contains
flags: m
---
Date\.now|開発専用|fail-closed|JSON\.parse は|userId が空|未来の issuedAt|署名は body だけ|HMAC-SHA256 の hex|時計ずれを 5 分|有効期限は 6 時間
