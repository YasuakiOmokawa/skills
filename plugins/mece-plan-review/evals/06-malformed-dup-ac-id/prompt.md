---
max_turns: 20
timeout_seconds: 400
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p plans src/billing
cat > plans/billing-v3.md <<'EOF'
# 請求管理 設計 v3

## 1. 目的
請求の作成と再試行を確実にする。

## 2. 仕様
- S-1: 請求を作成し、作成できた請求 ID を返す。
- S-2: 作成に失敗した場合は最大 3 回まで再試行する。

## 3. 変更対象
| ファイル | 変更 |
|---|---|
| src/billing/create.ts | 請求作成 |

## 4. 実装タスク
- T-1: `src/billing/create.ts` に請求作成 API を実装する。

## Acceptance Criteria
- [ ] AC-001: 請求作成に成功すると `createInvoice` が `{ ok: true }` と請求 ID を返す。
- [ ] AC-002: 作成に失敗すると `createInvoice` が `{ ok: false }` を返す。
- [ ] AC-002: 作成に失敗したとき、呼び出し元は最大 3 回まで再試行できる。
- [ ] AC-003: 請求 ID は `inv_` で始まる。
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

plans/billing-v3.md 設計を /mece-plan-review して、レビュー結果を設計書に反映して、設計を確定する。
