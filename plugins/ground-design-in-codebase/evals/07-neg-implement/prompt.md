---
max_turns: 10
timeout_seconds: 300
allowed_tools: [Skill, Read]
runs: 3
---
parseRole が未知の role 値を MEMBER に丸めているのを直して。未知の値なら listMembers が 403 を返すように、src/role.ts と src/routes/members.ts の修正後コードを書いて。レビューや設計の議論は要らない、コードだけ。

```ts
// src/role.ts
export const ROLES = ["OWNER", "ADMIN", "MEMBER"] as const;
export type Role = (typeof ROLES)[number];

export function parseRole(input: string): Role {
  if ((ROLES as readonly string[]).includes(input)) return input as Role;
  return "MEMBER"; // 旧データ互換: 未知の role は MEMBER として扱う
}

export function isAtLeast(role: Role, min: Role): boolean {
  return ROLES.indexOf(role) <= ROLES.indexOf(min);
}
```

```ts
// src/routes/members.ts
import { parseRole, isAtLeast } from "../role";
import { findMembership } from "../db";

export async function listMembers(userId: string, companyId: string) {
  const m = await findMembership(userId, companyId);
  if (!m) return { status: 403 };
  const role = parseRole(m.role);
  if (!isAtLeast(role, "ADMIN")) return { status: 403 };
  return { status: 200, body: await loadMembers(companyId) };
}
```
