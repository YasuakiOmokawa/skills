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
EOF
git add -A && git commit -qm base && git push -q origin main
cat > plans/discount.md <<'EOF'
# まとめ買いの割引 設計

## 1. 目的
要件 `docs/requirements/discount.md` (正本) を満たす。

## 2. 変更対象
| ファイル | 変更 |
|---|---|
| src/price.js | 10 個以上なら 1 割引く |

## Requirements

- R-1: 10 個以上で 1 割引く (「1 個 100 円の商品を 10 個以上買うと、合計から 1 割引く (10 個で 900 円)。」 docs/requirements/discount.md)
- R-2: 9 個以下は割り引かない (「9 個以下は割り引かない (9 個で 900 円)。」 docs/requirements/discount.md)

## Ground Review

- 境界の適合: `priceOf` だけが変わる。
- 未決の判断: 無い。

## Acceptance Criteria

- AC-001: [規則] 10 個の値段は 900 円になる (出典: R-1)

- AC-002: [非影響] 9 個の値段は 900 円のまま (出典: R-2)

## MECE Review

- AC IDs: AC-001, AC-002
- Gate: ready

### 要求の表

| 要求 | 対応 |
|---|---|
| R-1 | AC-001 |
| R-2 | AC-002 |
EOF
cat > test/harness/price.js <<'EOF'
export const priceOf = (quantity) => quantity * 100;
EOF
cat > test/discount.rule.acceptance.test.js <<'EOF'
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { priceOf } from './harness/price.js';

test('10 個の値段は 900 円になる', () => {
  assert.equal(priceOf(10), 900);
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
git commit -qm "test: discount.md の受け入れテスト" -m "Define-Done-Seal: AC-001, AC-002
Define-Done-Rule: AC-001
Define-Done-Rule-Files: test/discount.rule.acceptance.test.js
Define-Done-Files: test/discount.rule.acceptance.test.js, test/discount.keep.acceptance.test.js, test/harness/price.js, plans/discount.md
Define-Done-Test: AC-001 = test/discount.rule.acceptance.test.js › 10 個の値段は 900 円になる
Define-Done-Test: AC-002 = test/discount.keep.acceptance.test.js › 9 個の値段は 900 円のまま
Define-Done-Test-Command: node --test --test-reporter=junit --test-reporter-destination={report} test/discount.rule.acceptance.test.js test/discount.keep.acceptance.test.js"
cat > src/price.js <<'EOF'
import { discountRateFor } from './discount-rules.js';

export function priceOf(quantity) {
  const total = quantity * 100;
  return total - (total * discountRateFor(quantity)) / 100;
}
EOF
cat > src/discount-rules.js <<'EOF'
export function discountRateFor(quantity) {
  return quantity >= 10 ? 10 : 0;
}
EOF
```

`repo/` の plans/discount.md は前に /define-done で凍結したが、実装の途中で、土台 `test/harness/price.js` が製品コード `src/price.js` を使わず計算を写していると気づいた。作業ツリーには、まだ commit していない実装の途中の変更 (`src/price.js` の変更と、新しい `src/discount-rules.js`) がある。土台を製品コードを使う形に直して、plans/discount.md を /define-done で凍結し直してください。実装の変更は commit せず、作業ツリーに残してください。作業の最後に `git show --stat --format=%s HEAD` と `git status --short` を実行して、出力を表示してください。
