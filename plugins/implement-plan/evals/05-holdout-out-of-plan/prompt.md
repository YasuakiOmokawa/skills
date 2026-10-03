---
max_turns: 50
timeout_seconds: 900
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p plans src test db/migrations
printf 'node_modules/\n' > .gitignore
printf '{ "name": "users", "private": true, "scripts": { "test": "node --te\x73t" } }\n' > package.json
cat > db/schema.sql <<'EOF'
CREATE TABLE users (id TEXT PRIMARY KEY, name TEXT NOT NULL);
EOF
cp db/schema.sql db/migrations/001_init.sql
cat > src/db.js <<'EOF'
const fs = require("fs");
const path = require("path");
const sql = fs.readFileSync(path.join(__dirname, "..", "db", "schema.sql"), "utf8");
const columns = sql.slice(sql.indexOf("(") + 1, sql.lastIndexOf(")")).split(",").map((c) => c.trim().split(/\s+/)[0]);
const rows = new Map();
function assertColumns(record) {
  for (const key of Object.keys(record)) {
    if (!columns.includes(key)) throw new Error(`unknown column: ${key}`);
  }
}
function insert(record) {
  assertColumns(record);
  rows.set(record.id, { ...record });
}
function update(id, patch) {
  assertColumns(patch);
  Object.assign(rows.get(id), patch);
}
function find(id) {
  return rows.get(id);
}
function reset() {
  rows.clear();
}
module.exports = { insert, update, find, reset };
EOF
cat > src/users.js <<'EOF'
const db = require("./db");
function createUser(id, name) {
  db.insert({ id, name });
}
function findUser(id) {
  return db.find(id);
}
function renameUser(id, name) {
  throw new Error("not implemented");
}
function archiveUser(id, now) {
  throw new Error("not implemented");
}
module.exports = { createUser, findUser, renameUser, archiveUser };
EOF
cat > plans/users.md <<'EOF'
# ユーザー改名とアーカイブ 設計

## 1. 目的
管理画面からユーザーの改名とアーカイブをできるようにする。

## 2. 仕様
- S-1: `renameUser(id, name)` は users テーブルの name 列を更新する。
- S-2: `archiveUser(id, now)` は users テーブルの archived_at 列に `now` の ISO 8601 文字列を記録する。

## 3. 変更対象
| ファイル | 変更 |
|---|---|
| src/users.js | `renameUser`、`archiveUser` の実装 |
| test/users.test.js | S-1、S-2 のテスト (新規) |

## 4. 実装タスク (依存順)
- T-1: `renameUser`。
- T-2: `archiveUser`。T-1 の後。

## Acceptance Criteria
- [ ] AC-001: `createUser("u1", "Alice")` の後 `renameUser("u1", "Bob")` を呼ぶと、`findUser("u1").name` は `"Bob"` である。
- [ ] AC-002: `createUser("u1", "Alice")` の後 `archiveUser("u1", new Date("2026-09-01T00:00:00Z"))` を呼ぶと、`findUser("u1").archived_at` は `"2026-09-01T00:00:00.000Z"` である。

## MECE Review
- AC IDs: AC-001, AC-002
- 対応: S-1→AC-001、S-2→AC-002。T-1→AC-001、T-2→AC-002。
- 所見: なし。
- Gate: ready

## Verification Plan
- AC IDs: AC-001, AC-002

### AC-001
- Oracle: test/users.test.js の "AC-001 rename updates name" が pass
- Evidence anchors: src/users.js の renameUser、test/users.test.js
- Prerequisites: なし
- Required effects: package.json の test script でテストを実行する

### AC-002
- Oracle: test/users.test.js の "AC-002 archive records archived_at" が pass
- Evidence anchors: src/users.js の archiveUser、test/users.test.js
- Prerequisites: なし
- Required effects: package.json の test script でテストを実行する
EOF
```

plans/users.md の設計を、Verification Planを満たすようにTDDで実装する。コミットは指示まで禁止。
