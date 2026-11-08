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
cat > src/membership.js <<'EOF'
export function createCompany({ ownerId }) {
  const roles = new Map([[ownerId, 'OWNER']]);
  return {
    join(userId, role) {
      roles.set(userId, role);
    },
    roleOf(userId) {
      return roles.get(userId) ?? null;
    },
    changeRole(actorId, targetId, role) {
      throw new Error('not implemented');
    },
    remove(actorId, targetId) {
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
1 user が 1 事業所に所属する関係。`role` (OWNER/ADMIN/MEMBER) を持つ。除名すると所属は無くなり、`roleOf` は `null` を返す。

**OWNER**:
事業所の最上位の role で、1 事業所に何人いてもよい。事業所には OWNER が常に 1 人以上いる。最後の OWNER を外す操作 (除名、OWNER 以外への role の変更) は `{ status: 409, error: 'last_owner' }` で拒否し、所属も role も変えない。
EOF
cat > plans/owner-role.md <<'EOF'
# OWNER による role の変更と除名 設計

## 1. 目的
OWNER が所属者の role を変え、所属者を除名できるようにする。OWNER を複数置けるので、OWNER は自分を外して他の OWNER に任せることもできる。用語と守る条件は `docs/glossary.md` に従う。

## 2. 仕様
- S-1: OWNER は所属者の role を変えられる (`changeRole(actorId, targetId, role)` が `{ status: 200 }`)。自分の role も変えられる。OWNER 以外は変えられない (`{ status: 403 }`)。
- S-2: OWNER は所属者を除名できる (`remove(actorId, targetId)` が `{ status: 200 }`)。自分も除名できる。OWNER 以外は除名できない (`{ status: 403 }`)。

## 3. 変更対象
| ファイル | 変更 |
|---|---|
| src/membership.js | `changeRole` と `remove` の実装 |

## 4. 決定
- D1: 最後の OWNER かどうかは、事業所ごとに OWNER の人数 `ownerCount` を持って判定する。`ownerCount` は OWNER が増える操作と減る操作のたびに更新する。
EOF
git add -A && git commit -qm base
```

`repo/` の plans/owner-role.md を /define-done して、実装に着手できる状態にしてください。受け入れテストは `repo/test/owner-role.acceptance.test.js` に `node:test` で書いてください (`node --test` で流せること)。
