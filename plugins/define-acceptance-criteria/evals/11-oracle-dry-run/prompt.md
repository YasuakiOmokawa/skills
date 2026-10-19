---
max_turns: 30
timeout_seconds: 600
allowed_tools: [Skill, Read, Write, Edit, Bash]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p repo
cd repo
git init -q --template= --separate-git-dir=../repo.gitdir -b main .
mkdir -p src/__tests__ plans
cat > src/auth.ts <<'EOF'
export function legacySignIn(email: string): string {
  return `legacy:${email}`;
}

export function signIn(email: string): string {
  return `session:${email}`;
}
EOF
cat > src/login.ts <<'EOF'
import { legacySignIn } from "./auth";

export const login = (email: string) => legacySignIn(email);
EOF
cat > src/__tests__/auth.test.ts <<'EOF'
import { signIn } from "../auth";

test("signIn returns a session", () => {
  expect(signIn("a@example.com")).toBe("session:a@example.com");
});
EOF
cat > src/README.md <<'EOF'
# src

ログインは `legacySignIn` から `signIn` へ移行中。
EOF
cat > plans/remove-legacy.md <<'EOF'
# 旧ログイン関数の削除 設計

## 1. 目的
`legacySignIn` を削除し、`login` を `signIn` に寄せる。

## 2. 仕様
- S-1: 変更後、`src/` に `legacySignIn` が残らない。
- S-2: 変更後、`src/auth` の module が `legacySignIn` を export しないことを test で確かめる。
- S-3: `src/README.md` の移行メモは別 issue で書き直すので、今回は変えない。
- S-4: `login("a@example.com")` は `session:a@example.com` を返す。
EOF
git add -A
git -c user.name=fixture -c user.email=fixture@example.com commit -qm init
```

`repo/plans/remove-legacy.md` に /define-acceptance-criteria で受け入れ基準を作って。plan の更新は許可する。
