---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p plans docs src/user src/membership src/invitation src/team src/session
cat > plans/invite-accept.md <<'EOF'
# 招待受諾で current team を設定する 設計

## 1. 背景
招待を受諾して初めてチームに参加した user は `currentTeamId` が null のままで、
consumer がセッションを「チーム未選択」として扱ってしまう。

## 2. 仕様
- 仕様 source: `docs/session-contract.md`
- S-1: 招待を受諾すると、参加したチームがその user の current team になる。
- S-2: 期限切れの招待は受諾できず、current team は変わらない。

## 3. 変更対象
| ファイル | 変更 |
|---|---|
| src/invitation/accept.ts | 受諾時に `setCurrentTeam` を呼ぶ |
| src/session/verify.ts | 変更なし (current team をそのまま返すことの確認) |

## 4. 実装タスク
- T-1: `src/invitation/accept.ts` の `acceptInvitation` で、`insertMembership` の後に `setCurrentTeam(userId, teamId)` を呼ぶ。
- T-2: 期限切れ招待の拒否経路で `setCurrentTeam` を呼ばないことをテストで固定する。

## Acceptance Criteria
- [ ] AC-001: 有効な招待を受諾すると、user の `currentTeamId` が招待先のチーム ID になる。
- [ ] AC-002: 受諾後に `verifySession` を呼ぶと、`teamId` が招待先のチーム ID になる。
- [ ] AC-003: 期限切れの招待を受諾しようとすると `{ ok: false, reason: "expired" }` が返り、`currentTeamId` は変わらない。

## MECE Review
- AC IDs: (なし)
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

plans/invite-accept.md 設計を /mece-plan-review して、レビュー結果を設計書に反映して、設計を確定する。
