---
type: llm
focus: {source: file, path: src/session.ts}
---
src/session.ts を評価する。createSession が `base64url(JSON) + "." + HMAC-SHA256 hex` を返し、readSession が (1) 区切りが無い・署名不一致・JSON 不正・userId 空なら null、(2) issuedAt が now + 300 秒を超える未来なら null、(3) now が issuedAt + 21600 秒 と等しいときは有効 (Session を返す)、(4) それより後なら null、を維持していれば pass。境界、TTL、時計ずれ幅、署名方式のどれかが変わっていれば fail。
