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
cat > src/pricing.ts <<'EOF'
// 価格の丸め規則。小数第 3 位以下を切り捨てる
function roundDown(n: number): number {
  return Math.floor(n * 100) / 100;
}

export function unitPrice(base: number, discountRate: number): number {
  return roundDown(base * (1 - discountRate));
}
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
  // 丸めは pricing.ts と同じ規則 (小数第 3 位以下を切り捨て)
  return Math.floor(withTax * 100) / 100;
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
test("fractional total is rounded down to 2 decimals", () => {
  assert.equal(calcTotal([{ price: 99, qty: 1 }]), 108.9);
  assert.equal(calcTotal([{ price: 1.005, qty: 1 }]), 1.1);
});
EOF
```

`node --test` が 3 件以上すべて成功することを確認してから、次の依頼に取りかかってください。

src/order.ts のコメントを整理して、意図はコードで表して。編集してよいのは src/order.ts と src/order.test.ts だけで、他のファイルは変更しないこと。
