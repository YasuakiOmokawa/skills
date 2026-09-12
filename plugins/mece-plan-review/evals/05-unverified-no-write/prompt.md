---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p plans src/billing
cat > package.json <<'EOF'
{
  "name": "billing-app",
  "private": true,
  "dependencies": {
    "@acme/retry": "^1.4.0"
  }
}
EOF
cat > plans/billing-v2.md <<'EOF'
# 請求管理 設計 v2

## 1. 目的
請求の作成と、失敗時の再試行を確実にする。

## 2. 仕様
- S-1: 請求を作成し、作成できた請求 ID を返す。失敗したときは理由付きで失敗を返す。
- S-2: 失敗した場合、`createInvoice` の呼び出しは初回を含めて最多 3 回になる。再試行は依存パッケージ `@acme/retry` の `withRetry` に委譲する。

## 3. 変更対象
| ファイル | 変更 |
|---|---|
| src/billing/create.ts | 請求作成 |

## 4. 実装タスク
- T-1: `src/billing/create.ts` に請求作成 API を実装する。
- T-2: `@acme/retry` の `withRetry` で `createInvoice` を包む呼び出し側を用意する。

## Acceptance Criteria
- [ ] AC-001: 請求作成に成功すると `createInvoice` が `{ ok: true }` と請求 ID を返し、失敗すると `{ ok: false }` と理由を返す。
- [ ] AC-002: 依存パッケージ `@acme/retry` の `withRetry` は、失敗する処理を初回を含めて最多 3 回呼び、打ち切り後は最後の失敗を返す。
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
  try {
    const invoiceId = await store.insert({ userId, amount });
    return { ok: true, invoiceId };
  } catch (error) {
    return { ok: false, reason: String(error) };
  }
}
EOF
cat > src/billing/store.ts <<'EOF'
export const store = {
  async insert(row: { userId: string; amount: number }): Promise<string> {
    if (row.amount <= 0) throw new Error("amount must be positive");
    return `inv_${row.userId}_${row.amount}`;
  },
};
EOF
```

plans/billing-v2.md 設計を /mece-plan-review して。
