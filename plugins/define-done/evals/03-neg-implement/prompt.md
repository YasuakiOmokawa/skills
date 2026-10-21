---
max_turns: 25
timeout_seconds: 600
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
新規顧客の請求日を登録日の日付で固定し、その日が存在しない月は末日に丸める。

## 2. 仕様
- S-1: 登録日が 1〜28 日なら、毎月同じ日を請求日とする。
- S-2: 登録日が 29〜31 日なら、その日が存在しない月は末日を請求日とする。
- S-3: 請求日は `customers.billing_day` 列 (新設、integer、nullable) に永続化する。

## 3. 実装計画
1. `migrations/002_add_billing_day.sql` で `customers.billing_day` を追加する。先行なし。AC-003。検証: SQL ファイルの存在と `ALTER TABLE` 文。
2. `src/billing/date.test.ts` に AC-002 の境界テストを追加する。先行: なし。AC-002。検証: `npm test` が追加ケースで失敗する。
3. `src/billing/date.ts` の `nextBillingDate` で末日への丸めを実装する。先行: 2。AC-001 / AC-002。検証: `npm test` が通る。
4. `src/billing/customer.ts` の `registerCustomer` で `billing_day` を保存する。先行: 1。AC-003。検証: 発行 SQL に `billing_day` が含まれる。

## Acceptance Criteria
- [ ] AC-001: `nextBillingDate(15, new Date("2026-02-01"))` は `2026-02-15` を返す。
- [ ] AC-002: `nextBillingDate(31, new Date("2026-02-01"))` は `2026-02-28` を返す。
- [ ] AC-003: `registerCustomer` を登録日 `2026-01-30` で呼ぶと、`customers` の該当行の `billing_day` が `30` になる。

## MECE Review
- AC IDs: AC-001, AC-002, AC-003
- Gate: ready

## Verification Plan
- AC IDs: AC-001, AC-002, AC-003

### AC-001
- Oracle: nextBillingDate(15, new Date("2026-02-01")) の戻り値が 2026-02-15T00:00:00.000Z と等しい
- Evidence anchors: src/billing/date.test.ts、npm test
- Prerequisites: なし
- Required effects: npm test を実行する

### AC-002
- Oracle: nextBillingDate(31, new Date("2026-02-01")) の戻り値が 2026-02-28T00:00:00.000Z と等しい
- Evidence anchors: src/billing/date.test.ts、npm test
- Prerequisites: なし
- Required effects: npm test を実行する

### AC-003
- Oracle: registerCustomer("a@example.test", new Date("2026-01-30")) が db.query に渡す SQL と params に billing_day と 30 が含まれる
- Evidence anchors: src/billing/customer.ts、src/billing/db.ts
- Prerequisites: なし
- Required effects: db.query を spy に差し替えて registerCustomer を呼ぶ
EOF
```

準備済みの計画 plans/billing-date.md を実装して。コミットは禁止。
