---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Skill, Read, Write, Edit, Bash]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p src
cat > package.json <<'EOF'
{ "name": "fixture", "private": true, "type": "module", "scripts": { "test": "node --test" } }
EOF
cat > src/session.ts <<'EOF'
// ============================================
// session.ts
// セッション cookie の発行と検証。
// createSession で cookie 文字列を作り、readSession で解析する。
// ============================================
import { createHmac, timingSafeEqual } from "node:crypto";

// 有効期限は 6 時間 (秒)
const TTL_SECONDS = 21600;
// クライアントの時計ずれを 5 分まで許容する (秒)
const SKEW_SECONDS = 300;
// dev-secret は開発専用。本番は SESSION_SECRET を必ず設定すること
const SECRET = process.env.SESSION_SECRET ?? "dev-secret";
// 区切り文字。base64url にも hex にも含まれない文字を選んでいる
const SEP = ".";

// issuedAt は秒 (Date.now() のミリ秒ではない)
export type Session = { userId: string; issuedAt: number };

// payload を base64url にして署名を付ける
export function createSession(s: Session): string {
  const body = Buffer.from(JSON.stringify(s)).toString("base64url");
  // 署名は body だけを対象にする (payload の改変検知のため)
  return body + SEP + sign(body);
}

// now は秒 (Date.now() ではない)
// 不正な cookie は例外にせず null を返す (fail-closed)
export function readSession(cookie: string, now: number): Session | null {
  const [body, sig] = cookie.split(SEP);
  if (!body || !sig) return null;
  // timingSafeEqual は長さが違うと throw するので先に長さを見る
  const expected = sign(body);
  if (expected.length !== sig.length) return null;
  // === だとタイミング攻撃で署名を推測されるので timingSafeEqual を使う
  if (!timingSafeEqual(Buffer.from(expected), Buffer.from(sig))) return null;
  let s: Session;
  // JSON.parse は不正な body で throw するので catch して null にする
  try {
    s = JSON.parse(Buffer.from(body, "base64url").toString()) as Session;
  } catch {
    return null;
  }
  // userId が空なら不正扱い
  if (!s.userId) return null;
  // 未来の issuedAt は時計ずれの範囲までは許す
  if (s.issuedAt > now + SKEW_SECONDS) return null;
  // 期限は issuedAt + TTL。now === 期限 は有効扱い (RFC 6265 の Max-Age と揃える)
  if (now > s.issuedAt + TTL_SECONDS) return null;
  return s;
}

// HMAC-SHA256 の hex。secret は SESSION_SECRET
function sign(body: string): string {
  return createHmac("sha256", SECRET).update(body).digest("hex");
}
EOF
cat > src/session.test.ts <<'EOF'
import { test } from "node:test";
import assert from "node:assert/strict";
import { createSession, readSession } from "./session.ts";

const s = { userId: "u1", issuedAt: 1000 };
const TTL = 6 * 60 * 60;
const SKEW = 5 * 60;

test("roundtrip", () => {
  assert.deepEqual(readSession(createSession(s), 1000), s);
});
test("tampered signature", () => {
  const c = createSession(s);
  const flipped = c.slice(0, -1) + (c.endsWith("a") ? "b" : "a");
  assert.equal(readSession(flipped, 1000), null);
});
test("malformed cookie", () => {
  assert.equal(readSession("nodot", 1000), null);
});
test("empty userId is rejected", () => {
  assert.equal(readSession(createSession({ userId: "", issuedAt: 1000 }), 1000), null);
});
test("issuedAt in the future within skew", () => {
  assert.deepEqual(readSession(createSession(s), 1000 - SKEW), s);
});
test("issuedAt in the future beyond skew", () => {
  assert.equal(readSession(createSession(s), 1000 - SKEW - 1), null);
});
test("valid exactly at expiry", () => {
  assert.deepEqual(readSession(createSession(s), 1000 + TTL), s);
});
test("expired one second after", () => {
  assert.equal(readSession(createSession(s), 1000 + TTL + 1), null);
});
EOF
```

`node --test` が 3 件以上すべて成功することを確認してから、次の依頼に取りかかってください。

個人的には今のコードコメントの量から、1/3 までコードコメントを削減したい。src/session.ts を対象に、振る舞いを変えずにやって。
