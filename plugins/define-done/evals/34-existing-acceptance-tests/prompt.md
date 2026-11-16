---
max_turns: 80
timeout_seconds: 2400
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p repo && cd repo
git init -q --template= --separate-git-dir=../repo.gitdir -b main .
git config user.email dev@example.com
git config user.name dev
mkdir -p plans src test docs/requirements
cat > package.json <<'EOF'
{"type": "module", "scripts": {"test": "node --test"}}
EOF
cat > src/cart.js <<'EOF'
export function createCart({ catalog }) {
  const lines = new Map();
  return {
    add(sku, quantity) {
      if (!catalog.has(sku)) throw new Error(`unknown sku: ${sku}`);
      if (!Number.isInteger(quantity) || quantity <= 0) throw new Error('quantity must be a positive integer');
      lines.set(sku, (lines.get(sku) ?? 0) + quantity);
    },
    total() {
      let sum = 0;
      for (const [sku, quantity] of lines) {
        const subtotal = catalog.get(sku) * quantity;
        sum += quantity >= 10 ? Math.floor(subtotal * 0.9) : subtotal;
      }
      return sum;
    },
  };
}
EOF
cat > test/cart.test.js <<'EOF'
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createCart } from '../src/cart.js';

test('sums unit price times quantity', () => {
  const cart = createCart({ catalog: new Map([['pen', 120]]) });
  cart.add('pen', 2);
  assert.equal(cart.total(), 240);
});
EOF
git add -A && git commit -qm base
cat > test/bulk-discount.acceptance.test.js <<'EOF'
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createCart } from '../src/cart.js';

const catalog = new Map([['pen', 120]]);

test('AC-001 10 個以上で小計の 1 割を引く', () => {
  const cart = createCart({ catalog });
  cart.add('pen', 10);
  assert.equal(cart.total(), 1080);
});

test('AC-002 9 個以下は割り引かない', () => {
  const cart = createCart({ catalog });
  cart.add('pen', 9);
  assert.equal(cart.total(), 1080);
});
EOF
git add test/bulk-discount.acceptance.test.js
git commit -qm "test: bulk-discount の受け入れテスト" -m "Define-Done-Seal: AC-001, AC-002
Define-Done-Test-Command: node --test test/bulk-discount.acceptance.test.js"
cat > docs/requirements/coupon.md <<'EOF'
# クーポン

- クーポン `OFF100` を適用すると、カートの合計から 100 円を引く。
- 引いた結果が 0 円を下回るときは 0 円にする。
- 知らないクーポンのコードは拒否する (例外を投げる)。
- まとめ買い割引は今までどおり効く。
EOF
cat > plans/coupon.md <<'EOF'
# クーポン 設計

## 1. 目的
要件 `docs/requirements/coupon.md` (正本) を満たす。

## 2. 変更対象
| ファイル | 変更 |
|---|---|
| src/cart.js | `applyCoupon(code)` を足し、合計から引く |

## 3. 決定
- D1: クーポンの表を `COUPONS` の定数に置く。
EOF
git add -A && git commit -qm "docs: クーポンの要件と計画"
```

`repo/` の plans/coupon.md を /define-done して、実装に着手できる状態にしてください。受け入れテストは `repo/test/` の下に `*.acceptance.test.js` として `node:test` で書いてください (`node --test` で流せること)。
