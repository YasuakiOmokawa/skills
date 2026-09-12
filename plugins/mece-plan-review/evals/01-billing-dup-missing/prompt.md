---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p plans src/billing
cat > plans/billing.md <<'EOF'
# 請求管理 設計

## 1. 目的
利用者ごとの請求を作成・再試行・取消できるようにする。

## 2. 仕様
- S-1: 請求を作成し、作成できた請求 ID を返す。
- S-2: 作成に失敗した場合は最大 3 回まで再試行する。
- S-3: 作成済みの請求を取消でき、取消後は請求一覧に現れない。

## 3. 変更対象
| ファイル | 変更 |
|---|---|
| src/billing/create.ts | 請求作成 |
| src/billing/retry.ts | 再試行 |

## 4. 実装タスク
- T-1: `src/billing/create.ts` に請求作成 API を実装する。
- T-2: `src/billing/create.ts` に請求レコードの生成処理を実装する。
- T-3: `src/billing/retry.ts` に最大 3 回の再試行を実装する。

## Acceptance Criteria
- [ ] AC-001: 請求作成に成功すると `createInvoice` が `{ ok: true }` と請求 ID を返す。
- [ ] AC-002: 作成に失敗すると `createWithRetry` が最大 3 回 `createInvoice` を呼ぶ。
- [ ] AC-003: 3 回とも失敗した場合は例外を送出する。

## MECE Review
- AC IDs: (なし)
EOF
cat > src/billing/create.ts <<'EOF'
import { checkBillingAccess } from "./access";
import { store } from "./store";

export type CreateResult =
  | { ok: true; invoiceId: string }
  | { ok: false; reason: string };

export async function createInvoice(
  userId: string,
  amount: number,
): Promise<CreateResult> {
  const access = await checkBillingAccess(userId);
  if (!access.allowed) {
    return { ok: false, reason: access.reason };
  }
  const invoiceId = await store.insert({ userId, amount });
  return { ok: true, invoiceId };
}
EOF
cat > src/billing/retry.ts <<'EOF'
import { createInvoice, type CreateResult } from "./create";

export async function createWithRetry(
  userId: string,
  amount: number,
): Promise<CreateResult> {
  for (let attempt = 0; attempt < 3; attempt++) {
    const result = await createInvoice(userId, amount);
    if (result.ok) return result;
  }
  throw new Error("retry exhausted");
}
EOF
cat > src/billing/access.ts <<'EOF'
import { loadPolicy } from "./policy";

export type AccessDecision =
  | { allowed: true }
  | { allowed: false; reason: "suspended" | "no-permission" };

export async function checkBillingAccess(
  userId: string,
): Promise<AccessDecision> {
  const policy = await loadPolicy(userId);
  if (policy.suspended) {
    return { allowed: false, reason: "suspended" };
  }
  if (!policy.scopes.includes("billing:create")) {
    return { allowed: false, reason: "no-permission" };
  }
  return { allowed: true };
}
EOF
cat > src/billing/policy.ts <<'EOF'
export type Policy = { suspended: boolean; scopes: string[] };

const table: Record<string, Policy> = {
  "admin-1": { suspended: false, scopes: ["billing:create", "billing:read"] },
  "user-1": { suspended: false, scopes: ["billing:read"] },
  "user-2": { suspended: true, scopes: ["billing:create"] },
};

export async function loadPolicy(userId: string): Promise<Policy> {
  return table[userId] ?? { suspended: false, scopes: [] };
}
EOF
cat > src/billing/store.ts <<'EOF'
export const store = {
  async insert(row: { userId: string; amount: number }): Promise<string> {
    return `inv_${row.userId}_${row.amount}`;
  },
};
EOF
```

plans/billing.md 設計を /mece-plan-review して、レビュー結果を設計書に反映して、設計を確定する。
