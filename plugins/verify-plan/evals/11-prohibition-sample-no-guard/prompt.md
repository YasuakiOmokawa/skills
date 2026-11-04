---
max_turns: 50
timeout_seconds: 1200
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p repo
cd repo
git init -q --template= --separate-git-dir=../repo.gitdir -b main .
mkdir -p src test config plans
printf '{ "name": "items-api", "private": true, "scripts": { "check": "node --te\x73t" } }\n' > package.json
printf '{ "perMinute": 60 }\n' > config/limits.json
cat > src/health.js <<'EOF'
function health() {
  return { status: 200, body: "ok" };
}

module.exports = { health };
EOF
cat > src/app.js <<'EOF'
const { health } = require("./health");

const ITEMS = ["apple", "banana"];

function handle(req) {
  if (req.path === "/health") return health();
  if (req.path === "/items") return { status: 200, body: JSON.stringify(ITEMS) };
  return { status: 404, body: "not found" };
}

module.exports = { handle };
EOF
cat > test/app.test.js <<'EOF'
const test = require("node:test");
const assert = require("node:assert/strict");
const { handle } = require("../src/app");

test("/health は 200 と ok を返す", () => {
  assert.deepEqual(handle({ path: "/health", headers: {} }), { status: 200, body: "ok" });
});
EOF
cat > plans/rate-limit.md <<'EOF'
# /items の流量制限 設計

## 1. 目的
`/items` の要求を client ごとに制限する。上限値は `config/limits.json` にだけ置く。

## Acceptance Criteria
- [ ] AC-001: [振る舞い] 同じ `x-client-id` で `handle` に `/items` を `perMinute` 回 (60 回) 送ると、すべて status 200、61 回目は status 429 を返す
- [ ] AC-002: [振る舞い] `/items` を 61 回送った後も、`handle` に `/health` を送ると status 200 と body `ok` を返す
- [ ] AC-003: [禁止] 上限値を `config/limits.json` の外 (コードや他の設定) に写さない

## MECE Review
- AC IDs: AC-001, AC-002, AC-003
- Gate: ready

## Verification Plan
- AC IDs: AC-001, AC-002, AC-003

### AC-001
- Oracle: `handle` に同じ `x-client-id` の `/items` を 61 回送り、60 回目まで 200、61 回目が 429
- Evidence anchors: `src/app.js` の `handle`、`npm run check`
- Prerequisites: 無い
- Required effects: 無い

### AC-002
- Oracle: AC-001 の後に `handle` に `/health` を送ると `{ status: 200, body: "ok" }`
- Evidence anchors: `src/app.js` の `handle`、`test/app.test.js`
- Prerequisites: 無い
- Required effects: 無い

### AC-003
- Oracle: `npm run check` が通り、Violation sample を入れると落ち、除くと通る
- Evidence anchors: `npm run check`、`config/limits.json`
- Prerequisites: 無い
- Required effects: 無い
- Violation sample: `src/zz-violation.js` に `module.exports = { perMinute: 60 };`
EOF
fp=$(awk '/^## / {f=0} /^## (Acceptance Criteria|Verification Plan)$/ {f=1} f' plans/rate-limit.md | shasum -a 256 | cut -d' ' -f1)
awk -v fp="$fp" '{print} /^- Gate: ready$/{print "- Fingerprint: " fp}' plans/rate-limit.md > plans/rate-limit.md.tmp && mv plans/rate-limit.md.tmp plans/rate-limit.md
git add -A
git -c user.name=fixture -c user.email=fixture@example.com commit -qm init
cat > src/app.js <<'EOF'
const { health } = require("./health");
const { perMinute } = require("../config/limits.json");

const ITEMS = ["apple", "banana"];
const counts = new Map();

function overLimit(clientId) {
  const next = (counts.get(clientId) ?? 0) + 1;
  counts.set(clientId, next);
  return next > perMinute;
}

function handle(req) {
  if (req.path === "/health") return health();
  if (req.path === "/items") {
    if (overLimit(req.headers["x-client-id"])) return { status: 429, body: "too many requests" };
    return { status: 200, body: JSON.stringify(ITEMS) };
  }
  return { status: 404, body: "not found" };
}

module.exports = { handle };
EOF
cat > test/rate.test.js <<'EOF'
const test = require("node:test");
const assert = require("node:assert/strict");
const { handle } = require("../src/app");

test("同じ client の 61 回目は 429、その後も /health は 200", () => {
  const req = { path: "/items", headers: { "x-client-id": "c1" } };
  for (let i = 0; i < 60; i++) assert.equal(handle(req).status, 200);
  assert.equal(handle(req).status, 429);
  assert.deepEqual(handle({ path: "/health", headers: {} }), { status: 200, body: "ok" });
});
EOF
```

`repo/plans/rate-limit.md` の実装は `repo` の working tree に済んでいる (未 commit)。最後に /verify-plan を実行。コミットは指示まで禁止。
