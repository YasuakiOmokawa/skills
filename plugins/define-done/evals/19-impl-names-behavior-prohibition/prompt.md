---
max_turns: 60
timeout_seconds: 1800
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
```

`repo/plans/rate-limit.md` の設計を /define-done。
