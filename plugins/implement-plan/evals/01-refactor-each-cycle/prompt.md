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

## Requirements
- R-1: 本州の送料 (「本州 (`"honshu"`) は小計 5000 円未満なら 800 円、5000 円以上なら 0 円。」 計画:2. 仕様)
- R-2: 北海道の送料 (「北海道 (`"hokkaido"`) は小計 5000 円未満なら 1500 円、5000 円以上なら 0 円。」 計画:2. 仕様)
- R-3: 沖縄の送料 (「沖縄 (`"okinawa"`) は小計 5000 円未満なら 2000 円、5000 円以上なら 0 円。」 計画:2. 仕様)

## Ground Review
- 境界の適合: 変更対象の外の責務と信頼境界を動かさない。
- 前提の確認: 依存先の振る舞いに頼る決定は無い。

## Acceptance Criteria
- [ ] AC-001: [振る舞い] `shippingFee("honshu", 4999)` は 800、`shippingFee("honshu", 5000)` は 0 を返す (出典: R-1)
- [ ] AC-002: [振る舞い] `shippingFee("hokkaido", 4999)` は 1500、`shippingFee("hokkaido", 5000)` は 0 を返す (出典: R-2)
- [ ] AC-003: [振る舞い] `shippingFee("okinawa", 4999)` は 2000、`shippingFee("okinawa", 5000)` は 0 を返す (出典: R-3)

## MECE Review
- AC IDs: AC-001, AC-002, AC-003
- 対応: R-1→AC-001、R-2→AC-002、R-3→AC-003。
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
python3 - plans/shipping.md <<'PY'
import hashlib, sys
path = sys.argv[1]
lines = open(path, encoding="utf-8").read().splitlines(keepends=True)
def section(name):
    start = next(i for i, l in enumerate(lines) if l.rstrip("\n") == "## " + name)
    end = next((j for j in range(start + 1, len(lines)) if lines[j].startswith("## ")), len(lines))
    return "".join(lines[start:end])
fp = hashlib.sha256("".join(section(n) for n in ("Requirements", "Acceptance Criteria", "Verification Plan")).encode()).hexdigest()
out = []
for l in lines:
    out.append(l)
    if l.rstrip("\n") == "- Gate: ready":
        out.append(f"- Fingerprint: {fp}\n")
open(path, "w", encoding="utf-8").write("".join(out))
PY
```

plans/shipping.md の設計を、Verification Planを満たすようにTDDで実装する。コミットは指示まで禁止。
