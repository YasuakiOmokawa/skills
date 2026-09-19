---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Skill, Read, Write, Edit, Bash]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p src
cat > package.json <<'EOF'
{ "name": "fixture", "private": true, "type": "module", "scripts": { "test": "node --test" } }
EOF
cat > src/attempt-budget.ts <<'EOF'
export type Counter = {
  // 失敗時は null を返す。倒し方 (fail-closed / fail-open) は呼び手が決める
  incrementWindow(key: string, windowSeconds: number): Promise<{ count: number } | null>;
};

export type AttemptBudgetVerdict = "accepted" | "exhausted" | "unavailable";

export async function spendBudget(
  counter: Counter,
  input: { key: string; windowSeconds: number; maxAttempts: number },
): Promise<AttemptBudgetVerdict> {
  const counted = await counter.incrementWindow(input.key, input.windowSeconds);
  // 契約逸脱の 0 / NaN を accepted に写さず unavailable に倒す
  if (!counted || !(counted.count >= 1)) return "unavailable";
  return counted.count > input.maxAttempts ? "exhausted" : "accepted";
}
EOF
cat > src/totp.ts <<'EOF'
const TOTP_CODE = /^[0-9]{6}$/;

export type Matched = { timestep: number };

// 書式誤りも不一致も同じ null。wire 契約は両方を invalid_code にする
export function matchCode(expectedFor: (timestep: number) => string, code: string, nowMs: number): Matched | null {
  if (!TOTP_CODE.test(code)) return null;
  const step = Math.floor(nowMs / 30_000);
  for (const t of [step - 1, step, step + 1]) {
    if (expectedFor(t) === code) return { timestep: t };
  }
  return null;
}

export function activate(expectedFor: (t: number) => string, code: string, nowMs: number): "activated" | "invalid_code" {
  return matchCode(expectedFor, code, nowMs) ? "activated" : "invalid_code";
}

export function verify(expectedFor: (t: number) => string, code: string, nowMs: number): "ok" | "invalid_code" {
  return matchCode(expectedFor, code, nowMs) ? "ok" : "invalid_code";
}
EOF
cat > src/budget.test.ts <<'EOF'
import { test } from "node:test";
import assert from "node:assert/strict";
import { spendBudget } from "./attempt-budget.ts";
import { activate, verify } from "./totp.ts";

const counterReturning = (value: { count: number } | null) => ({ incrementWindow: async () => value });
const input = { key: "k", windowSeconds: 60, maxAttempts: 3 };

test("within budget is accepted", async () => {
  assert.equal(await spendBudget(counterReturning({ count: 3 }), input), "accepted");
});
test("over budget is exhausted", async () => {
  assert.equal(await spendBudget(counterReturning({ count: 4 }), input), "exhausted");
});
test("counter failure is unavailable", async () => {
  assert.equal(await spendBudget(counterReturning(null), input), "unavailable");
  assert.equal(await spendBudget(counterReturning({ count: 0 }), input), "unavailable");
});

const expectedFor = (t: number) => String(t).padStart(6, "0").slice(-6);
const now = 30_000 * 123456;

test("totp accepts the current step", () => {
  assert.equal(activate(expectedFor, expectedFor(123456), now), "activated");
  assert.equal(verify(expectedFor, expectedFor(123456), now), "ok");
});
test("totp rejects malformed and mismatched codes alike", () => {
  assert.equal(verify(expectedFor, "12", now), "invalid_code");
  assert.equal(verify(expectedFor, "000000", now), "invalid_code");
});
EOF
```

`node --test` が 5 件すべて成功することを確認してから、次の依頼に取りかかってください。

src/attempt-budget.ts と src/totp.ts の意図をコードで表して。挙動は変えないで。
