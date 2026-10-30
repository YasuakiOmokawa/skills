---
max_turns: 60
timeout_seconds: 1800
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p repo
cd repo
git init -q --template= --separate-git-dir=../repo.gitdir -b main .
mkdir -p src test/db db/migrations plans
cat > package.json <<'EOF'
{
  "name": "notes",
  "private": true,
  "scripts": {
    "test": "node --test test/unit",
    "db:up": "docker compose up -d db",
    "db:migrate": "node db/migrate.js",
    "test:db": "npm run db:up && npm run db:migrate && node --test test/db"
  }
}
EOF
cat > docker-compose.yml <<'EOF'
services:
  db:
    image: postgres:16
    ports: ["5432:5432"]
EOF
cat > db/migrations/0001_notes.sql <<'EOF'
CREATE TABLE notes (id serial PRIMARY KEY, body text NOT NULL);
EOF
cat > src/notes.js <<'EOF'
async function saveNote(db, body) {
  const { rows } = await db.query("INSERT INTO notes (body) VALUES ($1) RETURNING id", [body]);
  return rows[0].id;
}

module.exports = { saveNote };
EOF
cat > test/db/notes.test.js <<'EOF'
const test = require("node:test");
const assert = require("node:assert/strict");
const { connect } = require("../../db/connect");
const { saveNote } = require("../../src/notes");

test("saveNote stores the body", async () => {
  const db = await connect();
  const id = await saveNote(db, "hello");
  const { rows } = await db.query("SELECT body FROM notes WHERE id = $1", [id]);
  assert.equal(rows[0].body, "hello");
});
EOF
cat > plans/note-title.md <<'EOF'
# メモに題名を付ける 設計

## 1. 目的
メモに題名を保存できるようにする。

## 2. 仕様
- S-1: `notes` テーブルに `title text` 列を足す migration `db/migrations/0002_note_title.sql` を作る。
- S-2: `saveNote(db, body, title)` は題名も保存し、`SELECT title FROM notes WHERE id = $1` で読める。
- S-3: 題名を渡さなければ `title` は NULL で保存される。

## 3. 変更対象
| ファイル | 変更 |
|---|---|
| db/migrations/0002_note_title.sql | 新規 |
| src/notes.js | `title` を保存する |
| test/db/notes.test.js | S-2・S-3 の試験を足す |

## 4. 検証
DB を使う試験は `npm run test:db` で流す (DB コンテナを起動し、migration を適用してから試験を実行する)。
EOF
git add -A
git -c user.name=fixture -c user.email=fixture@example.com commit -qm init
```

`repo/plans/note-title.md` の設計を /define-done。
