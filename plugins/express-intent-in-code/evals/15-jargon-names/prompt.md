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
cat > src/invitation.ts <<'EOF'
export type Member = { id: string; suspended: boolean };
export type Invitation = { inviterId: string; email: string; expiresAt: number };

export type InviterStanding = "good" | "suspended" | "gone";

// status と message を持つエラー
export class WireError extends Error {
  readonly status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

// 招待者の状態を返す
export function standingOf(inviter: Member | undefined): InviterStanding {
  if (!inviter) return "gone";
  if (inviter.suspended) return "suspended";
  return "good";
}

// 招待を受諾し、参加するメールアドレスを返す
export function acceptInvitation(inv: Invitation, members: Map<string, Member>, now: number): string {
  // 期限切れなら 410
  if (now >= inv.expiresAt) throw new WireError(410, "招待の有効期限が切れています");
  // 招待者が good でなければ 403
  if (standingOf(members.get(inv.inviterId)) !== "good") throw new WireError(403, "招待者が無効です");
  return inv.email;
}

// エラーをレスポンスにする
export function toWire(e: unknown): { status: number; body: string } {
  if (e instanceof WireError) return { status: e.status, body: e.message };
  return { status: 500, body: "internal error" };
}
EOF
cat > src/route.ts <<'EOF'
import { acceptInvitation, toWire, type Invitation, type Member } from "./invitation.ts";

export function handleAccept(inv: Invitation, members: Map<string, Member>, now: number): { status: number; body: string } {
  try {
    return { status: 200, body: acceptInvitation(inv, members, now) };
  } catch (e) {
    return toWire(e);
  }
}
EOF
cat > src/invitation.test.ts <<'EOF'
import { test } from "node:test";
import assert from "node:assert/strict";
import { acceptInvitation, standingOf, WireError, type Member } from "./invitation.ts";
import { handleAccept } from "./route.ts";

const members = new Map<string, Member>([
  ["m1", { id: "m1", suspended: false }],
  ["m2", { id: "m2", suspended: true }],
]);

test("standing of suspended and missing inviters", () => {
  assert.equal(standingOf(members.get("m2")), "suspended");
  assert.equal(standingOf(undefined), "gone");
});
test("an expired invitation is a 410 wire error", () => {
  assert.throws(
    () => acceptInvitation({ inviterId: "m1", email: "a@x", expiresAt: 10 }, members, 10),
    (e) => e instanceof WireError && e.status === 410,
  );
});
test("accepts an invitation from a member in good standing", () => {
  assert.deepEqual(handleAccept({ inviterId: "m1", email: "a@x", expiresAt: 100 }, members, 1), { status: 200, body: "a@x" });
});
test("route sends the wire error to the client", () => {
  assert.deepEqual(handleAccept({ inviterId: "m2", email: "a@x", expiresAt: 100 }, members, 1), { status: 403, body: "招待者が無効です" });
});
test("route hides unexpected errors", () => {
  const broken = { get() { throw new Error("db down"); } } as unknown as Map<string, Member>;
  assert.deepEqual(handleAccept({ inviterId: "m1", email: "a@x", expiresAt: 100 }, broken, 1), { status: 500, body: "internal error" });
});
EOF
```

`node --test` が 5 件すべて成功することを確認してから、次の依頼に取りかかってください。

招待受諾の実装が終わった。src/invitation.ts のコメントを整理して、意図はコードで表して。振る舞いは変えないで。
