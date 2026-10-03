---
max_turns: 20
timeout_seconds: 600
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p plans src
printf 'node_modules/\n' > .gitignore
printf '{ "name": "stock", "private": true, "scripts": { "test": "node --te\x73t" } }\n' > package.json
cat > src/stock.js <<'EOF'
function reserve(stock, qty) {
  throw new Error("not implemented");
}
function release(stock, qty) {
  throw new Error("not implemented");
}
module.exports = { reserve, release };
EOF
cat > plans/stock.md <<'EOF'
# 在庫引当 設計

## 2. 仕様
- S-1: `reserve(stock, qty)` は `{ available, reserved }` の available から qty を引き reserved に足した新しい値を返す。available が qty 未満なら `Error("insufficient")` を投げる。
- S-2: `release(stock, qty)` は reserved から qty を引き available に戻した新しい値を返す。

## 3. 変更対象
| ファイル | 変更 |
|---|---|
| src/stock.js | S-1、S-2 の実装 |
| test/stock.test.js | S-1、S-2 のテスト (新規) |

## 4. 実装タスク (依存順)
- T-1: `reserve`。
- T-2: `release`。T-1 の後。

## Acceptance Criteria
- [ ] AC-001: `reserve({ available: 5, reserved: 0 }, 2)` は `{ available: 3, reserved: 2 }` を返す。
- [ ] AC-002: `reserve({ available: 1, reserved: 0 }, 2)` は `Error("insufficient")` を投げる。
- [ ] AC-003: `release({ available: 3, reserved: 2 }, 2)` は `{ available: 5, reserved: 0 }` を返す。

## MECE Review
- AC IDs: AC-001, AC-002, AC-003
- 対応: S-1→AC-001/AC-002、S-2→AC-003。T-1→AC-001/AC-002、T-2→AC-003。
- 所見: なし。
- Gate: ready
EOF
```

plans/stock.md の実装前に、Verification Plan を作って plan に追記して。
