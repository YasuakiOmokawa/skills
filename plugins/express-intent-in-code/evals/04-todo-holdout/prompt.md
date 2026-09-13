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
cat > src/order.ts <<'EOF'
// 注文合計を計算するモジュール
export type Item = { price: number; qty: number };

// items を受け取り税込合計を返す
export function calcTotal(items: Item[]): number {
  // 小計を 0 で初期化
  let subtotal = 0;
  // 各 item を足す
  for (const it of items) subtotal += it.price * it.qty;
  // 税を掛ける
  const withTax = subtotal * 1.1;
  // TODO: 端数は切り上げに変える
  // 小数点以下を切り捨てて返す
  return Math.floor(withTax);
}
EOF
cat > src/order.test.ts <<'EOF'
import { test } from "node:test";
import assert from "node:assert/strict";
import { calcTotal } from "./order.ts";

test("normal order", () => {
  assert.equal(calcTotal([{ price: 100, qty: 2 }, { price: 50, qty: 1 }]), 275);
});
test("empty order", () => {
  assert.equal(calcTotal([]), 0);
});
test("fractional total is floored", () => {
  assert.equal(calcTotal([{ price: 99, qty: 1 }]), 108);
});
EOF
```

`node --test` が 3 件以上すべて成功することを確認してから、次の依頼に取りかかってください。

src/order.ts のコメントを整理して。
