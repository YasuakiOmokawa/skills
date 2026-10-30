---
max_turns: 60
timeout_seconds: 1800
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p repo
cd repo
git init -q --template= --separate-git-dir=../repo.gitdir -b main .
mkdir -p src plans
cat > src/session.ts <<'EOF'
import { getCookie } from "cookie-kit";

export function currentUserId(req: Request): string | undefined {
  return getCookie(req, "sid")?.split(":")[0];
}
EOF
cat > src/profile.ts <<'EOF'
import { getCookie } from "cookie-kit";

export function profileOwner(req: Request): string | undefined {
  return getCookie(req, "sid")?.split(":")[0];
}
EOF
cat > src/logout.ts <<'EOF'
import { deleteCookie } from "cookie-kit";

export function logout(res: Response): void {
  deleteCookie(res, "sid");
}
EOF
cat > plans/read-session.md <<'EOF'
# セッション読み取りの一本化 設計

## 1. 目的
セッション cookie の読み取りを `src/read-session.ts` の `readSession` に一本化する。

## 2. 仕様
- S-1: `readSession(req)` は cookie `sid` の値の `:` より前を利用者 ID として返し、cookie が無ければ `undefined` を返す。
- S-2: 変更後、`src/` の中で `readSession` 以外が `cookie-kit` の `getCookie` を直接使わない。
- S-3: `currentUserId` と `profileOwner` は `readSession` を使う。

## 3. 変更対象
| ファイル | 変更 |
|---|---|
| src/read-session.ts | `readSession` を新規作成 |
| src/session.ts | `readSession` を使う |
| src/profile.ts | `readSession` を使う |
EOF
git add -A
git -c user.name=fixture -c user.email=fixture@example.com commit -qm init
```

`repo/plans/read-session.md` の設計を /define-done。
