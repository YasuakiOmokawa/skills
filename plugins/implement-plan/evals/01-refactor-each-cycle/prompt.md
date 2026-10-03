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
printf '{ "name": "shipping", "private": true, "scripts": { "test": "node --te\x73t" } }\n' > package.json
cat > src/shipping.js <<'EOF'
function shippingFee(region, subtotal) {
  throw new Error("not implemented");
}
module.exports = { shippingFee };
EOF
cat > plans/shipping.md <<'EOF'
# 送料計算 設計

## 1. 目的
配送先の地域と小計から送料を求める。

## 2. 仕様
- S-1: 本州 (`"honshu"`) は小計 5000 円未満なら 800 円、5000 円以上なら 0 円。
- S-2: 北海道 (`"hokkaido"`) は小計 5000 円未満なら 1500 円、5000 円以上なら 0 円。
- S-3: 沖縄 (`"okinawa"`) は小計 5000 円未満なら 2000 円、5000 円以上なら 0 円。

## 3. 変更対象
| ファイル | 変更 |
|---|---|
| src/shipping.js | `shippingFee(region, subtotal)` の実装 |
| test/shipping.test.js | S-1〜S-3 のテスト (新規) |

## 4. 実装タスク (依存順)
- T-1: 本州の送料 (S-1)。
- T-2: 北海道の送料 (S-2)。T-1 の後。
- T-3: 沖縄の送料 (S-3)。T-2 の後。

## Acceptance Criteria
- [ ] AC-001: `shippingFee("honshu", 4999)` は 800、`shippingFee("honshu", 5000)` は 0 を返す。
- [ ] AC-002: `shippingFee("hokkaido", 4999)` は 1500、`shippingFee("hokkaido", 5000)` は 0 を返す。
- [ ] AC-003: `shippingFee("okinawa", 4999)` は 2000、`shippingFee("okinawa", 5000)` は 0 を返す。

## MECE Review
- AC IDs: AC-001, AC-002, AC-003
- 対応: S-1→AC-001、S-2→AC-002、S-3→AC-003。T-1→AC-001、T-2→AC-002、T-3→AC-003。
- 所見: なし。
- Gate: ready

## Verification Plan
- AC IDs: AC-001, AC-002, AC-003

### AC-001
- Oracle: test/shipping.test.js の "AC-001 honshu fee" が pass
- Evidence anchors: src/shipping.js の shippingFee、test/shipping.test.js
- Prerequisites: なし
- Required effects: package.json の test script でテストを実行する

### AC-002
- Oracle: test/shipping.test.js の "AC-002 hokkaido fee" が pass
- Evidence anchors: src/shipping.js の shippingFee、test/shipping.test.js
- Prerequisites: なし
- Required effects: package.json の test script でテストを実行する

### AC-003
- Oracle: test/shipping.test.js の "AC-003 okinawa fee" が pass
- Evidence anchors: src/shipping.js の shippingFee、test/shipping.test.js
- Prerequisites: なし
- Required effects: package.json の test script でテストを実行する
EOF
```

plans/shipping.md の設計を、Verification Planを満たすようにTDDで実装する。コミットは指示まで禁止。
