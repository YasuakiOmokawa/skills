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
mkdir -p plans src test docs/adr docs/requirements
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
cat > docs/requirements/string-quantity.md <<'EOF'
# 数量の文字列

- フォームから届く数量は文字列になる。`add` は、正の整数を表す 10 進の文字列 (例: "3") も、その数値として受け付ける。
EOF
cat > plans/string-quantity.md <<'EOF'
# 数量の文字列 設計

## 1. 目的
要件 `docs/requirements/string-quantity.md` (正本) を満たす。

## 2. 変更対象
| ファイル | 変更 |
|---|---|
| src/cart.js | `add` で文字列の数量を数値に変える |

## 3. 決定
- D1: 数量は `Number.parseInt(quantity, 10)` で数値に変えてから、既存の検査に渡す。
EOF
git add -A && git commit -qm base
```

`repo/` の plans/string-quantity.md を /define-done して、実装に着手できる状態にしてください。受け入れテストは `repo/test/string-quantity.acceptance.test.js` に `node:test` で書いてください (`node --test` で流せること)。
