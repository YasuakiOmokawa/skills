---
name: chain-invite-owner
tags: [chain]
plugins:
  - "../../plugins/define-done"
  - "../../plugins/implement-plan"
max_turns: 150
timeout_seconds: 3600
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
cat > src/membership.js <<'EOF'
const ROLE_LEVEL = { MEMBER: 0, ADMIN: 1, OWNER: 2 };

function isAtLeast(role, minRole) {
  return Object.hasOwn(ROLE_LEVEL, role) && ROLE_LEVEL[role] >= ROLE_LEVEL[minRole];
}

export function canChangeRole(actorRole, beforeRole, nextRole) {
  const touchesOwner = beforeRole === 'OWNER' || nextRole === 'OWNER';
  return touchesOwner ? actorRole === 'OWNER' : true;
}

export function createCompany({ ownerId }) {
  const roles = new Map([[ownerId, 'OWNER']]);
  return {
    roleOf(userId) {
      return roles.get(userId) ?? null;
    },
    changeRole(actorId, targetId, nextRole) {
      const actorRole = roles.get(actorId);
      if (!actorRole || !isAtLeast(actorRole, 'ADMIN')) return { status: 403 };
      if (!canChangeRole(actorRole, roles.get(targetId), nextRole)) return { status: 403 };
      roles.set(targetId, nextRole);
      return { status: 200 };
    },
    invite(actorId, role) {
      throw new Error('not implemented');
    },
    accept(invitationId, userId) {
      throw new Error('not implemented');
    },
  };
}
EOF
cat > test/membership.test.js <<'EOF'
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createCompany } from '../src/membership.js';

test('owner can change a role', () => {
  const company = createCompany({ ownerId: 'owner' });
  assert.equal(company.changeRole('owner', 'owner', 'OWNER').status, 200);
});

test('a non member cannot change roles', () => {
  const company = createCompany({ ownerId: 'owner' });
  assert.equal(company.changeRole('stranger', 'owner', 'MEMBER').status, 403);
});
EOF
cat > docs/glossary.md <<'EOF'
# 用語

**role**:
所属が表す権限階層。`OWNER` / `ADMIN` / `MEMBER` の 3 段階。OWNER のみが事業所削除 / 課金変更 / OWNER 権限委譲を行える。ADMIN は OWNER を作れず、自身の昇格もできない (= OWNER 昇格は OWNER のみ承認可)。1 事業所に複数 OWNER を許容する。

**招待**:
所属者が他の利用者を事業所に迎えるための、受諾前の申し出。受諾すると所属になる。
EOF
cat > plans/invitation.md <<'EOF'
# 招待 設計

## 1. 目的
所属者が他の利用者を事業所に招待できるようにする。用語と権限は `docs/glossary.md` に従う。

## 2. 仕様
- S-1: OWNER と ADMIN は招待を作成できる (`invite(actorId, role)` が `{ status: 201, invitationId }` を返す)。MEMBER と非所属者は作成できない (`{ status: 403 }`)。
- S-2: 招待を受諾すると (`accept(invitationId, userId)` が `{ status: 200 }`)、利用者は招待の role で所属する。
- S-3: 同じ招待は二度受諾できない (`{ status: 410 }`)。

## 3. 変更対象
| ファイル | 変更 |
|---|---|
| src/membership.js | `invite` と `accept` の実装 |

## 4. 決定
- D1: 招待の ID は連番で振る。
- D2: `invite` は呼び手が ADMIN 以上かを、`changeRole` と同じく `isAtLeast` で確かめる。
EOF
git add -A && git commit -qm base
```

`repo/` の plans/invitation.md について、/define-done で要求から受け入れテストを `repo/test/invitation.acceptance.test.js` に `node:test` で書いて実装に着手できる状態にし、続けて /implement-plan で `repo/src/membership.js` を実装してください。受け入れテストの封の commit のほかは commit しなくていいです。作業の最後に、`cat repo/test/invitation.acceptance.test.js` と `cat repo/src/membership.js` をそれぞれ 1 回ずつ実行して内容を表示してください。
