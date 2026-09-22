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
cat > src/removal-policy.ts <<'EOF'
export type Role = "OWNER" | "ADMIN" | "MEMBER";

const ROLE_LEVEL = { MEMBER: 0, ADMIN: 1, OWNER: 2 } as const;

export function isAtLeast(role: Role, minRole: Role): boolean {
  return ROLE_LEVEL[role] >= ROLE_LEVEL[minRole];
}

export function canAttemptRemoval(actorRole: Role, isSelf: boolean): boolean {
  return isSelf || isAtLeast(actorRole, "ADMIN");
}

export function canRemoveTarget(actorRole: Role, isSelf: boolean, targetRole: Role): boolean {
  return !(targetRole === "OWNER" && !isSelf && actorRole !== "OWNER");
}
EOF
cat > src/removal-guard.ts <<'EOF'
import { canAttemptRemoval, canRemoveTarget, type Role } from "./removal-policy.ts";

export type Member = { userId: string; role: Role };

export function guardRemoval(actor: Member, target: Member): "allowed" | "forbidden" {
  const isSelf = actor.userId === target.userId;
  if (!canAttemptRemoval(actor.role, isSelf)) return "forbidden";
  if (!canRemoveTarget(actor.role, isSelf, target.role)) return "forbidden";
  return "allowed";
}
EOF
cat > src/sweep-signups.ts <<'EOF'
export type Signup = { id: string; createdAtMs: number; verified: boolean };

export type Store = {
  listSignups(): Signup[];
  deleteSignups(ids: string[]): number;
};

export function sweepSignups(store: Store, opts: { olderThanMs: number; nowMs: number; execute: boolean }) {
  const candidates = store
    .listSignups()
    .filter((s) => !s.verified && opts.nowMs - s.createdAtMs > opts.olderThanMs)
    .map((s) => s.id);
  if (!opts.execute) return { executed: false, candidates, deleted: 0 };
  const deleted = store.deleteSignups(candidates);
  return { executed: true, candidates, deleted };
}
EOF
cat > src/removal.test.ts <<'EOF'
import { test } from "node:test";
import assert from "node:assert/strict";
import { guardRemoval } from "./removal-guard.ts";
import { sweepSignups, type Signup } from "./sweep-signups.ts";

test("member can remove self", () => {
  assert.equal(guardRemoval({ userId: "a", role: "MEMBER" }, { userId: "a", role: "MEMBER" }), "allowed");
});
test("member cannot remove others", () => {
  assert.equal(guardRemoval({ userId: "a", role: "MEMBER" }, { userId: "b", role: "MEMBER" }), "forbidden");
});
test("admin cannot remove owner", () => {
  assert.equal(guardRemoval({ userId: "a", role: "ADMIN" }, { userId: "b", role: "OWNER" }), "forbidden");
});
test("owner can remove owner", () => {
  assert.equal(guardRemoval({ userId: "a", role: "OWNER" }, { userId: "b", role: "OWNER" }), "allowed");
});

const signups: Signup[] = [
  { id: "old-unverified", createdAtMs: 0, verified: false },
  { id: "old-verified", createdAtMs: 0, verified: true },
  { id: "new-unverified", createdAtMs: 900, verified: false },
];
const store = (deleted: string[][]) => ({
  listSignups: () => signups,
  deleteSignups: (ids: string[]) => { deleted.push(ids); return ids.length; },
});

test("dry run lists candidates without deleting", () => {
  const deleted: string[][] = [];
  const out = sweepSignups(store(deleted), { olderThanMs: 500, nowMs: 1000, execute: false });
  assert.deepEqual(out.candidates, ["old-unverified"]);
  assert.deepEqual(deleted, []);
});
test("execute deletes candidates", () => {
  const deleted: string[][] = [];
  const out = sweepSignups(store(deleted), { olderThanMs: 500, nowMs: 1000, execute: true });
  assert.equal(out.deleted, 1);
  assert.deepEqual(deleted, [["old-unverified"]]);
});
EOF
```

`node --test` が 6 件すべて成功することを確認してから、次の依頼に取りかかってください。

src/removal-policy.ts と src/sweep-signups.ts の意図をコードで表して。呼び出し側の src/removal-guard.ts も直してよい。テストは合わせて直してよいが、判定結果と削除される対象は変えないで。
