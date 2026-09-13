---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p plans src/billing migrations
cat > package.json <<'EOF'
{
  "name": "billing",
  "private": true,
  "scripts": { "test": "vitest run" },
  "dependencies": { "@acme/billing-schedule": "^2.0.0" },
  "devDependencies": { "vitest": "^2.0.0" }
}
EOF
cat > migrations/001_customers.sql <<'EOF'
CREATE TABLE customers (
  id serial PRIMARY KEY,
  email text NOT NULL,
  signup_date date NOT NULL
);
EOF
cat > src/billing/db.ts <<'EOF'
export const db = {
  async query(sql: string, params: unknown[] = []): Promise<Record<string, unknown>[]> {
    void sql;
    void params;
    return [];
  },
};
EOF
cat > src/billing/date.ts <<'EOF'
// 現状: 日付の存在確認をせず、31 日指定の 2 月は 3 月へ繰り越される。
export function nextBillingDate(billingDay: number, from: Date): Date {
  return new Date(Date.UTC(from.getUTCFullYear(), from.getUTCMonth(), billingDay));
}
EOF
cat > src/billing/customer.ts <<'EOF'
import { db } from "./db";

export async function registerCustomer(email: string, signupDate: Date): Promise<void> {
  await db.query("INSERT INTO customers (email, signup_date) VALUES ($1, $2)", [email, signupDate]);
}
EOF
cat > src/billing/date.test.ts <<'EOF'
import { describe, it, expect } from "vitest";
import { nextBillingDate } from "./date";

describe("nextBillingDate", () => {
  it("keeps the day when it exists in the month", () => {
    expect(nextBillingDate(15, new Date("2026-02-01"))).toEqual(new Date("2026-02-15"));
  });
});
EOF
cat > plans/billing-date.md <<'EOF'
# 請求日計算 設計

## 1. 目的
新規顧客の請求日を登録日の日付で固定し、その日が存在しない月は末日に丸める。既存顧客の請求日は変えない。

## 2. 仕様
- S-1: 登録日が 1〜28 日なら、毎月同じ日を請求日とする。
- S-2: 登録日が 29〜31 日なら、その日が存在しない月は末日を請求日とする。
- S-3: 既存顧客 (`customers.billing_day` が設定済み) の請求日は変更しない。
- S-4: 請求日は `customers.billing_day` 列 (新設、integer、nullable) に永続化する。

## 3. 変更対象
| ファイル | 変更 |
|---|---|
| migrations/002_add_billing_day.sql | 列追加 (新規) |
| src/billing/date.ts | 末日への丸め |
| src/billing/customer.ts | 登録時に billing_day を保存 |
| src/billing/date.test.ts | 境界テスト追加 |

## 4. 実装タスク
- T-1: `migrations/002_add_billing_day.sql` で `customers.billing_day` を追加する。
- T-2: `src/billing/date.ts` の `nextBillingDate(billingDay, from)` で S-1 / S-2 を実装する。
- T-3: `src/billing/customer.ts` の `registerCustomer` で登録日の日付を `billing_day` に保存する。既存行は更新しない。
- T-4: `src/billing/date.test.ts` に S-2 の境界テストを追加する。

## 5. 依存
- 請求の実行は外部パッケージ `@acme/billing-schedule` の `runBillingCycle` が `customers.billing_day` を読んで行う。本リポジトリにその実装は無く、本設計では変更しない。

## Acceptance Criteria
- [ ] AC-001: `nextBillingDate(15, new Date("2026-02-01"))` は `2026-02-15` を返す。
- [ ] AC-002: `nextBillingDate(31, new Date("2026-02-01"))` は `2026-02-28` を返し、`nextBillingDate(31, new Date("2026-03-01"))` は `2026-03-31` を返す。
- [ ] AC-003: `registerCustomer` を登録日 `2026-01-30` で呼ぶと、`customers` の該当行の `billing_day` が `30` になる。
- [ ] AC-004: `billing_day` が設定済みの既存顧客について、本変更の前後で `runBillingCycle` が生成する請求の日付が同一である。

## MECE Review
- AC IDs: AC-001, AC-002, AC-003, AC-004
- 対応: S-1→AC-001、S-2→AC-002、S-3→AC-004、S-4→AC-003。T-1→AC-003、T-2→AC-001/AC-002、T-3→AC-003、T-4→AC-001/AC-002。
- 所見: なし。
- Gate: ready
EOF
```

plans/billing-date.md 設計を /prepare-plan-for-implementation して、結果を設計書に反映して、設計を確定する。実装は指示まで禁止。
