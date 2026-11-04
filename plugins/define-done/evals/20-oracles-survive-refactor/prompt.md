---
max_turns: 90
timeout_seconds: 2400
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p repo
cd repo
git init -q --template= --separate-git-dir=../repo.gitdir -b main .
mkdir -p src test config docs/adr plans
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

test("/items は一覧を返す", () => {
  assert.equal(handle({ path: "/items", headers: {} }).status, 200);
});
EOF
cat > docs/adr/0005-rate-limit.md <<'EOF'
# ADR-0005 /items の流量制限

- Status: Accepted

## Decision
1. `handle` に届く `/items` の要求は、header `x-client-id` の値ごとに、プロセスの起動から数えて `config/limits.json` の `perMinute` 回までは今と同じ応答を返し、`perMinute + 1` 回目からは status 429 を返す。窓の切り替え (時間で数え直すこと) は別 ADR で決め、この ADR の範囲外とする。
2. 上限値は `config/limits.json` にだけ置き、コードや他の設定に写さない。
3. `/health` は制限の対象外で、応答は今と変わらない。
4. header `x-client-id` の無い `/items` の要求は数えず、今と同じ応答を返す。
5. 上限値はプロセスの起動時に一度だけ読む。`config/limits.json` が読めないときや値が不正なときの扱いは別 ADR で決め、この ADR の範囲外とする。

## Reason
上限を運用で変えるとき、変える場所を 1 か所にするため。
EOF
cat > plans/rate-limit.md <<'EOF'
# /items の流量制限 設計

- 判断の正本: `docs/adr/0005-rate-limit.md`。この設計は ADR の Decision を file の単位に落とす。
- 範囲外: 窓の切り替え (ADR の範囲外)

## 前提
- `src/app.js` の `handle(req)` が全 path の入口で、`test/app.test.js` が `/health` と `/items` の応答を固定している。
- `npm run check` が `test/` の試験を実行する。

## 決めたこと

| # | 決めること | 決定 |
|---|---|---|
| D1 | 上限の読み込み | `src/rate/limit-config.js` を新設し、`readLimitConfig()` が `config/limits.json` を読んで `perMinute` を返す |
| D2 | 数え方 | `src/rate/counter.js` の `createCounter()` が client ごとの回数を `Map` で持つ |
| D3 | 組み込み | `src/app.js` の `handle` で、`/items` のときだけ `checkRate(req)` を先に呼ぶ |
| D4 | health | `src/health.js` は変えない |
EOF
git add -A
git -c user.name=fixture -c user.email=fixture@example.com commit -qm init
cd ..
mkdir -p tools
cat > tools/implement.sh <<'IMPL'
set -e
cd repo
mkdir -p src/throttle
cat > src/throttle/limits.js <<'EOF'
const path = require("node:path");
const fs = require("node:fs");
function loadLimits() {
  return JSON.parse(fs.readFileSync(path.join(__dirname, "../../config/limits.json"), "utf8")).perMinute;
}
module.exports = { loadLimits };
EOF
cat > src/throttle/tally.js <<'EOF'
function makeTally() {
  const counts = new Map();
  return (id) => { const n = (counts.get(id) ?? 0) + 1; counts.set(id, n); return n; };
}
module.exports = { makeTally };
EOF
mkdir -p src/routes
cat > src/routes/health.js <<'EOF'
function health() {
  return { status: 200, body: "ok" };
}

module.exports = { health };
EOF
rm src/health.js
cat > src/app.js <<'EOF'
const { health } = require("./routes/health");
const { loadLimits } = require("./throttle/limits");
const { makeTally } = require("./throttle/tally");

const ITEMS = ["apple", "banana"];
const perMinute = loadLimits();
const tally = makeTally();

function withinLimit(req) {
  const id = req.headers["x-client-id"];
  return id === undefined || tally(id) <= perMinute;
}

function handle(req) {
  if (req.path === "/health") return health();
  if (req.path === "/items") {
    if (!withinLimit(req)) return { status: 429, body: "too many requests" };
    return { status: 200, body: JSON.stringify(ITEMS) };
  }
  return { status: 404, body: "not found" };
}

module.exports = { handle };
EOF
cat > test/throttle.test.js <<'EOF'
const test = require("node:test");
const assert = require("node:assert/strict");
const { perMinute } = require("../config/limits.json");
const { handle } = require("../src/app");
const ok = { status: 200, body: '["apple","banana"]' };
const items = (id) => handle({ path: "/items", headers: { "x-client-id": id } });

test("上限まで 200、超えたら 429 が続く", () => {
  for (let i = 0; i < perMinute; i++) assert.deepEqual(items("a"), ok);
  assert.equal(items("a").status, 429);
  assert.equal(items("a").status, 429);
});
test("別の client は 200", () => { assert.deepEqual(items("b"), ok); });
test("/health は制限されない", () => {
  for (let i = 0; i <= perMinute; i++) assert.deepEqual(handle({ path: "/health", headers: { "x-client-id": "a" } }), { status: 200, body: "ok" });
});
EOF
cat > test/single-limit-source.test.js <<'EOF'
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { perMinute } = require("../config/limits.json");
const root = path.join(__dirname, "..");
const files = (dir) => fs.readdirSync(dir, { withFileTypes: true }).flatMap((e) => e.isDirectory() ? files(path.join(dir, e.name)) : [path.join(dir, e.name)]);

test("上限値は config/limits.json の外に無い", () => {
  const scanned = [...files(path.join(root, "src")), ...files(path.join(root, "config")).filter((f) => !f.endsWith("limits.json")), path.join(root, "package.json")];
  const offenders = scanned.filter((f) => new RegExp(`\\b${perMinute}\\b`).test(fs.readFileSync(f, "utf8")));
  assert.deepEqual(offenders, []);
});
EOF
IMPL
```

この作業ディレクトリで、次を順に行ってください。

1. `repo/plans/rate-limit.md` の設計を /define-done。
2. 1 が終わったら `sh tools/implement.sh` を実行する。これは計画の振る舞いを保ったまま、計画の決定とは別の名前と置き場所で実装し、`/health` の処理も別のファイルへ移す。
3. `repo/plans/rate-limit.md` の `## Verification Plan` の各 Oracle を、書いてあるとおりに `repo` で観測し、AC ごとに結果 (成立した、落ちた、観測できなかった) と理由を 1 行ずつ報告する。計画、製品コード、試験は変えない。Oracle が求める一時的な見本の出し入れはしてよく、終わったら消す。
