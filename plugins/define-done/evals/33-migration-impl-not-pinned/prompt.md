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
mkdir -p src/legacy src/modern test docs/issues plans
printf '{ "name": "portal-web", "private": true, "scripts": { "check": "node --te\x73t" } }\n' > package.json
cat > src/runtime-for-path.js <<'EOF'
const MODERN_PATHS = ["/error"];

function runtimeForPath(pathname) {
  const trimmed = pathname.length > 1 ? pathname.replace(/\/$/, "") : pathname;
  return MODERN_PATHS.includes(trimmed) ? "Modern" : "Legacy";
}

module.exports = { runtimeForPath };
EOF
cat > src/legacy/pages.js <<'EOF'
function renderLegacy(url) {
  if (url.pathname === "/invite") {
    return url.searchParams.get("token")
      ? "<h1>招待</h1><p>招待を受諾しています</p>"
      : "<h1>招待</h1><p>招待のリンクが正しくありません</p>";
  }
  if (url.pathname === "/account") return "<h1>アカウント</h1>";
  return "<h1>ページが見つかりません</h1>";
}

module.exports = { renderLegacy };
EOF
cat > src/modern/pages.js <<'EOF'
function renderModern(url) {
  if (url.pathname === "/error") return "<h1>エラー</h1><p>もう一度お試しください</p>";
  return "<h1>ページが見つかりません</h1>";
}

module.exports = { renderModern };
EOF
cat > src/app.js <<'EOF'
const { runtimeForPath } = require("./runtime-for-path");
const { renderLegacy } = require("./legacy/pages");
const { renderModern } = require("./modern/pages");

function renderDocument(href) {
  const url = new URL(href, "https://portal.example.com");
  return runtimeForPath(url.pathname) === "Modern" ? renderModern(url) : renderLegacy(url);
}

module.exports = { renderDocument };
EOF
cat > test/runtime-for-path.test.js <<'EOF'
const test = require("node:test");
const assert = require("node:assert/strict");
const { runtimeForPath } = require("../src/runtime-for-path");

test("/error は Modern が描く", () => {
  assert.equal(runtimeForPath("/error"), "Modern");
});

test("/account は Legacy が描く", () => {
  assert.equal(runtimeForPath("/account"), "Legacy");
});
EOF
cat > test/app.test.js <<'EOF'
const test = require("node:test");
const assert = require("node:assert/strict");
const { renderDocument } = require("../src/app");

test("/error を開くとエラーの見出しを出す", () => {
  assert.match(renderDocument("/error"), /<h1>エラー<\/h1>/);
});

test("/account を開くとアカウントの見出しを出す", () => {
  assert.match(renderDocument("/account"), /<h1>アカウント<\/h1>/);
});
EOF
cat > docs/issues/12.md <<'EOF'
# 招待の受諾の画面を Modern で書き直す

## What to build

招待の受諾 (`/invite`) を Modern で書き直す。招待の link を開いた利用者には、今と同じ文言を出す。

- `src/runtime-for-path.js` の Modern の path の一覧に `/invite` を足す
- 移行は 1 画面ずつ進める。まだ移していない画面 (`/account`) は Legacy のまま動かす

## Acceptance criteria

- [ ] token のある招待の link を開くと「招待を受諾しています」を出す
- [ ] token の無い link を開くと「招待のリンクが正しくありません」を出す
- [ ] 移した画面の Legacy の code が消えている
EOF
cat > plans/invite.md <<'EOF'
# 招待の受諾の画面の移行

## 目的と背景

issue #12 (`docs/issues/12.md`)。Legacy から Modern へ、画面を 1 つずつ移している。今は `/error` だけが Modern で、残りは Legacy が描く。今回は招待の受諾を移す。

## 決定

| ID | 項目 | 決定 |
|---|---|---|
| D1 | 描く側の切り替え | `src/runtime-for-path.js` の `MODERN_PATHS` に `/invite` を足す |
| D2 | 画面 | `src/modern/invite.js` に `renderInvite(url)` を書き、`renderModern` から呼ぶ |
| D3 | 消すもの | `src/legacy/pages.js` の `/invite` の分岐を消す |

## 変更対象

| ファイル | 変更 |
|---|---|
| src/runtime-for-path.js | `/invite` を足す |
| src/modern/invite.js | 新規 |
| src/modern/pages.js | `/invite` を `renderInvite` に渡す |
| src/legacy/pages.js | `/invite` の分岐を消す |
EOF
git add -A
git -c user.name=fixture -c user.email=fixture@example.com commit -qm base
```

カレントブランチから新しいブランチを切り、`repo/plans/invite.md` の設計を /define-done する。受け入れテストは `repo/test/invite.acceptance.test.js` に `node:test` で書く (`node --test` で流せること)。Gate が ready でなければ止めて報告する。
