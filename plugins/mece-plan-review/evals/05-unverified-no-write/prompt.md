---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p plans src/billing
cat > plans/billing-v2.md <<'EOF'
# 請求管理 設計 v2

## 1. 目的
請求の作成と、失敗時の再試行を確実にする。

## 2. 仕様
- S-1: 請求を作成し、作成できた請求 ID を返す。
- S-2: 作成に失敗した場合は最大 3 回まで再試行する。

## 3. 変更対象
| ファイル | 変更 |
|---|---|
| src/billing/create.ts | 請求作成 |
| src/billing/retry.ts | 再試行 |

## 4. 実装タスク
- T-1: `src/billing/create.ts` に請求作成 API を実装する。
- T-2: `src/billing/retry.ts` に最大 3 回の再試行を実装する。

## Acceptance Criteria
- [ ] AC-001: 請求作成に成功すると `createInvoice` が `{ ok: true }` と請求 ID を返す。
- [ ] AC-002: 作成に失敗すると `src/billing/retry.ts` の `createWithRetry` が最大 3 回 `createInvoice` を呼ぶ。
EOF
cat > src/billing/create.ts <<'EOF'
import { store } from "./store";

export type CreateResult =
  | { ok: true; invoiceId: string }
  | { ok: false; reason: string };

export async function createInvoice(
  userId: string,
  amount: number,
): Promise<CreateResult> {
  const invoiceId = await store.insert({ userId, amount });
  return { ok: true, invoiceId };
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

plans/billing-v2.md 設計を /mece-plan-review して。
