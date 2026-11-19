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
mkdir -p plans src test docs/issues
cat > package.json <<'EOF'
{"type": "module", "scripts": {"test": "node --test"}}
EOF
cat > src/tags.js <<'EOF'
export function tagsInUse(posts) {
  return posts.flatMap((post) => post.tags);
}
EOF
cat > test/tags.test.js <<'EOF'
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { tagsInUse } from '../src/tags.js';

test('記事が無ければタグも無い', () => {
  assert.deepEqual(tagsInUse([]), []);
});
EOF
cat > docs/issues/123.md <<'EOF'
# 使われているタグの一覧を重複なく返す (#123)

記事の一覧から、使われているタグを重複なく返す。管理画面でのタグの一覧はまだ作らない。

## やること

- `tagsInUse(posts)` が、記事 (`{ tags: string[] }`) の一覧から、使われているタグを重複なく返す。返す順は問わない
- 記事が無ければ空の一覧を返す (今の振る舞いのまま)

## 受け入れ条件

- 同じタグが複数の記事にあっても、返す一覧にはそのタグが 1 回だけ現れる (`News` と `news` は別のタグとして数える)
- 記事が無ければ空の一覧を返す
- `npm test` が通る
EOF
cat > plans/tags.md <<'EOF'
# 使われているタグの一覧 設計

## 1. 目的
issue `docs/issues/123.md` (正本) を満たす。

## 2. 決定
- D1: `tagsInUse` が `Set` で重複を除く。

## 3. 変更対象
| ファイル | 変更 |
|---|---|
| src/tags.js | 重複を除いて返す |

## 4. 範囲外
- 管理画面でのタグの一覧 (別 issue)
EOF
git add -A && git commit -qm base
```

`repo/` の plans/tags.md を /define-done して、実装に着手できる状態にしてください。受け入れテストは `repo/test/` の下に `*.acceptance.test.js` として `node:test` で書いてください。判断はすべて推奨で決めてください。
