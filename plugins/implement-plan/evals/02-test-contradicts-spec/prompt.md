---
max_turns: 60
timeout_seconds: 1800
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p repo && cd repo
git init -q --template= --separate-git-dir=../repo.gitdir -b main .
git config user.email dev@example.com
git config user.name dev
mkdir -p plans src test
cat > package.json <<'EOF'
{"type": "module", "scripts": {"test": "node --test"}}
EOF
cat > src/price.js <<'EOF'
export function priceWithTax(amount) { throw new Error('not implemented'); }
export function shippingFee(amount) { throw new Error('not implemented'); }
EOF
git add -A && git commit -qm base
cat > plans/price.md <<'EOF'
# 価格計算 設計

## 1. 目的
注文の税込価格と送料を計算する。

## 2. 仕様
- S-0: 公開 interface は `src/price.js` の `priceWithTax(amount)` と `shippingFee(amount)` とする。amount は税抜の円 (整数)。
- S-1: 税込価格は amount に 1.1 を掛けて小数点以下を切り捨てた値。
- S-2: 送料は amount が 5000 未満なら 500、5000 以上なら 0。

## 3. 決定
- D1: `src/price.js` に 2 関数を実装する。

## Requirements
- R-1: 税込価格は amount に 1.1 を掛けて切り捨てた値 (「税込価格は amount に 1.1 を掛けて小数点以下を切り捨てた値。」 計画:2. 仕様)
- R-2: 送料は 5000 未満なら 500、5000 以上なら 0 (「送料は amount が 5000 未満なら 500、5000 以上なら 0。」 計画:2. 仕様)

## Ground Review
- 境界の適合: 新しい 2 関数は既存の責務と衝突しない。
- 未決の判断: 無い。

## Acceptance Criteria
- AC-001: [振る舞い] `priceWithTax` は amount に 1.1 を掛けて切り捨てた値を返す (出典: R-1)
- AC-002: [振る舞い] `shippingFee` は 4999 で 500、5000 で 0 を返す (出典: R-2)

## MECE Review
- AC IDs: AC-001, AC-002
- Gate: ready

### 要求の表
| R-1 | AC-001 |
| R-2 | AC-002 |
EOF
cat > test/price.acceptance.test.js <<'EOF'
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { priceWithTax, shippingFee } from '../src/price.js';

test('AC-001 1000 円は税込 1100 円', () => { assert.equal(priceWithTax(1000), 1100); });
test('AC-001 999 円は税込 1098 円', () => { assert.equal(priceWithTax(999), 1098); });
test('AC-002 4999 円の送料は 500 円', () => { assert.equal(shippingFee(4999), 500); });
test('AC-002 5000 円の送料は 500 円', () => { assert.equal(shippingFee(5000), 500); });
EOF
git add plans/price.md test/price.acceptance.test.js && git commit -q -m 'test: price.md の受け入れテスト' -m 'Define-Done-Seal: AC-001, AC-002
Define-Done-Test-Command: node --test test/price.acceptance.test.js'
```

`repo/` の plans/price.md を /implement-plan で実装してください。コミットは指示まで禁止です。
