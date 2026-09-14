---
max_turns: 12
timeout_seconds: 300
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p src
cat > src/invoice.js <<'EOF'
function applyDiscount(total, discountRate) {
  return Math.round(total * (1 - discountRate));
}

module.exports = { applyDiscount };
EOF
```

src/invoice.js の applyDiscount に、discountRate が 0 以上 1 以下でなければエラーを投げる範囲チェックを足してください。
