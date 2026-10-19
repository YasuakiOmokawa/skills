---
max_turns: 30
timeout_seconds: 600
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p gitdir
git init -q -b main --separate-git-dir=gitdir/repo repo
cd repo
git config user.name dev
git config user.email dev@example.com
printf '.claude/\n' > .gitignore
mkdir -p src/auth src/settings
cat > src/auth/login.ts <<'EOF'
export function login(email: string, password: string): string {
  if (password.length === 0) {
    throw new Error("password required");
  }
  return `session:${email}`;
}
EOF
cat > src/auth/login.test.ts <<'EOF'
import { login } from "./login";

test("login returns a session", () => {
  expect(login("a@example.com", "pw")).toBe("session:a@example.com");
});
EOF
cat > src/settings/page.ts <<'EOF'
export function renderSettings(email: string): string {
  return `<h1>設定</h1><p>${email}</p>`;
}
EOF
git add .gitignore src
git commit -qm scaffold
git checkout -q -b feature/mfa-rollout
git init -q --bare ../remote.git
git remote add origin ../remote.git
cat > src/auth/mfa.ts <<'EOF'
export function verifyTotp(code: string): boolean {
  return /^\d{6}$/.test(code);
}
EOF
cat > src/auth/mfa.test.ts <<'EOF'
import { verifyTotp } from "./mfa";

test("verifyTotp accepts six digits", () => {
  expect(verifyTotp("123456")).toBe(true);
});
EOF
cat > src/auth/login.ts <<'EOF'
import { verifyTotp } from "./mfa";

export function login(email: string, password: string, totp: string): string {
  if (password.length === 0) {
    throw new Error("password required");
  }
  if (!verifyTotp(totp)) {
    throw new Error("totp required");
  }
  return `session:${email}`;
}
EOF
cat > src/auth/login.test.ts <<'EOF'
import { login } from "./login";

test("login returns a session", () => {
  expect(login("a@example.com", "pw", "123456")).toBe("session:a@example.com");
});
EOF
cat > src/settings/page.ts <<'EOF'
export function renderSettings(email: string, notifyByMail: boolean): string {
  const notify = notifyByMail ? "受け取る" : "受け取らない";
  return `<h1>設定</h1><p>${email}</p><p>通知メール: ${notify}</p>`;
}
EOF
cat > src/settings/page.test.ts <<'EOF'
import { renderSettings } from "./page";

test("settings page shows the mail notification choice", () => {
  expect(renderSettings("a@example.com", true)).toContain("受け取る");
});
EOF
```

repo の feature/mfa-rollout で、main 向けの draft PR を作成してください。commit と push はしてよいです。
