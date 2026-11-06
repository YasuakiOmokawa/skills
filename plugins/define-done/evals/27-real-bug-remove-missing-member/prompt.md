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
mkdir -p plans src test docs/adr
cat > package.json <<'EOF'
{"type": "module", "scripts": {"test": "node --test"}}
EOF
cat > src/membership.js <<'EOF'
const ROLE_LEVEL = { MEMBER: 0, ADMIN: 1, OWNER: 2 };

function isAtLeast(role, minRole) {
  return Object.hasOwn(ROLE_LEVEL, role) && ROLE_LEVEL[role] >= ROLE_LEVEL[minRole];
}

export function createCompany({ ownerId }) {
  const roles = new Map([[ownerId, 'OWNER']]);
  const audit = [];
  return {
    join(userId, role) {
      roles.set(userId, role);
    },
    roleOf(userId) {
      return roles.get(userId) ?? null;
    },
    auditLog() {
      return [...audit];
    },
    remove(actorId, targetId) {
      throw new Error('not implemented');
    },
    transfer(actorId, toId) {
      throw new Error('not implemented');
    },
  };
}
EOF
cat > test/membership.test.js <<'EOF'
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createCompany } from '../src/membership.js';

test('the founder is the owner', () => {
  assert.equal(createCompany({ ownerId: 'owner' }).roleOf('owner'), 'OWNER');
});

test('a joined user has the given role', () => {
  const company = createCompany({ ownerId: 'owner' });
  company.join('admin', 'ADMIN');
  assert.equal(company.roleOf('admin'), 'ADMIN');
});
EOF
cat > docs/glossary.md <<'EOF'
# 用語

**所属**:
1 user が 1 事業所に所属する関係を表す行。`role` (OWNER/ADMIN/MEMBER) を持ち、行の存在自体が「確定所属」を表す。離脱 / 除名は監査ログ 1 行を記録した上で行を削除する。

**監査ログ**:
利用者の操作を 1 操作 1 行で残す記録。`auditLog()` で読める。除名は `membership_removed`、OWNER の委譲は `ownership_transferred` を記録する。
EOF
cat > docs/adr/0010-analysis.md <<'EOF'
# ADR-0010 分析: 確かめる観点

- [ ] permission: MEMBER が除名 → 403、所属は無変更
- [ ] permission: ADMIN が OWNER を除名 → 拒否、所属は無変更
- [ ] idempotency [境界値: 0 行対象]: 既に除名済みメンバーへ remove → 404 not_found
- [ ] 委譲先が所属していない transfer → 404 not_found、role も監査ログも無変更
EOF
cat > plans/membership-change.md <<'EOF'
# 除名と OWNER の委譲 設計

## 1. 目的
事業所の所属者を除名でき、OWNER が OWNER 権限を他の所属者に委譲できるようにする。用語は `docs/glossary.md` に、確かめる観点は `docs/adr/0010-analysis.md` に従う。

## 2. 仕様
- S-1: ADMIN 以上は所属者を除名できる (`remove(actorId, targetId)` が `{ status: 200 }`)。MEMBER は除名できない (`{ status: 403 }`)。OWNER を除名できるのは OWNER だけ。
- S-2: OWNER は所属者に OWNER を委譲できる (`transfer(actorId, toId)` が `{ status: 200 }`)。委譲した元の OWNER は ADMIN になる。

## 3. 変更対象
| ファイル | 変更 |
|---|---|
| src/membership.js | `remove` と `transfer` の実装 |

## 4. 決定
- D1: 除名は `roles.delete(targetId)` で行い、続けて監査ログに 1 行足す。
EOF
git add -A && git commit -qm base
```

`repo/` の plans/membership-change.md を /define-done して、実装に着手できる状態にしてください。受け入れテストは `repo/test/membership-change.acceptance.test.js` に `node:test` で書いてください (`node --test` で流せること)。
