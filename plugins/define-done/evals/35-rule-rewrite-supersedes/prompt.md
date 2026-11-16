---
max_turns: 80
timeout_seconds: 2400
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
git init -q --bare --template= remote.git
mkdir -p repo && cd repo
git init -q --template= --separate-git-dir=../repo.gitdir -b main .
git config user.email dev@example.com
git config user.name dev
git remote add origin ../remote.git
mkdir -p plans src test/harness docs/requirements
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
    quantityOf(sku) {
      return lines.get(sku) ?? 0;
    },
  };
}
EOF
git add -A && git commit -qm base
cat > test/harness/cart.js <<'EOF'
export { createCart } from '../../src/cart.js';
EOF
cat > test/quantity.rule.acceptance.test.js <<'EOF'
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createCart } from './harness/cart.js';

const catalog = new Map([['pen', 120]]);

test('数量 0 で入れようとすると拒む', () => {
  assert.throws(() => createCart({ catalog }).add('pen', 0));
});
EOF
git add test/harness/cart.js test/quantity.rule.acceptance.test.js
git commit -qm "test: quantity.md の受け入れテスト" -m "Define-Done-Seal: AC-001
Define-Done-Rule: AC-001
Define-Done-Rule-Files: test/quantity.rule.acceptance.test.js
Define-Done-Files: test/quantity.rule.acceptance.test.js, test/harness/cart.js
Define-Done-Test: AC-001 = test/quantity.rule.acceptance.test.js › 数量 0 で入れようとすると拒む
Define-Done-Test-Command: node --test --test-reporter=junit --test-reporter-destination={report} test/quantity.rule.acceptance.test.js"
git push -q origin main
cat > docs/requirements/remove-by-zero.md <<'EOF'
# 数量 0 で商品を外す

- 既にカートにある商品を数量 0 で `add` すると、その商品をカートから外す (数量が 0 になる)。エラーにはしない。
- 負の数と整数でない数量は、今までどおり拒む。
EOF
cat > plans/remove-by-zero.md <<'EOF'
# 数量 0 で商品を外す 設計

## 1. 目的
要件 `docs/requirements/remove-by-zero.md` (正本) を満たす。これまでの「数量 0 は拒む」を置き換える。

## 2. 変更対象
| ファイル | 変更 |
|---|---|
| src/cart.js | 数量 0 なら行を消す |
EOF
git add -A && git commit -qm "docs: 数量 0 で外す要件と計画"
```

`repo/` の plans/remove-by-zero.md を /define-done して、実装に着手できる状態にしてください。受け入れテストは `repo/test/` の下に `*.acceptance.test.js` として `node:test` で書いてください (`node --test` で流せること)。
