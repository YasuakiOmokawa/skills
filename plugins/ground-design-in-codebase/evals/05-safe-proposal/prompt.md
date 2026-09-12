---
max_turns: 8
timeout_seconds: 300
allowed_tools: [Skill, Read]
runs: 3
---
次の設計を、仕様と既存コードに照らして実装前にレビューして。

## 設計: ログイン成功の監査ログ

- src/auth/login.ts の成功パス末尾 (createSession の後、return の直前) で、既存の recordEvent を `recordEvent("login.succeeded", { userId: user.id })` として 1 回呼ぶ。
- 新しい event kind "login.succeeded" を src/audit/kinds.ts の `EVENT_KINDS` 配列末尾に追加する。
- 失敗パスは変更しない。

## 仕様

```md
# docs/spec/audit.md
- AU-1: ログイン成功は監査ログに記録する。payload は userId を含む。
- AU-2: 監査ログは追記専用で、既存 event の形式を変えてはならない。
```

## 既存コード

```ts
// src/audit/kinds.ts
export const EVENT_KINDS = ["login.failed", "invitation.accepted"] as const;
export type EventKind = (typeof EVENT_KINDS)[number];
```

```ts
// src/audit/audit-log.ts
import type { EventKind } from "./kinds";
// 追記専用。既存 kind の payload 形状は固定 (audit-log.test.ts が snapshot で検証)。
export async function recordEvent(kind: EventKind, payload: Record<string, string>) {
  await db.insert("audit_events", { kind, payload: JSON.stringify(payload), at: Date.now() });
}
```

```ts
// src/auth/login.ts
import { recordEvent } from "../audit/audit-log";
type User = { id: string; hash: string };
declare function findUser(email: string): Promise<User | null>;

export async function login(email: string, password: string) {
  const user = await findUser(email);
  if (!user || !verify(password, user.hash)) {
    await recordEvent("login.failed", { email });
    return { ok: false };
  }
  const session = await createSession(user.id);
  return { ok: true, session };
}
```

```ts
// src/audit/__tests__/audit-log.test.ts
it("既存 kind の payload 形状", async () => {
  await recordEvent("login.failed", { email: "a@b" });
  expect(lastRow()).toMatchInlineSnapshot(`{ "kind": "login.failed", "payload": "{\"email\":\"a@b\"}" }`);
});
it("EVENT_KINDS は kind 毎に 1 つ", () => {
  expect(new Set(EVENT_KINDS).size).toBe(EVENT_KINDS.length);
});
```
