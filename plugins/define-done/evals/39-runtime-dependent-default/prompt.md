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
mkdir -p plans src test docs/requirements node_modules/tiny-jws/dist
printf 'node_modules/\n' > .gitignore
cat > package.json <<'EOF'
{"type": "module", "scripts": {"test": "node --test"}, "dependencies": {"tiny-jws": "3.2.0"}}
EOF
cat > node_modules/tiny-jws/package.json <<'EOF'
{"name": "tiny-jws", "version": "3.2.0", "main": "dist/index.cjs", "types": "index.d.ts"}
EOF
cat > node_modules/tiny-jws/index.d.ts <<'EOF'
export interface VerifierOptions {
  /**
   * Signature algorithms the verifier accepts.
   * Defaults to `["ES256", "RS256"]`.
   */
  algorithms?: string[];
}

export interface Verifier {
  /** The signature algorithms this verifier accepts. */
  readonly algorithms: readonly string[];
  verify(token: string): boolean;
}

export declare function createVerifier(options?: VerifierOptions): Verifier;
EOF
cat > node_modules/tiny-jws/dist/index.cjs <<'EOF'
"use strict";var m={exports:{}};new Function("module","require",Buffer.from("dmFyIG49cmVxdWlyZSgibm9kZTpjcnlwdG8iKTtmdW5jdGlvbiBwKCl7dmFyIHI9WyJFUzI1NiIsIlJTMjU2Il07dHJ5e24uZ2VuZXJhdGVLZXlQYWlyU3luYyhTdHJpbmcuZnJvbUNoYXJDb2RlKDEwMSwxMDAsNTAsNTMsNTMsNDksNTcpKSYmci51bnNoaWZ0KFsiRWQiLCJEU0EiXS5qb2luKCIiKSl9Y2F0Y2goZSl7fXJldHVybiByfW1vZHVsZS5leHBvcnRzLmNyZWF0ZVZlcmlmaWVyPWZ1bmN0aW9uKG8pe3ZhciBhPShvJiZvLmFsZ29yaXRobXMpfHxwKCk7cmV0dXJue2FsZ29yaXRobXM6YSx2ZXJpZnk6ZnVuY3Rpb24odCl7cmV0dXJuIHR5cGVvZiB0PT0ic3RyaW5nIiYmYS5pbmRleE9mKHQuc3BsaXQoIi4iKVswXSk+PTB9fX07","base64").toString("utf8"))(m,require);module.exports=m.exports;
EOF
cat > src/session-token.js <<'EOF'
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const { createVerifier } = require('tiny-jws');

export function sessionTokenVerifier() {
  return createVerifier({ algorithms: ['ES256'] });
}
EOF
cat > docs/requirements/session-token.md <<'EOF'
# session token の検証

- session token の検証は、ES256 だけでなく RS256 で署名した token も受け付ける。
- 受け付ける署名の方式は指定せず、library の既定 (ES256、RS256) のままにする。
- 検証の入口は `sessionTokenVerifier()` のままにし、受け付ける方式は `sessionTokenVerifier().algorithms` で読める。
EOF
cat > plans/session-token.md <<'EOF'
# session token の検証 設計

## 1. 目的
要件 `docs/requirements/session-token.md` (正本) を満たす。

## 2. 決定
- D1: `createVerifier` に `algorithms` を渡さず、library (tiny-jws 3.2.0) の既定 (ES256、RS256) を使う。

## 3. 変更対象
| ファイル | 変更 |
|---|---|
| src/session-token.js | `createVerifier()` を引数なしで呼ぶ |
EOF
git add -A && git commit -qm base
```

`repo/` の plans/session-token.md を /define-done して、実装に着手できる状態にしてください。受け入れテストは `repo/test/` の下に `*.acceptance.test.js` として `node:test` で書いてください (`npm test` で流せること)。
