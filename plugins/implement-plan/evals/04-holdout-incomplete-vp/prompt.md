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

## Requirements
- R-1: truncate (「`truncate(s, n)` は `s` が `n` 文字を超えるとき先頭 `n` 文字に `…` を付ける。」 計画:2. 仕様)
- R-2: capitalize (「`capitalize(s)` は先頭 1 文字を大文字にする。」 計画:2. 仕様)
- R-3: countWords (「`countWords(s)` は空白区切りの語数を返す。」 計画:2. 仕様)
- R-4: reverseWords (「`reverseWords(s)` は空白区切りの語順を逆にする。」 計画:2. 仕様)

## Ground Review
- 境界の適合: 変更対象の外の責務と信頼境界を動かさない。
- 前提の確認: 依存先の振る舞いに頼る決定は無い。

## Acceptance Criteria
- [ ] AC-001: [振る舞い] `truncate("abcdef", 3)` は `"abc…"`、`truncate("ab", 3)` は `"ab"` を返す (出典: R-1)
- [ ] AC-002: [振る舞い] `capitalize("hello")` は `"Hello"` を返す (出典: R-2)
- [ ] AC-003: [振る舞い] `countWords("a b  c")` は 3 を返す (出典: R-3)
- [ ] AC-004: [振る舞い] `reverseWords("a b c")` は `"c b a"` を返す (出典: R-4)

## MECE Review
- AC IDs: AC-001, AC-002, AC-003, AC-004
- 対応: R-1→AC-001、R-2→AC-002、R-3→AC-003、R-4→AC-004。
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
python3 - plans/text.md <<'PY'
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

plans/text.md を実装して。
