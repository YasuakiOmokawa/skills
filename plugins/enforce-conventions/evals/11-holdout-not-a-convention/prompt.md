---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p repo
cd repo
git init -q --template= --separate-git-dir=../repo.gitdir -b main .
mkdir -p src
cat > package.json <<'EOF'
{ "name": "back-office", "private": true, "type": "module", "scripts": { "test": "node --test" } }
EOF
git add -A
git -c user.name=fixture -c user.email=fixture@example.com commit -qm init
cat > src/article-import.ts <<'EOF'
export type ImportedArticle = { title: string; status: "draft" | "published"; publishedAt: string | null };

export function readImportedArticle(json: string): ImportedArticle {
  return JSON.parse(json) as ImportedArticle;
}

export function importedArticleLine(article: ImportedArticle): string {
  switch (article.status) {
    case "draft":
      return `${article.title} (下書き)`;
    case "published":
      return `${article.title} (${article.publishedAt!.slice(0, 10)})`;
  }
}
EOF
cat > src/article-import.test.ts <<'EOF'
import { test } from "node:test";
import assert from "node:assert/strict";
import { importedArticleLine, readImportedArticle } from "./article-import.ts";

test("下書きの記事の行", () => {
  const article = readImportedArticle('{"title":"春の新作","status":"draft","publishedAt":null}');
  assert.equal(importedArticleLine(article), "春の新作 (下書き)");
});
test("公開済みの記事の行は公開日を含む", () => {
  const article = readImportedArticle('{"title":"春の新作","status":"published","publishedAt":"2026-04-01T09:00:00Z"}');
  assert.equal(importedArticleLine(article), "春の新作 (2026-04-01)");
});
EOF
cat > src/coupon.ts <<'EOF'
export type Coupon = { code: string; kind: "percent" | "fixed"; percent: number | null; amount: number | null };

export function percentCoupon(code: string, percent: number): Coupon {
  return { code, kind: "percent", percent, amount: null };
}

export function fixedCoupon(code: string, amount: number): Coupon {
  return { code, kind: "fixed", percent: null, amount };
}

export function discount(coupon: Coupon, price: number): number {
  switch (coupon.kind) {
    case "percent":
      return Math.floor((price * coupon.percent!) / 100);
    case "fixed":
      return coupon.amount!;
  }
}
EOF
cat > src/coupon.test.ts <<'EOF'
import { test } from "node:test";
import assert from "node:assert/strict";
import { discount, fixedCoupon, percentCoupon } from "./coupon.ts";

test("割合のクーポンは価格に割合を掛けた額を引く", () => {
  assert.equal(discount(percentCoupon("SPRING", 10), 1980), 198);
});
test("定額のクーポンは決まった額を引く", () => {
  assert.equal(discount(fixedCoupon("THANKS", 300), 1980), 300);
});
EOF
cat > src/campaign.ts <<'EOF'
import type { Coupon } from "./coupon.ts";

export const welcomeCoupon: Coupon = { code: "WELCOME", kind: "fixed", percent: null, amount: null };
EOF
cat > src/ticket.ts <<'EOF'
export type TicketStatus = "open" | "pending" | "closed";

export type Ticket = { id: string; status: TicketStatus; assignee: string | null };

export function openTicket(id: string, assignee: string): Ticket {
  return { id, status: "open", assignee };
}

export function holdTicket(ticket: Ticket): Ticket {
  return { ...ticket, status: "pending" };
}

export function closeTicket(ticket: Ticket): Ticket {
  return { ...ticket, status: "closed" };
}

export function badgeColor(status: TicketStatus): string {
  if (status === "open") return "green";
  return "gray";
}

export function assigneeLabel(ticket: Ticket): string {
  return ticket.assignee ?? "未割り当て";
}
EOF
cat > src/ticket.test.ts <<'EOF'
import { test } from "node:test";
import assert from "node:assert/strict";
import { assigneeLabel, badgeColor, closeTicket, holdTicket, openTicket } from "./ticket.ts";

test("開いているチケットだけ緑", () => {
  const ticket = openTicket("t-1", "葵");
  assert.equal(badgeColor(ticket.status), "green");
  assert.equal(badgeColor(holdTicket(ticket).status), "gray");
  assert.equal(badgeColor(closeTicket(ticket).status), "gray");
});
test("担当者の名前を表示する", () => {
  assert.equal(assigneeLabel(openTicket("t-1", "葵")), "葵");
});
EOF
```

`repo/` で `node --test` が 6 件すべて成功することを確認してから、次の依頼に取りかかってください。

repo/ の未 commit の実装差分 (src/ 以下の全ファイル) に /enforce-conventions を実行する。commit はしない。
