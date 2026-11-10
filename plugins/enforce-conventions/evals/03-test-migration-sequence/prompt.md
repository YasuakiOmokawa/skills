---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p repo
cd repo
git init -q --template= --separate-git-dir=../repo.gitdir -b main .
mkdir -p node_modules/import-lint src/web src/app src/db src/domain src/infra
printf 'node_modules/\n' > .gitignore
cat > package.json <<'EOF'
{
  "name": "shop",
  "private": true,
  "type": "module",
  "scripts": { "test": "node --test", "lint": "node node_modules/import-lint/cli.mjs" },
  "devDependencies": { "import-lint": "1.2.0" }
}
EOF
cat > node_modules/import-lint/package.json <<'EOF'
{ "name": "import-lint", "version": "1.2.0", "type": "module", "bin": "cli.mjs" }
EOF
cat > node_modules/import-lint/README.md <<'EOF'
# import-lint

`lint.config.json` の `restrictedImports` の規則ごとに、`files` のディレクトリ配下の `.ts` が `forbidden` のディレクトリ配下を相対 import していれば、`lint error:` の行を出して exit 1 で終わる。規則の種類はこの 1 つだけで、plugin の仕組みは無い。

設定の例: { "restrictedImports": [{ "files": "src/web", "forbidden": "src/db", "message": "src/web から src/db を import しない" }] }
EOF
cat > node_modules/import-lint/cli.mjs <<'EOF'
import { readFileSync, readdirSync } from "node:fs";
import { join, relative } from "node:path";

const { restrictedImports } = JSON.parse(readFileSync("lint.config.json", "utf8"));

function withoutTrailingSlash(directory) {
  return directory.replace(/\/+$/, "");
}

function typescriptFilesUnder(directory) {
  return readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const path = join(directory, entry.name);
    if (entry.isDirectory()) return typescriptFilesUnder(path);
    return entry.name.endsWith(".ts") ? [path] : [];
  });
}

const errors = [];
for (const rule of restrictedImports) {
  const forbidden = withoutTrailingSlash(rule.forbidden);
  for (const file of typescriptFilesUnder(withoutTrailingSlash(rule.files))) {
    for (const [, specifier] of readFileSync(file, "utf8").matchAll(/from\s+"([^"]+)"/g)) {
      if (!specifier.startsWith(".")) continue;
      const imported = relative(".", join(file, "..", specifier));
      if (imported === forbidden || imported.startsWith(`${forbidden}/`)) {
        errors.push(`${file}: ${rule.message} (${imported})`);
      }
    }
  }
}
for (const error of errors) console.error(`lint error: ${error}`);
console.log(`${errors.length} errors`);
process.exit(errors.length === 0 ? 0 : 1);
EOF
cat > lint.config.json <<'EOF'
{
  "restrictedImports": [
    { "files": "src/web", "forbidden": "src/db", "message": "src/web から src/db を import しない" }
  ]
}
EOF
cat > CLAUDE.md <<'EOF'
# shop

## 規約

- `src/web/` から `src/db/` を import しない。DB へは `src/app/` を通す。
- `db/migrations/` のファイル名は `NNNN_<名前>.sql` にする。番号は `0001` から欠番も重複も無く続ける。
EOF
cat > src/infra/clock.ts <<'EOF'
export function currentTime(): Date {
  return new Date();
}
EOF
cat > src/domain/price.ts <<'EOF'
export function priceWithTax(price: number, taxRate: number): number {
  return Math.floor(price * (1 + taxRate));
}
EOF
cat > src/db/orders-table.ts <<'EOF'
export type OrderRow = { id: string; total: number; placedAt: string };

const rows: OrderRow[] = [];

export function insertOrder(row: OrderRow): void {
  rows.push(row);
}

export function selectOrders(): OrderRow[] {
  return [...rows];
}
EOF
cat > src/app/list-orders.ts <<'EOF'
import { selectOrders } from "../db/orders-table.ts";

export function listOrders() {
  return selectOrders();
}
EOF
cat > src/web/orders-page.ts <<'EOF'
import { listOrders } from "../app/list-orders.ts";

export function renderOrdersPage(): string {
  return listOrders()
    .map((order) => `${order.id}: ${order.total}`)
    .join("\n");
}
EOF
mkdir -p db/migrations
cat > db/migrations/0001_create_orders.sql <<'EOF'
create table orders (id text primary key, total integer not null);
EOF
cat > db/migrations/0002_add_placed_at.sql <<'EOF'
alter table orders add column placed_at text not null default '';
EOF
cat > src/db/migrations.ts <<'EOF'
import { readdirSync } from "node:fs";

export function migrationFileNames(directory: string): string[] {
  return readdirSync(directory)
    .filter((name) => name.endsWith(".sql"))
    .sort();
}

export function pendingMigrations(directory: string, applied: string[]): string[] {
  return migrationFileNames(directory).filter((name) => !applied.includes(name));
}
EOF
cat > src/db/migrations.test.ts <<'EOF'
import { test } from "node:test";
import assert from "node:assert/strict";
import { migrationFileNames, pendingMigrations } from "./migrations.ts";

test("適用済みを除いた migration を名前順に返す", () => {
  const all = migrationFileNames("db/migrations");
  assert.deepEqual(pendingMigrations("db/migrations", all.slice(0, 1)), all.slice(1));
});
EOF
git add -A
git -c user.name=fixture -c user.email=fixture@example.com commit -qm init
cat > db/migrations/0003_add_order_status.sql <<'EOF'
alter table orders add column status text not null default 'placed';
EOF
cat > src/db/orders-table.ts <<'EOF'
export type OrderRow = { id: string; total: number; placedAt: string; status: "placed" | "shipped" };

const rows: OrderRow[] = [];

export function insertOrder(row: OrderRow): void {
  rows.push(row);
}

export function selectOrders(): OrderRow[] {
  return [...rows];
}
EOF
```

`repo/` で `node --test` と `node node_modules/import-lint/cli.mjs` が成功することを確認してから、次の依頼に取りかかってください。

repo/ の未 commit の実装差分 (db/migrations/0003_add_order_status.sql、src/db/orders-table.ts) に /enforce-conventions を実行する。commit はしない。
