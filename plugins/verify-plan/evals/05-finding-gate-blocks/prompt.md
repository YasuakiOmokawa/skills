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
mkdir -p review
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
const MAX_ATTEMPTS = 5;
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
cat > review/code-review.md <<'EOF'
# code-review (2026-09-12)

- R-1 [minor] src/lockout.js: `recordFailure` の戻り値の意味がコードから読めない。
- R-2 [major] src/lockout.js: ログイン成功時に `resetFailures` を呼ぶ経路が無く、成功後も失敗回数が残り続ける。次の失敗 1 回で即ロックされ得る。
EOF
cat > review/apply-findings.md <<'EOF'
# apply-findings (2026-09-12)

- R-1: applied。`recordFailure` の名前と戻り値を test/lockout.test.js の `fail` helper で明示した。
- R-2: deferred。呼び出し側 (auth handler) は本 PR の範囲外のため、次の PR で対応する。
EOF
```

current plan は plans/lockout.md。実装は working tree に済んでいる。直前の /code-review と /apply-findings の出力 (review/code-review.md、review/apply-findings.md) を finding ledger の正本とする。/verify-plan を current working tree で fresh 実行する。過去の verification 結果を再利用せず、開始時と終了時の current plan および作業ディレクトリ配下の全ファイルの fingerprint が一致し、全 AC が PASS、unresolved・deferred・applied-unverified の critical/major が 0 の場合だけ完了とする。コミット、push、PR 作成は禁止。
