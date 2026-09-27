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
cat > src/order-id.ts <<'EOF'
// 注文 ID のユーティリティ

// 決済代行が払い出す注文 ID は 19 桁あり、Number では 2^53 を超えた下位桁が丸まるので BigInt で持つ
export type OrderId = bigint;

// 文字列の注文 ID を読む
export function parseOrderId(raw: string): OrderId {
  // 前後の空白を落としてから変換する
  return BigInt(raw.trim());
}

// 注文 ID を文字列に戻す
export function formatOrderId(id: OrderId): string {
  return id.toString();
}

// 2 つの注文 ID が同じか
export function sameOrder(a: OrderId, b: OrderId): boolean {
  return a === b;
}
EOF
cat > src/order-id.test.ts <<'EOF'
import { test } from "node:test";
import assert from "node:assert/strict";
import { formatOrderId, parseOrderId, sameOrder } from "./order-id.ts";

test("parses and formats an order id", () => {
  assert.equal(formatOrderId(parseOrderId(" 42 ")), "42");
});
test("compares order ids by value", () => {
  assert.equal(sameOrder(parseOrderId("7"), parseOrderId("7")), true);
  assert.equal(sameOrder(parseOrderId("7"), parseOrderId("8")), false);
});
EOF
```

`node --test` が 2 件すべて成功することを確認してから、次の依頼に取りかかってください。

src/order-id.ts はコメントが多いので減らして、意図はコードで表して。振る舞いは変えないで。
