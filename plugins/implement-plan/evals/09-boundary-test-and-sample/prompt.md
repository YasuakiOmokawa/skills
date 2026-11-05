---
max_turns: 60
timeout_seconds: 1500
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p repo
cd repo
git init -q --template= --separate-git-dir=../repo.gitdir -b main .
mkdir -p src test plans
printf '{ "name": "items-api", "version": "1.4.2", "private": true, "scripts": { "check": "node --te\x73t" } }\n' > package.json
cat > src/app.js <<'EOF'
function handle(req) {
  if (req.path === "/health") return { status: 200, body: "ok" };
  return { status: 404, body: "not found" };
}

module.exports = { handle };
EOF
cat > test/app.test.js <<'EOF'
const test = require("node:test");
const assert = require("node:assert/strict");
const { handle } = require("../src/app");

test("/health は 200 と ok を返す", () => {
  assert.deepEqual(handle({ path: "/health" }), { status: 200, body: "ok" });
});
EOF
cat > plans/version.md <<'EOF'
# /version を足す 設計

## 1. 目的
運用者が動いている版を `/version` で確かめられるようにする。版の値は `package.json` の `version` にだけ置く。

## 決めたこと
| # | 決めること | 決定 |
|---|---|---|
| D1 | 版の読み込み | `src/version-info.js` を新設し、`readVersion()` が `package.json` の `version` を返す |
| D2 | 組み込み | `src/app.js` の `handle` で `/version` のとき `readVersion()` の値を返す |

## 作業項目
- W-1: D1 と D2 を実装する (AC-001、AC-002)。

## Requirements
- R-1: 運用者が版を `/version` で確かめられる (「運用者が動いている版を `/version` で確かめられるようにする。」 計画:1. 目的)
- R-2: 版の値は `package.json` にだけ置く (「版の値は `package.json` の `version` にだけ置く。」 計画:1. 目的)

## Ground Review
- 境界の適合: `handle` に経路を 1 つ足すだけで、既存の `/health` の応答と責務を動かさない。
- 前提の確認: 依存先の振る舞いに頼る決定は無い。

## Acceptance Criteria
- [ ] AC-001: [振る舞い] `handle` に `/version` を送ると、status 200 と、body に `package.json` の `version` の値を返す (出典: R-1)
- [ ] AC-002: [禁止] 版の値をコード (`src/`) に写さない (出典: R-2)

## MECE Review
- AC IDs: AC-001, AC-002
- 対応: R-1→AC-001、R-2→AC-002。
- Gate: ready

| 決定 | 要求 |
|---|---|
| D1 | R-1, R-2 |
| D2 | R-1 |

## Verification Plan
- AC IDs: AC-001, AC-002

### AC-001
- Oracle: `handle({ path: "/version" })` が `{ status: 200, body: "1.4.2" }`
- Evidence anchors: `src/app.js` の `handle`、`test/app.test.js`
- Prerequisites: 無い
- Required effects: 無い

### AC-002
- Oracle: check_plan.py の禁止の検査が通り、Violation sample を入れると落ち、除くと通る
- Evidence anchors: `package.json`
- Prerequisites: 無い
- Required effects: 無い
- Violation sample: `src/zz-violation.js` に `module.exports = "1.4.2";`
- Forbidden row: {"pattern": "1\\.4\\.2", "pathspec": ["src"]}
EOF
python3 - plans/version.md <<'PY'
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
git add -A
git -c user.name=fixture -c user.email=fixture@example.com commit -qm init
```

`repo/plans/version.md` を実装して。コミットは指示まで禁止。
