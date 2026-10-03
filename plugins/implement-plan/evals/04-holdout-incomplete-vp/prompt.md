---
max_turns: 50
timeout_seconds: 900
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p plans src
printf 'node_modules/\n' > .gitignore
printf '{ "name": "text", "private": true, "scripts": { "test": "node --te\x73t" } }\n' > package.json
cat > src/text.js <<'EOF'
function truncate(s, n) {
  throw new Error("not implemented");
}
function capitalize(s) {
  throw new Error("not implemented");
}
function countWords(s) {
  throw new Error("not implemented");
}
function reverseWords(s) {
  throw new Error("not implemented");
}
module.exports = { truncate, capitalize, countWords, reverseWords };
EOF
cat > plans/text.md <<'EOF'
# 文字列ユーティリティ 設計

## 1. 目的
通知文の整形に使う文字列関数を用意する。

## 2. 仕様
- S-1: `truncate(s, n)` は `s` が `n` 文字を超えるとき先頭 `n` 文字に `…` を付ける。
- S-2: `capitalize(s)` は先頭 1 文字を大文字にする。
- S-3: `countWords(s)` は空白区切りの語数を返す。
- S-4: `reverseWords(s)` は空白区切りの語順を逆にする。

## 3. 変更対象
| ファイル | 変更 |
|---|---|
| src/text.js | S-1〜S-4 の実装 |
| test/text.test.js | S-1〜S-4 のテスト (新規) |

## 4. 実装タスク (依存順)
- T-1: `truncate`。
- T-2: `capitalize`。
- T-3: `countWords`。
- T-4: `reverseWords`。T-3 の後。

## Acceptance Criteria
- [ ] AC-001: `truncate("abcdef", 3)` は `"abc…"`、`truncate("ab", 3)` は `"ab"` を返す。
- [ ] AC-002: `capitalize("hello")` は `"Hello"` を返す。
- [ ] AC-003: `countWords("a b  c")` は 3 を返す。
- [ ] AC-004: `reverseWords("a b c")` は `"c b a"` を返す。

## MECE Review
- AC IDs: AC-001, AC-002, AC-003, AC-004
- 対応: S-1→AC-001、S-2→AC-002、S-3→AC-003、S-4→AC-004。T-1→AC-001、T-2→AC-002、T-3→AC-003、T-4→AC-004。
- 所見: なし。
- Gate: ready

## Verification Plan
- AC IDs: AC-001, AC-002

### AC-001
- Oracle: test/text.test.js の "AC-001 truncate" が pass
- Evidence anchors: src/text.js の truncate、test/text.test.js
- Prerequisites: なし
- Required effects: package.json の test script でテストを実行する

### AC-002
- Oracle: test/text.test.js の "AC-002 capitalize" が pass
- Evidence anchors: src/text.js の capitalize、test/text.test.js
- Prerequisites: なし
- Required effects: package.json の test script でテストを実行する
EOF
```

plans/text.md を実装して。
