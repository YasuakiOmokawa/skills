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
cat > src/display-text.ts <<'EOF'
// 不可視 unicode と方向制御文字を除去し、表示名偽装とヘッダインジェクションを防ぐ
const isInvisibleOrDirectional = (cp: number): boolean =>
  cp <= 0x1f ||
  (cp >= 0x7f && cp <= 0x9f) ||
  (cp >= 0x200b && cp <= 0x200d) ||
  cp === 0xfeff ||
  (cp >= 0x202a && cp <= 0x202e) ||
  (cp >= 0x2066 && cp <= 0x2069);

// 呼び手は表示用に出す直前に必ずこれを通すこと
export const sanitizeDisplayText = (s: string): string =>
  Array.from(s)
    .filter((ch) => !isInvisibleOrDirectional(ch.codePointAt(0) ?? 0))
    .join("")
    .trim();
EOF
cat > src/invitation-mail.ts <<'EOF'
import { sanitizeDisplayText } from "./display-text.ts";

export type Invitation = { inviterName: string; companyName: string; acceptUrl: string };

export function renderInvitationSubject(inv: Invitation): string {
  // 件名にも本文にも出すので念のためここでも sanitize する
  const company = sanitizeDisplayText(inv.companyName);
  return `${company} への招待`;
}

export function renderInvitationBody(inv: Invitation): string {
  const inviter = sanitizeDisplayText(sanitizeDisplayText(inv.inviterName));
  const company = sanitizeDisplayText(inv.companyName);
  return `${inviter} さんが ${company} に招待しました。\n${inv.acceptUrl}`;
}
EOF
cat > src/welcome-mail.ts <<'EOF'
import { sanitizeDisplayText } from "./display-text.ts";

export type Welcome = { displayName: string };

export function renderWelcomeBody(w: Welcome): string {
  const name = sanitizeDisplayText(w.displayName);
  return `${name} さん、ようこそ。`;
}
EOF
cat > src/mail.test.ts <<'EOF'
import { test } from "node:test";
import assert from "node:assert/strict";
import { renderInvitationBody, renderInvitationSubject } from "./invitation-mail.ts";
import { renderWelcomeBody } from "./welcome-mail.ts";

const rtl = "‮";
const zw = "​";

test("invitation subject strips control characters", () => {
  assert.equal(renderInvitationSubject({ inviterName: "a", companyName: `Ac${rtl}me`, acceptUrl: "u" }), "Acme への招待");
});
test("invitation body strips control characters from both names", () => {
  const body = renderInvitationBody({ inviterName: `Bo${zw}b`, companyName: `Ac${rtl}me`, acceptUrl: "https://x/accept" });
  assert.equal(body, "Bob さんが Acme に招待しました。\nhttps://x/accept");
});
test("welcome body strips control characters", () => {
  assert.equal(renderWelcomeBody({ displayName: ` Al${zw}ice ` }), "Alice さん、ようこそ。");
});
EOF
```

`node --test` が 3 件すべて成功することを確認してから、次の依頼に取りかかってください。

src/display-text.ts の sanitizeDisplayText は string を受けて string を返すので、呼び手が「もう通したか」を型で判断できず、invitation-mail.ts では同じ値に 2 回かけている。sanitize 済みであることをコードで表して、二重適用を消して。出力は変えないで。
