---
max_turns: 30
timeout_seconds: 600
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p repo
cat > pr-body.md <<'EOF'
## なぜやるのか

合計に税率を掛けられるようにする。
EOF
cd repo
git init -q --template= --separate-git-dir=../repo.gitdir -b main .
export GIT_AUTHOR_NAME=fixture GIT_AUTHOR_EMAIL=fixture@example.com GIT_AUTHOR_DATE=2026-11-01T00:00:00Z
export GIT_COMMITTER_NAME=fixture GIT_COMMITTER_EMAIL=fixture@example.com GIT_COMMITTER_DATE=2026-11-01T00:00:00Z
mkdir -p .github src db/migrate
cat > .github/pr-checks.md <<'EOF'
# PR の検査項目

| ID | 対象 | 項目 |
|---|---|---|
| C1 | `**` | 引数を変えた関数の呼び出し元が、すべて変更後の引数で呼んでいる |
| M1 | `db/migrate/**` | 追加した up の migration に、対になる down の migration がある |
| L1 | `package.json` | メジャー番号が上がった依存ごとに、破壊的変更に該当する呼び出しの有無を挙げている |
EOF
cat > package.json <<'EOF'
{
  "name": "shop",
  "version": "1.0.0",
  "type": "module",
  "dependencies": {
    "left-pad": "1.3.0"
  }
}
EOF
cat > src/price.js <<'EOF'
export function total(items) {
  return items.reduce((sum, item) => sum + item.price, 0);
}
EOF
cat > src/cart.js <<'EOF'
import { total } from "./price.js";

export function cartTotal(cart) {
  return total(cart.items);
}
EOF
cat > src/report.js <<'EOF'
import { total } from "./price.js";

export function monthlyReport(orders) {
  return orders.map((order) => total(order.items));
}
EOF
git add -A
git -c commit.gpgsign=false commit -qm init
git switch -q -c feature/tax-rate
cat > src/price.js <<'EOF'
export function total(items, taxRate) {
  const sum = items.reduce((acc, item) => acc + item.price, 0);
  return sum * (1 + taxRate);
}
EOF
cat > src/cart.js <<'EOF'
import { total } from "./price.js";

export function cartTotal(cart) {
  return total(cart.items, cart.taxRate);
}
EOF
cat > db/migrate/001_add_tax_rate.up.sql <<'EOF'
ALTER TABLE carts ADD COLUMN tax_rate REAL NOT NULL DEFAULT 0;
EOF
cat > db/migrate/001_add_tax_rate.down.sql <<'EOF'
ALTER TABLE carts DROP COLUMN tax_rate;
EOF
git add -A
git -c commit.gpgsign=false commit -qm "合計に税率を掛ける"
cd ..
```

`repo/` のブランチ `feature/tax-rate` で PR を出します。base は `main` です。/check-pr を実行して、検査結果ブロックを `pr-body.md` の末尾に書いてください。
