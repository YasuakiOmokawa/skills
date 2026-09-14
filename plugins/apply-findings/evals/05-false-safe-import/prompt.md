---
max_turns: 30
timeout_seconds: 600
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p src test
cat > src/polyfill.js <<'EOF'
if (typeof globalThis.__polyfilled === "undefined") {
  globalThis.__polyfilled = true;
  if (!Array.prototype.at) {
    Array.prototype.at = function (i) { return this[i < 0 ? this.length + i : i]; };
  }
}
EOF
cat > src/format.js <<'EOF'
function formatDate(d) { return d.toISOString().slice(0, 10); }
module.exports = { formatDate };
EOF
cat > src/order.js <<'EOF'
function parseOrder(input) { return { items: input.split(",").map((s) => s.trim()) }; }
module.exports = { parseOrder };
EOF
cat > src/app.js <<'EOF'
require("./polyfill");
const { formatDate } = require("./format");
const { parseOrder } = require("./order");

function run(input) {
  return parseOrder(input).items.at(-1);
}

module.exports = { run };
EOF
cat > test/app.test.js <<'EOF'
const assert = require("node:assert");
const { run } = require("../src/app");
assert.strictEqual(globalThis.__polyfilled, true, "app must register the polyfill");
assert.strictEqual(run("a, b, c"), "c");
console.log("app.test: 2 passed");
EOF
```

テストは `node test/app.test.js` で走ります。

直前の /code-review medium の出力:

| # | 位置 | 指摘 | reviewer の分類 |
|---|---|---|---|
| 1 | src/app.js:1 | `require("./polyfill")` は戻り値を使っていない未使用 import。削除 | 機械的に安全 |
| 2 | src/app.js:2 | `formatDate` は未使用。削除 | 機械的に安全 |

=> /apply-findings を実行。
