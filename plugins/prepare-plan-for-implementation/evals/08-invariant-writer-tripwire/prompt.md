---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p plans docs src/user src/membership src/invitation src/team src/session
cat > plans/team-current.md <<'EOF'
# current team を所属の増減に追従させる 設計

## 1. 背景
招待受諾で参加した user の `currentTeamId` が null のまま残り、除名された user の
`currentTeamId` は所属していないチームを指したまま残る。どちらも consumer が誤って扱う。

## 2. 仕様
- 仕様 source: `docs/session-contract.md`
- S-1: 招待を受諾すると、参加したチームがその user の current team になる。
- S-2: current team から除名されると、残る所属のどれか、所属 0 件なら null が current team になる。
- S-3: `verifySession` の `teamId` は常に所属しているチームのどれか、所属 0 件なら null。

## 3. 変更対象
| ファイル | 変更 |
|---|---|
| src/invitation/accept.ts | 受諾時に `setCurrentTeam` を呼ぶ |
| src/membership/remove.ts | 除名後に current team を付け替える |
| src/membership/repo.ts | user の残る所属を返す `listTeams` を足す |

## 4. 実装タスク
- T-1: `src/membership/repo.ts` に `listTeams(userId)` を足す。
- T-2: `src/invitation/accept.ts` の `acceptInvitation` で、`insertMembership` の後に `setCurrentTeam(userId, teamId)` を呼ぶ。
- T-3: `src/membership/remove.ts` の `removeMember` で、除名したチームが current team なら `listTeams` の先頭か null へ付け替える。

## Acceptance Criteria
- [ ] AC-001: 有効な招待を受諾すると、`verifySession` の `teamId` が招待先のチーム ID になる。
- [ ] AC-002: current team から除名された user は、`verifySession` の `teamId` が残る所属のどれか、所属 0 件なら null になる。
- [ ] AC-003: `createTeam`・`acceptInvitation`・`switchTeam`・`removeMember` のそれぞれの後で、`verifySession` の `teamId` はその user が所属するチームのどれか、所属 0 件なら null である。

## MECE Review
- AC IDs: AC-001, AC-002, AC-003
- Gate: ready

### 対応
- S-1 → T-2 / AC-001、S-2 → T-1, T-3 / AC-002、S-3 → AC-003。
- `setCurrentTeam` の呼び手は `src/team/create.ts`、`src/team/switch.ts`、`src/invitation/accept.ts` (T-2 後)、`src/membership/remove.ts` (T-3 後)。
- 所属を増減する呼び手は `insertMembership` が `src/team/create.ts` と `src/invitation/accept.ts`、`deleteMembership` が `src/membership/remove.ts`。
EOF
cat > docs/session-contract.md <<'EOF'
# セッション契約

`verifySession` は consumer に `{ userId, teamId }` を返す。

- `teamId` は、その user が所属しているチームのどれか。所属が 0 件なら `null`。
- consumer は `teamId` を「所属しているチーム」か「未選択 (null)」の 2 通りだけで扱う。
  所属していないチームの ID が返ると、consumer はそのチームのデータを読もうとして 403 になる。
EOF
cat > src/user/repo.ts <<'EOF'
export type User = { id: string; currentTeamId: string | null };

const users = new Map<string, User>();

export async function getUser(userId: string): Promise<User> {
  const user = users.get(userId);
  if (!user) throw new Error(`user not found: ${userId}`);
  return user;
}

export async function setCurrentTeam(
  userId: string,
  teamId: string | null,
): Promise<void> {
  const user = await getUser(userId);
  users.set(userId, { ...user, currentTeamId: teamId });
}
EOF
cat > src/membership/repo.ts <<'EOF'
type Membership = { userId: string; teamId: string };

const rows: Membership[] = [];

export async function insertMembership(userId: string, teamId: string): Promise<void> {
  rows.push({ userId, teamId });
}

export async function deleteMembership(userId: string, teamId: string): Promise<void> {
  const i = rows.findIndex((r) => r.userId === userId && r.teamId === teamId);
  if (i >= 0) rows.splice(i, 1);
}

export async function isMember(userId: string, teamId: string): Promise<boolean> {
  return rows.some((r) => r.userId === userId && r.teamId === teamId);
}
EOF
cat > src/invitation/accept.ts <<'EOF'
import { insertMembership } from "../membership/repo";

export type Invitation = { teamId: string; expiresAt: number };

export type AcceptResult = { ok: true } | { ok: false; reason: "expired" };

export async function acceptInvitation(
  userId: string,
  invitation: Invitation,
  now: number,
): Promise<AcceptResult> {
  if (invitation.expiresAt <= now) {
    return { ok: false, reason: "expired" };
  }
  await insertMembership(userId, invitation.teamId);
  return { ok: true };
}
EOF
cat > src/team/create.ts <<'EOF'
import { insertMembership } from "../membership/repo";
import { setCurrentTeam } from "../user/repo";

export async function createTeam(userId: string, teamId: string): Promise<void> {
  await insertMembership(userId, teamId);
  await setCurrentTeam(userId, teamId);
}
EOF
cat > src/team/switch.ts <<'EOF'
import { isMember } from "../membership/repo";
import { setCurrentTeam } from "../user/repo";

export type SwitchResult = { ok: true } | { ok: false; reason: "not-member" };

export async function switchTeam(userId: string, teamId: string): Promise<SwitchResult> {
  if (!(await isMember(userId, teamId))) {
    return { ok: false, reason: "not-member" };
  }
  await setCurrentTeam(userId, teamId);
  return { ok: true };
}
EOF
cat > src/membership/remove.ts <<'EOF'
import { deleteMembership } from "./repo";

export async function removeMember(
  actorId: string,
  userId: string,
  teamId: string,
): Promise<void> {
  if (actorId === userId) throw new Error("cannot remove yourself");
  await deleteMembership(userId, teamId);
}
EOF
cat > src/session/verify.ts <<'EOF'
import { getUser } from "../user/repo";

export type SessionView = { userId: string; teamId: string | null };

export async function verifySession(userId: string): Promise<SessionView> {
  const user = await getUser(userId);
  return { userId: user.id, teamId: user.currentTeamId };
}
EOF
```

plans/team-current.md 設計を /prepare-plan-for-implementation して、結果を設計書に反映して、設計を確定する。実装は指示まで禁止。
