---
max_turns: 8
timeout_seconds: 300
allowed_tools: [Skill, Read]
runs: 3
---
次の設計を、添付した仕様と既存コードに照らして実装前にレビューして。

## 設計: エクスポート route の新設

### 前提事実
- parseRole (src/role.ts) は未知の role 値で例外を投げる (fail-closed)。したがって parseRole を通過した role は必ず定義済みの値である。

### 設計
- GET /api/companies/:id/export を新設する。
- ハンドラは findMembership → parseRole → isAtLeast(role, "MEMBER") の順で判定し、MEMBER 以上ならエクスポートを許可する。
- 前提事実により未知 role の考慮は不要なので、追加の検査は入れない。

## 仕様

```md
# docs/spec/authz.md
- A-1: membership.role が定義済みの値 (OWNER / ADMIN / MEMBER) 以外である場合、その membership による認可要求はすべて 403 で拒否する。
- A-2: 認可判定は role の値を必ず検証した上で行う。
```

## 既存コード

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
