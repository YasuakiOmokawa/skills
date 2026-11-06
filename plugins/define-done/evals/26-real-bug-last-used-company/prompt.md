---
max_turns: 80
timeout_seconds: 2400
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p repo && cd repo
git init -q --template= --separate-git-dir=../repo.gitdir -b main .
git config user.email dev@example.com
git config user.name dev
mkdir -p plans src test docs
cat > package.json <<'EOF'
{"type": "module", "scripts": {"test": "node --test"}}
EOF
cat > src/account.js <<'EOF'
export function createAccounts() {
  const users = new Map();
  const memberships = new Map();
  const invitations = new Map();
  let seq = 0;
  return {
    register(userId) {
      users.set(userId, { lastUsedCompanyId: null });
    },
    createCompany(userId, companyId) {
      memberships.set(`${userId}:${companyId}`, 'OWNER');
      users.get(userId).lastUsedCompanyId = companyId;
    },
    companiesOf(userId) {
      return [...memberships.keys()].filter((key) => key.startsWith(`${userId}:`)).map((key) => key.split(':')[1]);
    },
    signIn(userId) {
      return { currentCompanyId: users.get(userId).lastUsedCompanyId };
    },
    invite(companyId, role) {
      seq += 1;
      const invitationId = `inv${seq}`;
      invitations.set(invitationId, { companyId, role });
      return invitationId;
    },
    accept(invitationId, userId) {
      throw new Error('not implemented');
    },
  };
}
EOF
cat > test/account.test.js <<'EOF'
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createAccounts } from '../src/account.js';

test('a new company is selected in the next session', () => {
  const accounts = createAccounts();
  accounts.register('owner');
  accounts.createCompany('owner', 'acme');
  assert.equal(accounts.signIn('owner').currentCompanyId, 'acme');
});

test('a user without companies has no company selected', () => {
  const accounts = createAccounts();
  accounts.register('guest');
  assert.equal(accounts.signIn('guest').currentCompanyId, null);
});
EOF
cat > docs/glossary.md <<'EOF'
# 用語

**currentCompanyId** / **lastUsedCompanyId**:
近接する 2 つの概念を分けて使う。
- session の `currentCompanyId`: 現在 active な事業所。1 session の中で操作対象になる事業所を指す。`null` は「事業所未選択」の状態を表す (所属が 0 件の時、または唯一の事業所が削除された直後)。
- user の `lastUsedCompanyId`: 新規 session 確立時の default 候補。`signIn` がこの値を session の `currentCompanyId` にコピーする。

**招待**:
所属者が他の利用者を事業所に迎えるための、受諾前の申し出。受諾すると所属になる。
EOF
cat > plans/invitation-accept.md <<'EOF'
# 招待の受諾 設計

## 1. 目的
招待された利用者が招待を受諾して事業所に所属できるようにする。用語と状態の定義は `docs/glossary.md` に従う。

## 2. 仕様
- S-1: 招待を受諾すると (`accept(invitationId, userId)` が `{ status: 200 }`)、利用者は招待の事業所に招待の role で所属する。
- S-2: 同じ招待は二度受諾できない (`{ status: 410 }`)。

## 3. 変更対象
| ファイル | 変更 |
|---|---|
| src/account.js | `accept` の実装 |

## 4. 決定
- D1: 受諾した招待は削除する。
EOF
git add -A && git commit -qm base
```

`repo/` の plans/invitation-accept.md を /define-done して、実装に着手できる状態にしてください。受け入れテストは `repo/test/invitation-accept.acceptance.test.js` に `node:test` で書いてください (`node --test` で流せること)。
