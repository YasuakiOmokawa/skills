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
mkdir -p plans src test docs/requirements
cat > package.json <<'EOF'
{"type": "module", "scripts": {"test": "node --test --test-isolation=none"}}
EOF
cat > src/rate-limit.js <<'EOF'
const counts = new Map();

export function allow(key, max = 5) {
  const used = counts.get(key) ?? 0;
  if (used >= max) return false;
  counts.set(key, used + 1);
  return true;
}

export function resetRateLimits() {
  counts.clear();
}
EOF
cat > src/auth.js <<'EOF'
import { allow } from './rate-limit.js';

export function createAuth({ users, audit }) {
  return {
    login({ ip, email, password }) {
      if (!allow(ip)) return { status: 429 };
      if (users.get(email) !== password) return { status: 401 };
      return { status: 200 };
    },
  };
}
EOF
cat > test/support.js <<'EOF'
export const TEST_IP = '203.0.113.9';
export const users = new Map([['alice@example.com', 'correct horse']]);
export const recordingAudit = () => {
  const entries = [];
  return { entries, append: (entry) => entries.push(entry) };
};
EOF
cat > test/auth.test.js <<'EOF'
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createAuth } from '../src/auth.js';
import { TEST_IP, users, recordingAudit } from './support.js';

test('正しいパスワードでログインできる', () => {
  const auth = createAuth({ users, audit: recordingAudit() });
  assert.equal(auth.login({ ip: TEST_IP, email: 'alice@example.com', password: 'correct horse' }).status, 200);
});

test('誤ったパスワードは 401', () => {
  const auth = createAuth({ users, audit: recordingAudit() });
  assert.equal(auth.login({ ip: TEST_IP, email: 'alice@example.com', password: 'wrong' }).status, 401);
});

test('同じ IP の 6 回目は 429', () => {
  const auth = createAuth({ users, audit: recordingAudit() });
  const ip = '198.51.100.7';
  for (let i = 0; i < 5; i++) auth.login({ ip, email: 'alice@example.com', password: 'wrong' });
  assert.equal(auth.login({ ip, email: 'alice@example.com', password: 'correct horse' }).status, 429);
});
EOF
cat > docs/requirements/login-audit.md <<'EOF'
# ログインの記録

- ログインに成功したら、監査ログ (`audit.append`) に `{ event: 'sign_in', email, ip }` を 1 件記録する。
- パスワードの誤り (401) と、試行の上限 (429) では記録しない。
- ログインの応答 (200・401・429) と、IP ごとに 5 回までの上限は変えない。
EOF
cat > plans/login-audit.md <<'EOF'
# ログインの記録 設計

## 1. 目的
要件 `docs/requirements/login-audit.md` (正本) を満たす。

## 2. 変更対象
| ファイル | 変更 |
|---|---|
| src/auth.js | 成功の後に `audit.append` を呼ぶ |
EOF
git add -A && git commit -qm base
```

`repo/` の plans/login-audit.md を /define-done して、実装に着手できる状態にしてください。受け入れテストは `repo/test/` の下に `*.acceptance.test.js` として `node:test` で書いてください (`npm test` で流せること)。
