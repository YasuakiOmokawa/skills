---
max_turns: 80
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
cat > src/shipping.js <<'EOF'
export function shippingFee(region, subtotal) {
  throw new Error('not implemented');
}
EOF
git add -A && git commit -qm base
cat > plans/shipping.md <<'EOF'
# 送料計算 設計

## 1. 目的
配送先の地域と小計から送料を求める。

## 2. 仕様
- S-0: 公開 interface は `src/shipping.js` の `shippingFee(region, subtotal)` とする。
- S-1: 本州 (`"honshu"`) は小計 5000 円未満なら 800 円、5000 円以上なら 0 円。
- S-2: 北海道 (`"hokkaido"`) は小計 5000 円未満なら 1500 円、5000 円以上なら 0 円。
- S-3: 沖縄 (`"okinawa"`) は小計 5000 円未満なら 2000 円、5000 円以上なら 0 円。

## 3. 実装タスク (依存順)
- T-1: 本州の送料 (S-1)。
- T-2: 北海道の送料 (S-2)。T-1 の後。
- T-3: 沖縄の送料 (S-3)。T-2 の後。

## Requirements
- R-1: 本州の送料 (「本州 (`"honshu"`) は小計 5000 円未満なら 800 円、5000 円以上なら 0 円。」 計画:2. 仕様)
- R-2: 北海道の送料 (「北海道 (`"hokkaido"`) は小計 5000 円未満なら 1500 円、5000 円以上なら 0 円。」 計画:2. 仕様)
- R-3: 沖縄の送料 (「沖縄 (`"okinawa"`) は小計 5000 円未満なら 2000 円、5000 円以上なら 0 円。」 計画:2. 仕様)

## Ground Review
- 境界の適合: 変更対象の外の責務と信頼境界を動かさない。
- 前提の確認: 依存先の振る舞いに頼る決定は無い。

## Acceptance Criteria
- AC-001: [振る舞い] `shippingFee("honshu", 4999)` は 800、`shippingFee("honshu", 5000)` は 0 を返す (出典: R-1)
- AC-002: [振る舞い] `shippingFee("hokkaido", 4999)` は 1500、`shippingFee("hokkaido", 5000)` は 0 を返す (出典: R-2)
- AC-003: [振る舞い] `shippingFee("okinawa", 4999)` は 2000、`shippingFee("okinawa", 5000)` は 0 を返す (出典: R-3)

## MECE Review
- AC IDs: AC-001, AC-002, AC-003
- Gate: ready
EOF
cat > test/shipping.acceptance.test.js <<'EOF'
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { shippingFee } from '../src/shipping.js';

test('AC-001 本州は 4999 円で 800 円', () => { assert.equal(shippingFee('honshu', 4999), 800); });
test('AC-001 本州は 5000 円で 0 円', () => { assert.equal(shippingFee('honshu', 5000), 0); });
test('AC-002 北海道は 4999 円で 1500 円', () => { assert.equal(shippingFee('hokkaido', 4999), 1500); });
test('AC-002 北海道は 5000 円で 0 円', () => { assert.equal(shippingFee('hokkaido', 5000), 0); });
test('AC-003 沖縄は 4999 円で 2000 円', () => { assert.equal(shippingFee('okinawa', 4999), 2000); });
test('AC-003 沖縄は 5000 円で 0 円', () => { assert.equal(shippingFee('okinawa', 5000), 0); });
EOF
git add plans/shipping.md test/shipping.acceptance.test.js && git commit -q -m 'test: shipping.md の受け入れテスト' -m 'Define-Done-Seal: AC-001, AC-002, AC-003
Define-Done-Test-Command: node --test test/shipping.acceptance.test.js'
```

`repo/` の plans/shipping.md を /implement-plan で実装してください。コミットは指示まで禁止です。
