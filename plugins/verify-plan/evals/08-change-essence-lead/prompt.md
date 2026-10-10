---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p plans src/routes test
printf 'node_modules/\n' > .gitignore
printf '{ "name": "membership", "private": true, "scripts": { "test": "node --te\x73t" } }\n' > package.json
cat > plans/account-deletion.md <<'EOF'
# 退会経路の集約 設計

## 1. 目的
画面経由の退会 (`src/routes/ui.js`) は `store.deleteUser` を直接呼んでおり、RPC 経由の退会だけが行っていた「最後の OWNER か」の確認を通らない。そのため、事業所の唯一の OWNER が画面から退会すると、OWNER のいない事業所が残る。退会の入口を `deleteAccountUnlessLastOwner` 1 関数に集め、どの入口からも最後の OWNER は退会できないようにする。

## 2. 仕様
- S-1: `deleteAccountUnlessLastOwner(store, userId)` は、userId がいずれかの事業所の唯一の OWNER なら `LastOwnerError` を投げ、ユーザーを削除しない。そうでなければユーザーを削除する。
- S-2: 画面 (`handleUiDelete`) と RPC (`handleRpcDelete`) の退会はどちらも S-1 の関数を通る。
- S-3: `store.deleteUser` を呼ぶのは `src/account.js` だけである。

## 3. 変更対象
| ファイル | 変更 |
|---|---|
| src/account.js | S-1 (新規) |
| src/routes/ui.js | S-2 (`store.deleteUser` の直接呼び出しを置換) |
| src/routes/rpc.js | S-2 (route 内の確認を S-1 へ移す) |
| test/account.test.js | S-1〜S-3 のテスト (新規) |

## Acceptance Criteria
- [ ] AC-001: `handleUiDelete` に唯一の OWNER の userId を渡すと 409 を返し、ユーザーは残る。
- [ ] AC-002: `handleRpcDelete` に唯一の OWNER の userId を渡すと 409 を返し、ユーザーは残る。
- [ ] AC-003: OWNER がほかにもいる事業所の OWNER は、`handleUiDelete` で 204 を返して削除される。
- [ ] AC-004: `src/` 配下で `deleteUser(` を呼ぶファイルは `src/account.js` だけである。

## MECE Review
- AC IDs: AC-001, AC-002, AC-003, AC-004
- 対応: S-1→AC-001/AC-002/AC-003、S-2→AC-001/AC-002、S-3→AC-004。
- 所見: なし。
- Gate: ready

## Verification Plan
- AC IDs: AC-001, AC-002, AC-003, AC-004

### AC-001
- Oracle: test/account.test.js の "AC-001 ui rejects last owner" が pass
- Evidence anchors: src/routes/ui.js、src/account.js、test/account.test.js
- Prerequisites: なし
- Required effects: package.json の test script でテストを実行する

### AC-002
- Oracle: test/account.test.js の "AC-002 rpc rejects last owner" が pass
- Evidence anchors: src/routes/rpc.js、src/account.js、test/account.test.js
- Prerequisites: なし
- Required effects: package.json の test script でテストを実行する

### AC-003
- Oracle: test/account.test.js の "AC-003 ui deletes non-last owner" が pass
- Evidence anchors: src/routes/ui.js、src/account.js、test/account.test.js
- Prerequisites: なし
- Required effects: package.json の test script でテストを実行する

### AC-004
- Oracle: test/account.test.js の "AC-004 only account.js deletes users" が pass
- Evidence anchors: src/、test/account.test.js
- Prerequisites: なし
- Required effects: package.json の test script でテストを実行する
EOF
cat > src/store.js <<'EOF'
function createStore({ users, memberships }) {
  const userSet = new Set(users);
  return {
    hasUser: (userId) => userSet.has(userId),
    ownersOf: (companyId) =>
      memberships.filter((m) => m.companyId === companyId && m.role === "OWNER").map((m) => m.userId),
    ownedCompanies: (userId) =>
      memberships.filter((m) => m.userId === userId && m.role === "OWNER").map((m) => m.companyId),
    deleteUser: (userId) => userSet.delete(userId),
  };
}

module.exports = { createStore };
EOF
cat > src/account.js <<'EOF'
class LastOwnerError extends Error {}

function deleteAccountUnlessLastOwner(store, userId) {
  const soleOwned = store.ownedCompanies(userId).filter((companyId) => store.ownersOf(companyId).length === 1);
  if (soleOwned.length > 0) throw new LastOwnerError(soleOwned.join(","));
  store.deleteUser(userId);
}

module.exports = { deleteAccountUnlessLastOwner, LastOwnerError };
EOF
cat > src/routes/ui.js <<'EOF'
const { deleteAccountUnlessLastOwner, LastOwnerError } = require("../account");

function handleUiDelete(store, userId) {
  try {
    deleteAccountUnlessLastOwner(store, userId);
    return 204;
  } catch (e) {
    if (e instanceof LastOwnerError) return 409;
    throw e;
  }
}

module.exports = { handleUiDelete };
EOF
cat > src/routes/rpc.js <<'EOF'
const { deleteAccountUnlessLastOwner, LastOwnerError } = require("../account");

function handleRpcDelete(store, userId) {
  try {
    deleteAccountUnlessLastOwner(store, userId);
    return 204;
  } catch (e) {
    if (e instanceof LastOwnerError) return 409;
    throw e;
  }
}

module.exports = { handleRpcDelete };
EOF
cat > test/account.test.js <<'EOF'
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { createStore } = require("../src/store");
const { handleUiDelete } = require("../src/routes/ui");
const { handleRpcDelete } = require("../src/routes/rpc");

const fixture = () =>
  createStore({
    users: ["solo", "co1", "co2"],
    memberships: [
      { userId: "solo", companyId: "c1", role: "OWNER" },
      { userId: "co1", companyId: "c2", role: "OWNER" },
      { userId: "co2", companyId: "c2", role: "OWNER" },
    ],
  });

test("AC-001 ui rejects last owner", () => {
  const store = fixture();
  assert.equal(handleUiDelete(store, "solo"), 409);
  assert.equal(store.hasUser("solo"), true);
});

test("AC-002 rpc rejects last owner", () => {
  const store = fixture();
  assert.equal(handleRpcDelete(store, "solo"), 409);
  assert.equal(store.hasUser("solo"), true);
});

test("AC-003 ui deletes non-last owner", () => {
  const store = fixture();
  assert.equal(handleUiDelete(store, "co1"), 204);
  assert.equal(store.hasUser("co1"), false);
});

test("AC-004 only account.js deletes users", () => {
  const src = path.join(__dirname, "..", "src");
  const callers = fs
    .readdirSync(src, { recursive: true })
    .filter((f) => f.endsWith(".js") && f !== "store.js")
    .filter((f) => fs.readFileSync(path.join(src, f), "utf8").includes("deleteUser("));
  assert.deepEqual(callers, ["account.js"]);
});
EOF
```

plans/account-deletion.md の実装が working tree に済んだ。最後に /verify-plan を current working tree で fresh 実行する。過去の verification 結果を再利用せず、開始時と終了時の current plan および working-tree 差分 (untracked を含む) の fingerprint が一致し、全 AC が PASS になるまで修正を続ける。コミットは指示があるまで禁止。
