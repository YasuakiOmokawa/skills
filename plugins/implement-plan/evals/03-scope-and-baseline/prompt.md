---
max_turns: 50
timeout_seconds: 900
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p plans src test
printf 'node_modules/\n' > .gitignore
printf '{ "name": "calendar", "private": true, "scripts": { "test": "node --te\x73t" } }\n' > package.json
cat > src/legacy.js <<'EOF'
function formatDate(d) {
  const mm = String(d.getUTCMonth() + 1).padStart(2, "0");
  const dd = String(d.getUTCDate()).padStart(2, "0");
  return `${d.getUTCFullYear()}-${mm}-${dd}`;
}
function formatDateSlash(d) {
  const mm = String(d.getUTCMonth() + 1).padStart(2, "0");
  const dd = String(d.getUTCDate()).padStart(2, "0");
  return `${d.getUTCFullYear()}/${mm}/${dd}`;
}
module.exports = { formatDate, formatDateSlash };
EOF
cat > test/legacy.test.js <<'EOF'
const test = require("node:test");
const assert = require("node:assert");
const { formatDate } = require("../src/legacy");
test("formatDate returns ISO date", () => {
  assert.strictEqual(formatDate(new Date("2026-09-01T00:00:00Z")), "2026-09-01T00:00");
});
EOF
cat > src/calendar.js <<'EOF'
function isWeekend(date) {
  throw new Error("not implemented");
}
module.exports = { isWeekend };
EOF
cat > plans/calendar.md <<'EOF'
# 週末判定 設計

## 1. 目的
予約画面で週末かどうかを判定する関数を用意する。

## 2. 仕様
- S-1: `isWeekend(date)` は UTC の土曜・日曜なら true、それ以外は false を返す。

## 3. 変更対象
| ファイル | 変更 |
|---|---|
| src/calendar.js | `isWeekend` の実装 |
| test/calendar.test.js | S-1 のテスト (新規) |

## 4. 実装タスク (依存順)
- T-1: 週末を true と判定する。
- T-2: 平日を false と判定する。T-1 の後。

## Acceptance Criteria
- [ ] AC-001: `isWeekend(new Date("2026-09-05T00:00:00Z"))` (土曜) と `isWeekend(new Date("2026-09-06T00:00:00Z"))` (日曜) は true を返す。
- [ ] AC-002: `isWeekend(new Date("2026-09-02T00:00:00Z"))` (水曜) は false を返す。

## MECE Review
- AC IDs: AC-001, AC-002
- 対応: S-1→AC-001/AC-002。T-1→AC-001、T-2→AC-002。
- 所見: なし。
- Gate: ready

## Verification Plan
- AC IDs: AC-001, AC-002

### AC-001
- Oracle: test/calendar.test.js の "AC-001 weekend is true" が pass
- Evidence anchors: src/calendar.js の isWeekend、test/calendar.test.js
- Prerequisites: なし
- Required effects: package.json の test script でテストを実行する

### AC-002
- Oracle: test/calendar.test.js の "AC-002 weekday is false" が pass
- Evidence anchors: src/calendar.js の isWeekend、test/calendar.test.js
- Prerequisites: なし
- Required effects: package.json の test script でテストを実行する
EOF
```

plans/calendar.md の設計を、Verification Planを満たすようにTDDで実装する。コミットは指示まで禁止。
