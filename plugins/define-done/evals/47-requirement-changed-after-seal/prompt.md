---
max_turns: 80
timeout_seconds: 2400
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
git init -q --bare --template= remote.git
mkdir -p repo && cd repo
git init -q --template= --separate-git-dir=../repo.gitdir -b main .
git config user.email dev@example.com
git config user.name dev
git remote add origin ../remote.git
mkdir -p plans src test/harness docs/requirements
cat > package.json <<'EOF'
{"type": "module", "scripts": {"test": "node --test"}}
EOF
cat > src/price.js <<'EOF'
export function priceOf(quantity) {
  return quantity * 100;
}
EOF
cat > docs/requirements/discount.md <<'EOF'
# まとめ買いの割引

- 1 個 100 円の商品を 10 個以上買うと、合計から 1 割引く (10 個で 900 円)。
- 9 個以下は割り引かない (9 個で 900 円)。
- 100 個以上買うと、合計から 2 割引く (100 個で 8,000 円)。
EOF
git add -A && git commit -qm base && git push -q origin main
cat > plans/discount.md <<'EOF'
# まとめ買いの割引 設計

## 1. 目的
要件 `docs/requirements/discount.md` (正本) を満たす。

## 2. 変更対象
| ファイル | 変更 |
|---|---|
| src/price.js | 10 個以上なら 1 割、100 個以上なら 2 割引く |

## Requirements

- R-1: 10 個以上で 1 割引く (「1 個 100 円の商品を 10 個以上買うと、合計から 1 割引く (10 個で 900 円)。」 docs/requirements/discount.md)
- R-2: 9 個以下は割り引かない (「9 個以下は割り引かない (9 個で 900 円)。」 docs/requirements/discount.md)
- R-3: 100 個以上で 2 割引く (「100 個以上買うと、合計から 2 割引く (100 個で 8,000 円)。」 docs/requirements/discount.md)

## Ground Review

- 境界の適合: `priceOf` だけが変わる。

### 未決の判断

- 無い

### 未検証の結論

- 無い

## Acceptance Criteria

- AC-001: [規則] 10 個の値段は 900 円になる (出典: R-1)

- AC-002: [非影響] 9 個の値段は 900 円のまま (出典: R-2)

- AC-003: [規則] 100 個の値段は 8,000 円になる (出典: R-3)

## MECE Review

- AC IDs: AC-001, AC-002, AC-003
- Gate: ready

### 要求の表

| 要求 | 対応 |
|---|---|
| R-1 | AC-001 |
| R-2 | AC-002 |
| R-3 | AC-003 |
EOF
cat > test/harness/price.js <<'EOF'
export { priceOf } from '../../src/price.js';
EOF
cat > test/discount.rule.acceptance.test.js <<'EOF'
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { priceOf } from './harness/price.js';

test('10 個の値段は 900 円になる', () => {
  assert.equal(priceOf(10), 900);
});

test('100 個の値段は 8,000 円になる', () => {
  assert.equal(priceOf(100), 8000);
});
EOF
cat > test/discount.keep.acceptance.test.js <<'EOF'
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { priceOf } from './harness/price.js';

test('9 個の値段は 900 円のまま', () => {
  assert.equal(priceOf(9), 900);
});
EOF
git add plans/discount.md test/harness/price.js test/discount.rule.acceptance.test.js test/discount.keep.acceptance.test.js
git commit -qm "test: plans/discount.md の受け入れテスト" -m "Define-Done-Seal: AC-001, AC-002, AC-003
Define-Done-Rule: AC-001, AC-003
Define-Done-Rule-Files: test/discount.rule.acceptance.test.js
Define-Done-Files: test/discount.rule.acceptance.test.js, test/discount.keep.acceptance.test.js, test/harness/price.js, plans/discount.md
Define-Done-Test: AC-001 = test/discount.rule.acceptance.test.js › 10 個の値段は 900 円になる
Define-Done-Test: AC-002 = test/discount.keep.acceptance.test.js › 9 個の値段は 900 円のまま
Define-Done-Test: AC-003 = test/discount.rule.acceptance.test.js › 100 個の値段は 8,000 円になる
Define-Done-Test-Command: node --test --test-reporter=junit --test-reporter-destination={report} test/discount.rule.acceptance.test.js test/discount.keep.acceptance.test.js
Define-Done-Plan: plans/discount.md
Define-Done-Criteria: AC-001=de58a60277, AC-002=963eee75ab, AC-003=dfd0f198ce
Define-Done-Requirements: R-1=e3893c4718, R-2=a773ba7b84, R-3=cd08919b05"
sed -i.bak -e 's/^要件 `docs\/requirements\/discount.md` (正本) を満たす。$/要件 `docs\/requirements\/discount.md` (正本) を、受け入れテストを書いた後に依頼が変えた 2 点を除いて満たす。/' -e 's/10 個以上なら 1 割、100 個以上なら 2 割引く/10 個以上なら 15% 引く/' plans/discount.md && rm plans/discount.md.bak
git status --short
```

`repo/` の plans/discount.md は、前に /define-done で受け入れテストを書いて commit した (実装はまだ始めていない)。その後、要求を 2 つ変えることにした。

1. 100 個以上の 2 割引はやめる。
2. 10 個以上の割引は、1 割ではなく 15% にする (10 個で 850 円)。

計画の「1. 目的」と「2. 変更対象」は、この変更に合わせて直してある (未 commit)。要件の文書 docs/requirements/discount.md は後で自分が直すので、触らないでほしい。plans/discount.md と受け入れテストを /define-done で、この変更に合わせて直してください。
