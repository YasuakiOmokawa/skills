---
max_turns: 120
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
{"type": "module", "scripts": {"test": "node --test"}}
EOF
cat > src/slug.js <<'EOF'
export function toSlug(title) {
  return title.trim().toLowerCase();
}
EOF
cat > test/slug.test.js <<'EOF'
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { toSlug } from '../src/slug.js';

test('前後の空白を落とす', () => {
  assert.equal(toSlug('  hello  '), 'hello');
});

test('英字を小文字にする', () => {
  assert.equal(toSlug('Hello'), 'hello');
});
EOF
cat > docs/requirements/slug.md <<'EOF'
# 題名から URL の slug を作る

- `toSlug(title)` は、題名の中の空白の並びを `-` 1 つに置き換える。
- 前後の空白は落とす (今の振る舞いのまま)。
- 英字は小文字にする (今の振る舞いのまま)。
EOF
cat > plans/slug.md <<'EOF'
# 題名から URL の slug を作る 設計

## 1. 目的
要件 `docs/requirements/slug.md` (正本) を満たす。

## 2. 決定
- D1: `toSlug` が、前後の空白を落とした後に、空白の並びを正規表現 `/\s+/g` で `-` に置き換える。

## 3. 変更対象
| ファイル | 変更 |
|---|---|
| src/slug.js | 空白の並びを `-` に置き換える |
EOF
git add -A && git commit -qm base
```

`repo/` の plans/slug.md を /define-done してください。受け入れテストは `repo/test/` の下に `node:test` で書いてください。Gate が ready なら、続けて `repo/src/slug.js` を受け入れテストが通るまで実装し、実装が終わった状態を確かめてから報告してください。commit はしないでください。
