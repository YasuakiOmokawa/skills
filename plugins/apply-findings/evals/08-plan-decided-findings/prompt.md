---
max_turns: 30
timeout_seconds: 600
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p src plans
cat > src/export.js <<'EOF'
const API = "https://billing.example.com/invoices";

async function fetchInvoices() {
  const res = await fetch(API, { signal: AbortSignal.timeout(5000) });
  return res.json();
}

function toCsv(invocies) {
  return invocies.map((i) => `${i.id},${i.amount}`).join("\n");
}

async function exportCsv() {
  return toCsv(await fetchInvoices());
}

module.exports = { exportCsv };
EOF
cat > plans/export.md <<'EOF'
# 請求書の CSV export 設計

## 1. 目的
請求書の一覧を CSV で export できるようにする。

## 2. 対象外
- export する件数の上限と分割は、この issue では扱わない。#120 で件数の実測を取ってから決める。

## 3. 設計
- `fetchInvoices` は外部 API を 5 秒の timeout 付きで呼ぶ。
EOF
```

直前の /code-review medium の出力:

1. src/export.js:12 export に件数の上限が無く、請求書が大量にあると遅くなる。上限を入れるべき。
2. src/export.js:4 外部 API の呼び出しに timeout が無く、API が止まると export が終わらない。
3. src/export.js:9 全件をメモリで組み立てているので、stream で書き出す形に変えるか検討してほしい。
4. src/export.js:8-9 引数名 `invocies` は `invoices` の typo。

=> /apply-findings を実行。安全な修正は反映して、それ以外は判断に必要なことを添えて返してください。計画は plans/export.md です。
