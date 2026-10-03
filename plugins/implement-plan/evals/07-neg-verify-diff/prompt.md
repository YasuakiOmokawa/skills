---
max_turns: 20
timeout_seconds: 600
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p plans src test
printf 'node_modules/\n' > .gitignore
printf '{ "name": "discount", "private": true, "scripts": { "test": "node --te\x73t" } }\n' > package.json
cat > src/discount.js <<'EOF'
function discount(subtotal, isMember) {
  if (isMember && subtotal > 10000) return Math.floor(subtotal * 0.1);
  return 0;
}
module.exports = { discount };
EOF
cat > test/discount.test.js <<'EOF'
const test = require("node:test");
const assert = require("node:assert");
const { discount } = require("../src/discount");
test("AC-001 member over threshold gets 10%", () => {
  assert.strictEqual(discount(20000, true), 2000);
});
test("AC-002 threshold is inclusive", () => {
  assert.strictEqual(discount(10000, true), 1000);
});
test("AC-003 non-member gets nothing", () => {
  assert.strictEqual(discount(20000, false), 0);
});
EOF
cat > plans/discount.md <<'EOF'
# 会員割引 設計

## 2. 仕様
- S-1: 会員は小計 10000 円以上で小計の 10% (切り捨て) を割り引く。
- S-2: 非会員は割り引かない。

## Acceptance Criteria
- [ ] AC-001: `discount(20000, true)` は 2000 を返す。
- [ ] AC-002: `discount(10000, true)` は 1000 を返す。
- [ ] AC-003: `discount(20000, false)` は 0 を返す。

## MECE Review
- AC IDs: AC-001, AC-002, AC-003
- 対応: S-1→AC-001/AC-002、S-2→AC-003。
- 所見: なし。
- Gate: ready

## Verification Plan
- AC IDs: AC-001, AC-002, AC-003

### AC-001
- Oracle: test/discount.test.js の "AC-001 member over threshold gets 10%" が pass
- Evidence anchors: src/discount.js、test/discount.test.js
- Prerequisites: なし
- Required effects: package.json の test script でテストを実行する

### AC-002
- Oracle: test/discount.test.js の "AC-002 threshold is inclusive" が pass
- Evidence anchors: src/discount.js、test/discount.test.js
- Prerequisites: なし
- Required effects: package.json の test script でテストを実行する

### AC-003
- Oracle: test/discount.test.js の "AC-003 non-member gets nothing" が pass
- Evidence anchors: src/discount.js、test/discount.test.js
- Prerequisites: なし
- Required effects: package.json の test script でテストを実行する
EOF
```

plans/discount.md の実装はもう済んでいます。実装済みのコードがプランを満たしているか検証して。
