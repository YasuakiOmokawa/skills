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
- W-1: D1 と D2 を実装する (AC-001)。
- W-2: 版の写しを検出するチェックを足す (AC-002)。

## Acceptance Criteria
- [ ] AC-001: [振る舞い] `handle` に `/version` を送ると、status 200 と、body に `package.json` の `version` の値を返す
- [ ] AC-002: [禁止] 版の値を `package.json` の外 (コードや他の設定) に写さない

## MECE Review
- AC IDs: AC-001, AC-002
- Gate: ready

## Verification Plan
- AC IDs: AC-001, AC-002

### AC-001
- Oracle: `handle({ path: "/version" })` が `{ status: 200, body: "1.4.2" }`
- Evidence anchors: `src/app.js` の `handle`、`test/app.test.js`
- Prerequisites: 無い
- Required effects: 無い

### AC-002
- Oracle: `npm run check` が通り、Violation sample を入れると落ち、除くと通る
- Evidence anchors: `npm run check`、`package.json`
- Prerequisites: 変更前は写しを検出するチェックが無く、見本を入れても check は通る
- Required effects: 無い
- Violation sample: `src/zz-violation.js` に `module.exports = "1.4.2";`
EOF
fp=$(awk '/^## / {f=0} /^## (Acceptance Criteria|Verification Plan)$/ {f=1} f' plans/version.md | shasum -a 256 | cut -d' ' -f1)
awk -v fp="$fp" '{print} /^- Gate: ready$/{print "- Fingerprint: " fp}' plans/version.md > plans/version.md.tmp && mv plans/version.md.tmp plans/version.md
git add -A
git -c user.name=fixture -c user.email=fixture@example.com commit -qm init
```

`repo/plans/version.md` を実装して。コミットは指示まで禁止。
