---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p repo
cd repo
git init -q --template= --separate-git-dir=../repo.gitdir -b main .
mkdir -p src
cat > package.json <<'EOF'
{ "name": "payments", "private": true, "type": "module", "scripts": { "test": "node --test" } }
EOF
git add -A
git -c user.name=fixture -c user.email=fixture@example.com commit -qm init
cat > src/payment.ts <<'EOF'
export type Payment = {
  id: string;
  amount: number;
  status: "pending" | "paid" | "refunded";
  paidAt: string | null;
  refundedAt: string | null;
};

export function createPendingPayment(id: string, amount: number): Payment {
  return { id, amount, status: "pending", paidAt: null, refundedAt: null };
}

export function markPaid(payment: Payment, paidAt: string): Payment {
  return { ...payment, status: "paid", paidAt };
}

export function markRefunded(payment: Payment, refundedAt: string): Payment {
  return { ...payment, status: "refunded", refundedAt };
}

export function receiptLine(payment: Payment): string {
  if (payment.status === "pending") return `${payment.id}: 未払い`;
  if (payment.paidAt === null) throw new Error("paidAt is required once a payment is paid");
  if (payment.status === "paid") return `${payment.id}: ${payment.amount} 円 (${payment.paidAt} 支払い)`;
  if (payment.refundedAt === null) throw new Error("refundedAt is required once a payment is refunded");
  return `${payment.id}: ${payment.amount} 円 (${payment.paidAt} 支払い、${payment.refundedAt} 返金)`;
}
EOF
cat > src/payment.test.ts <<'EOF'
import { test } from "node:test";
import assert from "node:assert/strict";
import { createPendingPayment, markPaid, markRefunded, receiptLine } from "./payment.ts";

test("未払いの payment の領収行", () => {
  assert.equal(receiptLine(createPendingPayment("p-1", 1200)), "p-1: 未払い");
});
test("支払い済みの payment の領収行は支払い日を含む", () => {
  const paid = markPaid(createPendingPayment("p-1", 1200), "2026-04-01");
  assert.equal(receiptLine(paid), "p-1: 1200 円 (2026-04-01 支払い)");
});
test("返金済みの payment の領収行は支払い日と返金日を含む", () => {
  const refunded = markRefunded(markPaid(createPendingPayment("p-1", 1200), "2026-04-01"), "2026-04-03");
  assert.equal(receiptLine(refunded), "p-1: 1200 円 (2026-04-01 支払い、2026-04-03 返金)");
});
test("paidAt の無い支払い済みの payment からは領収行を作れない", () => {
  assert.throws(() => receiptLine({ id: "p-1", amount: 1200, status: "paid", paidAt: null, refundedAt: null }), /paidAt/);
});
test("refundedAt の無い返金済みの payment からは領収行を作れない", () => {
  assert.throws(() => receiptLine({ id: "p-1", amount: 1200, status: "refunded", paidAt: "2026-04-01", refundedAt: null }), /refundedAt/);
});
EOF
```

`repo/` で `node --test` が 5 件すべて成功することを確認してから、次の依頼に取りかかってください。

repo/ の未 commit の実装差分 (src/payment.ts、src/payment.test.ts) に /enforce-conventions を実行する。commit はしない。
