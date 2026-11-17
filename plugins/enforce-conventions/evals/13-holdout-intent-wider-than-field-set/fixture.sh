set -eu
mkdir -p repo
cd repo
git init -q --template= --separate-git-dir=../repo.gitdir -b main .
printf 'node_modules/\n' > .gitignore
cat > package.json <<'EOF'
{
  "name": "keys",
  "private": true,
  "type": "module",
  "scripts": { "test": "node --test", "typecheck": "node node_modules/typescript/bin/tsc --noEmit" },
  "devDependencies": { "@types/node": "24.19.2", "typescript": "5.9.3" }
}
EOF
cat > tsconfig.json <<'EOF'
{
  "compilerOptions": {
    "strict": true,
    "noEmit": true,
    "module": "nodenext",
    "target": "es2022",
    "allowImportingTsExtensions": true,
    "types": ["node"],
    "skipLibCheck": true
  },
  "include": ["src"]
}
EOF
NODE_OPTIONS=--use-system-ca npm install --include=dev --no-audit --no-fund --silent --fetch-retries=1
mkdir -p src docs
cat > CLAUDE.md <<'EOF'
# keys

## 規約

- API キーが使えるかは、記録があるかどうかだけで決める。記録に状態 (有効、失効、停止など) を表すフィールドを持たせず、失効や停止を別の集合や表で持たない。
EOF
cat > docs/api-key.md <<'EOF'
# API キーの記録を作る

- 記録のフィールド: id、ownerId、hash、createdAt、lastUsedAt
- 状態を表すフィールドは持たない。記録があれば使え、無ければ無い。失効や停止を別の集合や表で持たない
- 保存と一覧を提供する (削除は後で足す)

## Acceptance criteria

- 保存したキーが持ち主の一覧に出る
- 記録に状態を表すフィールドが無い
EOF
cat > docs/plan.md <<'EOF'
# 計画

## MECE Review

| 要求 | 対応 |
|---|---|
| 保存したキーが持ち主の一覧に出る | AC-001 |
| 記録に状態を表すフィールドが無い | 範囲外: 規約として enforce-conventions で担保する |
EOF
cat > src/clock.ts <<'EOF'
export function currentTime(): Date {
  return new Date();
}
EOF
git add -A
git -c user.name=fixture -c user.email=fixture@example.com commit -qm init
cat > src/api-key.ts <<'EOF'
export type ApiKey = {
  id: string;
  ownerId: string;
  hash: string;
  createdAt: Date;
  lastUsedAt: Date | null;
};

const keys = new Map<string, ApiKey>();

export function saveApiKey(key: ApiKey): boolean {
  if (keys.has(key.id)) return false;
  keys.set(key.id, key);
  return true;
}

export function listApiKeys(ownerId: string): ApiKey[] {
  return [...keys.values()].filter((key) => key.ownerId === ownerId);
}

export function deleteApiKey(ownerId: string, id: string): boolean {
  const key = keys.get(id);
  if (key === undefined || key.ownerId !== ownerId) return false;
  return keys.delete(id);
}
EOF
cat > src/api-key.test.ts <<'EOF'
import { test } from "node:test";
import assert from "node:assert/strict";
import { deleteApiKey, listApiKeys, saveApiKey } from "./api-key.ts";

const key = (id: string, ownerId: string) => ({
  id,
  ownerId,
  hash: `hash-${id}`,
  createdAt: new Date("2026-04-01T00:00:00.000Z"),
  lastUsedAt: null,
});

test("保存したキーは持ち主の一覧に出て、ほかの人の一覧に出ない", () => {
  assert.equal(saveApiKey(key("k-1", "alice")), true);
  assert.deepEqual(listApiKeys("alice").map(({ id }) => id), ["k-1"]);
  assert.deepEqual(listApiKeys("bob"), []);
});
test("同じ id のキーは 2 度保存できない", () => {
  assert.equal(saveApiKey(key("k-2", "alice")), true);
  assert.equal(saveApiKey(key("k-2", "alice")), false);
});
test("持ち主だけがキーを消せ、消したキーは一覧から消える", () => {
  saveApiKey(key("k-3", "alice"));
  assert.equal(deleteApiKey("bob", "k-3"), false);
  assert.equal(deleteApiKey("alice", "k-3"), true);
  assert.deepEqual(listApiKeys("alice").map(({ id }) => id).includes("k-3"), false);
});
EOF
