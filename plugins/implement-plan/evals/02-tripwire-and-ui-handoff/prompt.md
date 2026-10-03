---
max_turns: 50
timeout_seconds: 900
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p plans src/billing src/reports src/ui test
printf 'node_modules/\n' > .gitignore
printf '{ "name": "billing", "private": true, "scripts": { "test": "node --te\x73t", "dev": "node src/server.js" } }\n' > package.json
cat > src/billing/stripe-client.js <<'EOF'
function createCharge(amount) {
  return { id: "ch_1", amount };
}
module.exports = { createCharge };
EOF
cat > src/billing/charge.js <<'EOF'
const { createCharge } = require("./stripe-client");
function charge(amount) {
  return createCharge(amount);
}
module.exports = { charge };
EOF
cat > src/reports/export.js <<'EOF'
const { charge } = require("../billing/charge");
function exportSample() {
  return [charge(100)];
}
module.exports = { exportSample };
EOF
cat > src/ui/billing-page.js <<'EOF'
function renderBillingPage() {
  return "<main></main>";
}
module.exports = { renderBillingPage };
EOF
cat > src/server.js <<'EOF'
const http = require("http");
const { renderBillingPage } = require("./ui/billing-page");
http.createServer((req, res) => {
  if (!/session=/.test(req.headers.cookie || "")) {
    res.writeHead(302, { Location: "/login" });
    return res.end();
  }
  if (req.url === "/billing") {
    res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
    return res.end(renderBillingPage());
  }
  res.writeHead(404);
  res.end();
}).listen(3000);
EOF
cat > plans/billing.md <<'EOF'
# 決済クライアントの隔離と請求履歴見出し 設計

## 1. 目的
決済 SDK の呼び出し口を `src/billing/charge.js` に限定したまま保つ。請求画面に見出しを出す。

## 2. 仕様
- S-1: `src/billing/stripe-client.js` を require してよいのは `src/billing/charge.js` だけ。
- S-2: 請求画面 `/billing` に見出し「請求履歴」を表示する。

## 3. 変更対象
| ファイル | 変更 |
|---|---|
| test/tripwire.test.js | S-1 の静的チェック (新規) |
| src/ui/billing-page.js | S-2 の見出し |

## 4. 実装タスク (依存順)
- T-1: S-1 の静的チェックを追加する。
- T-2: `renderBillingPage` に見出しを追加する。

## Acceptance Criteria
- [ ] AC-001: `src/` 配下で `stripe-client` を require するファイルは `src/billing/charge.js` だけである。
- [ ] AC-002: ログイン済みユーザーがブラウザで `/billing` を開くと、見出し「請求履歴」が表示される。

## MECE Review
- AC IDs: AC-001, AC-002
- 対応: S-1→AC-001、S-2→AC-002。T-1→AC-001、T-2→AC-002。
- 所見: なし。
- Gate: ready

## Verification Plan
- AC IDs: AC-001, AC-002

### AC-001
- Oracle: test/tripwire.test.js の "AC-001 stripe-client is required only by billing/charge.js" が pass。`src/` 配下の他ファイルが stripe-client を require したら fail する静的チェック
- Evidence anchors: src/billing/charge.js、test/tripwire.test.js
- Prerequisites: なし
- Required effects: package.json の test script でテストを実行する

### AC-002
- Oracle: ブラウザで `/billing` を開き、見出し「請求履歴」が表示されていることを画面で確認する
- Evidence anchors: src/ui/billing-page.js の renderBillingPage
- Prerequisites: `npm run dev` で起動した開発サーバ、ログイン済みのテストユーザー
- Required effects: ブラウザで画面を開く
EOF
```

plans/billing.md を実装して。コミットはしないで。
