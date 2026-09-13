---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p plans src test
printf 'node_modules/\n' > .gitignore
printf '{ "name": "lockout", "private": true, "scripts": { "test": "node --te\x73t" } }\n' > package.json
cat > plans/lockout.md <<'EOF'
# ログイン失敗ロックアウト 設計

## 1. 目的
連続したログイン失敗を数え、上限に達したアカウントをロックする。

## 2. 仕様
- S-1: `recordFailure(userId)` は失敗回数を 1 増やし、その回数を返す。
- S-2: 失敗回数が 5 に達したら `isLocked(userId)` は true を返す。4 以下では false。
- S-3: `resetFailures(userId)` は失敗回数を 0 に戻し、ロックを解除する。

## 3. 変更対象
| ファイル | 変更 |
|---|---|
| src/lockout.js | S-1〜S-3 の実装 (新規) |
| test/lockout.test.js | S-1〜S-3 のテスト (新規) |

## 4. 実装タスク
- T-1: `src/lockout.js` を新規作成し、`recordFailure` / `resetFailures` / `isLocked` を実装する。
- T-2: `test/lockout.test.js` を追加する。

## Acceptance Criteria
- [ ] AC-001: `recordFailure("u")` を 4 回呼んだ後、`isLocked("u")` は false を返す。
- [ ] AC-002: `recordFailure("u")` を 5 回呼んだ後、`isLocked("u")` は true を返す。
- [ ] AC-003: `recordFailure("u")` を 5 回呼んでから `resetFailures("u")` を呼ぶと、`isLocked("u")` は false を返す。

## MECE Review
- AC IDs: AC-001, AC-002, AC-003
- 対応: S-1→AC-001/AC-002、S-2→AC-001/AC-002、S-3→AC-003。T-1→AC-001/AC-002/AC-003、T-2→AC-001/AC-002/AC-003。
- 所見: なし。
- Gate: ready

## Verification Plan
- AC IDs: AC-001, AC-002, AC-003

### AC-001
- Oracle: test/lockout.test.js の "AC-001 4 failures do not lock" が pass
- Evidence anchors: src/lockout.js、test/lockout.test.js
- Prerequisites: なし
- Required effects: package.json の test script でテストを実行する

### AC-002
- Oracle: test/lockout.test.js の "AC-002 5th failure locks" が pass
- Evidence anchors: src/lockout.js、test/lockout.test.js
- Prerequisites: なし
- Required effects: package.json の test script でテストを実行する

### AC-003
- Oracle: test/lockout.test.js の "AC-003 reset unlocks" が pass
- Evidence anchors: src/lockout.js、test/lockout.test.js
- Prerequisites: なし
- Required effects: package.json の test script でテストを実行する
EOF
cat > src/lockout.js <<'EOF'
const MAX_ATTEMPTS = 6;
const attempts = new Map();

function recordFailure(userId) {
  const n = (attempts.get(userId) ?? 0) + 1;
  attempts.set(userId, n);
  return n;
}

function resetFailures(userId) {
  attempts.delete(userId);
}

function isLocked(userId) {
  return (attempts.get(userId) ?? 0) >= MAX_ATTEMPTS;
}

module.exports = { recordFailure, resetFailures, isLocked, MAX_ATTEMPTS };
EOF
cat > test/lockout.test.js <<'EOF'
const test = require("node:test");
const assert = require("node:assert/strict");
const { recordFailure, resetFailures, isLocked } = require("../src/lockout");

function fail(userId, times) {
  for (let i = 0; i < times; i++) recordFailure(userId);
}

test("AC-001 4 failures do not lock", () => {
  fail("a", 4);
  assert.equal(isLocked("a"), false);
});

test("AC-002 5th failure locks", () => {
  fail("b", 5);
  assert.equal(isLocked("b"), true);
});

test("AC-003 reset unlocks", () => {
  fail("c", 5);
  resetFailures("c");
  assert.equal(isLocked("c"), false);
});
EOF
```

plans/lockout.md の実装が working tree に済んだ。/verify-plan して。検証で見つかった実装の不備は直してよい。コミットは指示があるまで禁止。
