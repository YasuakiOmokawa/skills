---
max_turns: 30
timeout_seconds: 600
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p src
cat > src/invoice.js <<'EOF'
const tempLabel = "請求書";

function calculateTotal(lines, taxRate) {
  const subtotal = lines.reduce((sum, l) => sum + l.price * l.qty, 0);
  return Math.round(subtotal * (1 + taxRate));
}

function renderInvoice(lines, taxRate) {
  return `${tempLabel}: ${calculateTotal(lines, taxRate)}`;
}

module.exports = { tempLabel, calculateTotal, renderInvoice };
EOF
cat > src/report.js <<'EOF'
const { tempLabel, calculateTotal } = require("./invoice");

function monthlyReport(items) {
  const totals = items.map((lines) => calculateTotal(lines, 0.1));
  return `${tempLabel} 合計: ${totals.reduce((a, b) => a + b, 0)}`;
}

module.exports = { monthlyReport };
EOF
```

直前の /code-review medium の出力:

1. src/invoice.js:1 `tempLabel` は請求書ラベルの定数なので `invoiceLabel` に改名すべき。src/report.js:1,5 でも参照している。
2. src/invoice.js は請求計算 (calculateTotal) と表示 (renderInvoice) が同居している。計算を src/billing.js に分離すべき。

=> /apply-findings を実行。
