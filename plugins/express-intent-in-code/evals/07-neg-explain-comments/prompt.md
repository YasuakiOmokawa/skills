---
max_turns: 15
timeout_seconds: 600
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
// 価格計算のユーティリティ
// 金額は円だが整数とは限らない (小数を許す)

// 会員ランクごとの割引率
// gold は 10%、silver は 5%、それ以外は 0
export type Rank = "gold" | "silver" | "none";

// ランクを受け取り割引率を返す
export function rate(r: Rank): number {
  // gold なら 0.1
  if (r === "gold") return 0.1;
  // silver なら 0.05
  if (r === "silver") return 0.05;
  // それ以外は割引なし
  return 0;
}

// 単価に割引を適用する
// 結果は小数第 3 位以下を切り捨てる (小数第 2 位までが表示単位)
export function apply(p: number, r: Rank): number {
  // 割引率を引いた係数を掛ける
  const v = p * (1 - rate(r));
  // 100 倍して floor して 100 で割る
  // 丸めは切り捨て: 経理の指示 (2023-07 の月次締めで四捨五入との差額が問題化) により切り上げ・四捨五入は不可
  return Math.floor(v * 100) / 100;
}
EOF
cat > src/shipping.ts <<'EOF'
// 送料計算
// 送料は 500 円。ただし小計 5000 円以上で無料
export const FEE = 500;
export const FREE_MIN = 5000;

// 離島は追加料金 800 円
const REMOTE_EXTRA = 800;

// 小計と離島フラグから送料を返す
export function fee(sub: number, remote: boolean): number {
  // 空の注文には送料を掛けない
  if (sub === 0) return 0;
  // 無料条件
  // 離島は無料条件を満たしても追加料金だけは掛かる (運送会社との契約 2025 年度版 第 4 条)
  const base = sub >= FREE_MIN ? 0 : FEE;
  // 離島なら追加
  return base + (remote ? REMOTE_EXTRA : 0);
}
EOF
cat > src/order.ts <<'EOF'
// 注文合計を計算するモジュール
import { apply, type Rank } from "./pricing.ts";
import { fee } from "./shipping.ts";

// price は税抜き単価 (円)
export type Item = { price: number; qty: number };
// 注文。remote は離島配送
export type Order = { items: Item[]; rank: Rank; remote: boolean };

// 消費税 10%
const TAX = 0.1;

// 注文を受け取り税込合計を返す
export function calcTotal(o: Order): number {
  // 小計を 0 で初期化
  let tmp = 0;
  // 各 item をループして割引後単価 × qty を足す
  for (const it of o.items) {
    // tmp は税抜き小計
    tmp += apply(it.price, o.rank) * it.qty;
  }
  // 送料を足す
  const s = fee(tmp, o.remote);
  // 税を掛ける (送料にも課税)
  const x = (tmp + s) * (1 + TAX);
  // Math.round ではなく floor: 2024-03 の税務相談の回答に従う (社内 wiki 消費税/端数)
  return Math.floor(x);
}
EOF
cat > src/pricing.test.ts <<'EOF'
import { test } from "node:test";
import assert from "node:assert/strict";
import { apply, rate } from "./pricing.ts";

test("rates", () => {
  assert.equal(rate("gold"), 0.1);
  assert.equal(rate("silver"), 0.05);
  assert.equal(rate("none"), 0);
});
test("apply rounds down to 2 decimals", () => {
  assert.equal(apply(100, "gold"), 90);
  assert.equal(apply(99.99, "silver"), 94.99);
  assert.equal(apply(10, "none"), 10);
});
EOF
cat > src/shipping.test.ts <<'EOF'
import { test } from "node:test";
import assert from "node:assert/strict";
import { fee } from "./shipping.ts";

test("shipping fee", () => {
  assert.equal(fee(0, false), 0);
  assert.equal(fee(0, true), 0);
  assert.equal(fee(100, false), 500);
  assert.equal(fee(5000, false), 0);
  assert.equal(fee(5000, true), 800);
  assert.equal(fee(100, true), 1300);
});
EOF
cat > src/order.test.ts <<'EOF'
import { test } from "node:test";
import assert from "node:assert/strict";
import { calcTotal } from "./order.ts";

test("normal order includes shipping", () => {
  assert.equal(calcTotal({ items: [{ price: 100, qty: 2 }, { price: 50, qty: 1 }], rank: "none", remote: false }), 825);
});
test("empty order", () => {
  assert.equal(calcTotal({ items: [], rank: "gold", remote: true }), 0);
});
test("gold member to remote island", () => {
  assert.equal(calcTotal({ items: [{ price: 5000, qty: 1 }], rank: "gold", remote: true }), 6380);
});
test("fractional total is floored", () => {
  assert.equal(calcTotal({ items: [{ price: 99, qty: 1 }], rank: "none", remote: false }), 658);
});
EOF
```

`node --test` が 3 件以上すべて成功することを確認してから、次の依頼に取りかかってください。

src/order.ts のコメントはそれぞれ何を説明している? 変更はせず、読んで答えて。
