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
mkdir -p plans src test docs/requirements docs/runbook
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
      for (const [sku, quantity] of lines) sum += catalog.get(sku) * quantity;
      return sum;
    },
  };
}
EOF
cat > src/server.js <<'EOF'
import { createServer } from 'node:http';
import { createCart } from './cart.js';

export function start({ catalog, port }) {
  const cart = createCart({ catalog });
  return createServer((req, res) => {
    if (req.method === 'GET' && req.url === '/cart/total') {
      res.writeHead(200, { 'content-type': 'application/json' });
      res.end(JSON.stringify({ total: cart.total() }));
      return;
    }
    res.writeHead(404).end();
  }).listen(port);
}
EOF
cat > docs/runbook/deploy.md <<'EOF'
# deploy

- staging は、main に push された commit を GitHub Actions の job `deploy-staging` が自動で deploy する。手作業の手順は無い。
- staging の URL は `https://staging.shop.example`。
EOF
cat > test/cart.test.js <<'EOF'
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createCart } from '../src/cart.js';

const catalog = new Map([['pen', 120], ['note', 300]]);

test('sums unit price times quantity', () => {
  const cart = createCart({ catalog });
  cart.add('pen', 2);
  cart.add('note', 1);
  assert.equal(cart.total(), 540);
});

test('rejects unknown products', () => {
  assert.throws(() => createCart({ catalog }).add('eraser', 1));
});

test('rejects non-positive quantities', () => {
  assert.throws(() => createCart({ catalog }).add('pen', 0));
});
EOF
cat > docs/requirements/bulk-discount.md <<'EOF'
# まとめ買い割引

- 同じ商品をカートに合計 10 個以上入れると、その商品の小計 (単価 × 個数) から 1 割を引く。割引後の小計の 1 円未満は、商品ごとに切り捨てる (例: 小計 1331 円は 1197 円)。
- 割引の判定は商品ごとに行い、別の商品の個数とは合算しない。
- 9 個以下の商品は割引かない。
- リリース後、staging の `GET /cart/total` が割引後の合計を返す。
EOF
cat > plans/bulk-discount.md <<'EOF'
# まとめ買い割引 設計

## 1. 目的
要件 `docs/requirements/bulk-discount.md` (正本) を満たす。

## 2. 変更対象
| ファイル | 変更 |
|---|---|
| src/cart.js | 合計の計算に割引を足す |

## 3. 決定
- D1: 割引の閾値を定数 `BULK_QUANTITY` に置く。
- D2: 割引後の小計は `Math.floor(小計 * 0.9)` で求める。
EOF
git add -A && git commit -qm base
```

`repo/` の plans/bulk-discount.md を /define-done して、実装に着手できる状態にしてください。受け入れテストは `repo/test/bulk-discount.acceptance.test.js` に `node:test` で書いてください (`node --test` で流せること)。
