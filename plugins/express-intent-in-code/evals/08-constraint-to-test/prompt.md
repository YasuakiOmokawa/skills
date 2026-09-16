---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Skill, Read, Write, Edit, Bash]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p src
cat > package.json <<'EOF'
{ "name": "fixture", "private": true, "type": "module", "scripts": { "test": "node --test" } }
EOF
cat > src/receipt.ts <<'EOF'
// 明細行
export type Line = { label: string; amount: number };

// 明細の合計を返す
export function total(lines: Line[]): number {
  // amount を全部足す
  return lines.reduce((acc, l) => acc + l.amount, 0);
}

// 置換対象の文字
const NO_BREAK_SPACES = new RegExp("[" + String.fromCodePoint(0x202f, 0xa0) + "]", "g");

// 金額をユーロ表記にする
export function formatEuro(amount: number): string {
  const s = new Intl.NumberFormat("fr-FR", { style: "currency", currency: "EUR" }).format(amount);
  return s.replace(NO_BREAK_SPACES, " ");
}

// 明細と合計をメール本文用のテキストにする
export function renderReceipt(lines: Line[]): string {
  // 各行を "label: 金額" にして改行で繋ぐ
  const body = lines.map((l) => `${l.label}: ${formatEuro(l.amount)}`).join("\n");
  // 最後に合計行
  return `${body}\nTotal: ${formatEuro(total(lines))}`;
}
EOF
cat > src/receipt.test.ts <<'EOF'
import { test } from "node:test";
import assert from "node:assert/strict";
import { formatEuro, renderReceipt, total } from "./receipt.ts";

test("total sums amounts", () => {
  assert.equal(total([{ label: "a", amount: 10 }, { label: "b", amount: 2.5 }]), 12.5);
});
test("formatEuro uses French formatting", () => {
  assert.match(formatEuro(1234.5), /^1.234,50.€$/);
  assert.match(formatEuro(0), /^0,00.€$/);
});
test("renderReceipt lists lines then total", () => {
  const out = renderReceipt([{ label: "Livre", amount: 12 }, { label: "Stylo", amount: 3 }]);
  const rows = out.split("\n");
  assert.equal(rows.length, 3);
  assert.match(rows[0], /^Livre: 12,00.€$/);
  assert.match(rows[2], /^Total: 15,00.€$/);
});
EOF
```

`node --test` が 3 件以上すべて成功することを確認してから、次の依頼に取りかかってください。

src/receipt.ts のコメントを減らして、意図はコードで表して。それと `formatEuro` の `.replace(NO_BREAK_SPACES, " ")` は、Node の ICU が桁区切りと通貨記号の前に no-break space (U+202F / U+00A0) を返し、メール本文での検索と折り返しが崩れるので入れてある。この理由が後から読んでも分かるようにしておいて。
