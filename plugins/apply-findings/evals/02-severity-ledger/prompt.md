---
max_turns: 30
timeout_seconds: 600
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p src test
cat > src/labels.js <<'EOF'
const recieveLabel = "受領";

function labelFor(kind) {
  return kind === "receive" ? recieveLabel : "送付";
}

module.exports = { labelFor };
EOF
cat > src/export.js <<'EOF'
function buildExport(doc) {
  return JSON.stringify({ id: doc.id, body: doc.body });
}

function exportDocument(user, doc) {
  return buildExport(doc);
}

module.exports = { buildExport, exportDocument };
EOF
cat > test/labels.test.js <<'EOF'
const assert = require("node:assert");
const { labelFor } = require("../src/labels");
assert.strictEqual(labelFor("receive"), "受領");
assert.strictEqual(labelFor("send"), "送付");
console.log("labels.test: 2 passed");
EOF
```

直前の /code-review medium の出力:

1. src/labels.js:1 モジュール内でしか使わない `recieveLabel` は typo。`receiveLabel` に直す。
2. src/export.js:5 `exportDocument` は user.role も doc.ownerId も見ずに export を返す。member が他人の doc を export できる。
3. src/export.js は buildExport と exportDocument を両方 export しており公開境界が広い。buildExport を非公開にして境界を再設計すべき。

テストは `node test/labels.test.js` で走り、現在は成功している。

=> /apply-findings を実行。安全な修正を反映し、設計判断は返してください。
