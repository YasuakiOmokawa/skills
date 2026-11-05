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
printf '{ "name": "slug", "private": true, "scripts": { "test": "node --te\x73t" } }\n' > package.json
cat > src/slug.js <<'EOF'
module.exports = {};
EOF
cat > plans/slug.md <<'EOF'
# URL スラッグ生成 設計

## 1. 目的
記事タイトルから URL 用のスラッグを作る。

## 2. 仕様
- S-1: `toSlug(title)` は英字を小文字にし、空白をハイフンにする。
- S-2: 英数字・空白以外の記号は取り除き、連続するハイフンは 1 つにまとめる。

## 3. 変更対象
| ファイル | 変更 |
|---|---|
| src/slug.js | `toSlug` を新規 export |
| test/slug.test.js | S-1、S-2 のテスト (新規) |

## 4. 実装タスク (依存順)
- T-1: 小文字化と空白の置換 (S-1)。
- T-2: 記号の除去 (S-2)。T-1 の後。

## Requirements
- R-1: 小文字化とハイフン (「`toSlug(title)` は英字を小文字にし、空白をハイフンにする。」 計画:2. 仕様)
- R-2: 記号の除去 (「英数字・空白以外の記号は取り除き、連続するハイフンは 1 つにまとめる。」 計画:2. 仕様)

## Ground Review
- 境界の適合: 変更対象の外の責務と信頼境界を動かさない。
- 前提の確認: 依存先の振る舞いに頼る決定は無い。

## Acceptance Criteria
- [ ] AC-001: [振る舞い] `toSlug("Hello World")` は `"hello-world"` を返す (出典: R-1)
- [ ] AC-002: [振る舞い] `toSlug("Rock & Roll!")` は `"rock-roll"` を返す (出典: R-2)

## MECE Review
- AC IDs: AC-001, AC-002
- 対応: R-1→AC-001、R-2→AC-002。
- 所見: なし。
- Gate: ready

## Verification Plan
- AC IDs: AC-001, AC-002

### AC-001
- Oracle: test/slug.test.js の "AC-001 lowercases and hyphenates" が pass
- Evidence anchors: src/slug.js の toSlug、test/slug.test.js
- Prerequisites: なし
- Required effects: package.json の test script でテストを実行する

### AC-002
- Oracle: test/slug.test.js の "AC-002 strips symbols" が pass
- Evidence anchors: src/slug.js の toSlug、test/slug.test.js
- Prerequisites: なし
- Required effects: package.json の test script でテストを実行する
EOF
python3 - plans/slug.md <<'PY'
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

plans/slug.md を実装して。
