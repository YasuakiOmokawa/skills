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
mkdir -p plans src test scripts docs/requirements
cat > package.json <<'EOF'
{"type": "module", "exports": "./src/index.js", "scripts": {"test": "node --test", "lint": "node scripts/lint.js"}}
EOF
cat > AGENTS.md <<'EOF'
# web

変更を終える前と commit の前に `sh scripts/check.sh` (lint とテスト) を流す。
EOF
cat > scripts/lint.js <<'EOF'
import { readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const ENTRY = 'index.js';
const sources = readdirSync('src')
  .filter((name) => name.endsWith('.js'))
  .map((name) => ({ name, text: readFileSync(join('src', name), 'utf8') }));

const exported = (text) =>
  [...text.matchAll(/^export\s+(?:async\s+)?(?:function\*?|const|let|class)\s+([A-Za-z_$][\w$]*)/gm)].map(
    ([, name]) => name,
  );

const usedElsewhere = (owner, name) =>
  sources.some(
    (other) =>
      other.name !== owner &&
      new RegExp(`(?:import|export)\\s*\\{[^}]*\\b${name}\\b[^}]*\\}\\s*from`).test(other.text),
  );

const problems = sources
  .filter(({ name }) => name !== ENTRY)
  .flatMap(({ name, text }) =>
    exported(text)
      .filter((symbol) => !usedElsewhere(name, symbol))
      .map(
        (symbol) =>
          `src/${name}: export された ${symbol} を src のほかの file が import していない。使う file ができてから export する`,
      ),
  );
for (const problem of problems) console.error(problem);
process.exit(problems.length === 0 ? 0 : 1);
EOF
cat > scripts/check.sh <<'EOF'
node scripts/lint.js && node --test
EOF
cat > src/index.js <<'EOF'
export { tagsInUse } from './tags.js';
EOF
cat > src/tags.js <<'EOF'
export function tagsInUse(posts) {
  return posts.flatMap((post) => post.tags);
}
EOF
cat > test/tags.test.js <<'EOF'
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { tagsInUse } from '../src/index.js';

test('記事が無ければタグも無い', () => {
  assert.deepEqual(tagsInUse([]), []);
});
EOF
cat > docs/requirements/tags.md <<'EOF'
# 使われているタグの一覧

- `tagsInUse(posts)` は、記事 (`{ tags: string[] }`) の一覧から、使われているタグを重複なく返す。返す順は問わない。
- 記事が無ければ空の一覧を返す (今の振る舞いのまま)。
EOF
cat > plans/tags.md <<'EOF'
# 使われているタグの一覧 設計

## 1. 目的
要件 `docs/requirements/tags.md` (正本) を満たす。

## 2. 決定
- D1: 重複を除く処理を `uniq(values)` として `src/tags.js` から export し、`tagsInUse` がそれを使う。

## 3. 変更対象
| ファイル | 変更 |
|---|---|
| src/tags.js | `uniq` を足して export し、`tagsInUse` が使う |
EOF
git add -A && git commit -qm base
```

`repo/` の plans/tags.md を /define-done して、実装に着手できる状態にしてください。受け入れテストは `repo/test/` の下に `*.acceptance.test.js` として `node:test` で書いてください (`npm test` で流せること)。
