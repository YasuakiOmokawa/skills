---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p repo
cd repo
git init -q --template= --separate-git-dir=../repo.gitdir -b main .
mkdir -p src/__tests__ plans
cat > plans/mfa-rollout.md <<'EOF'
# MFA 導入

## 作業項目

1. セッション有効期間を定数にする (挙動は変えない)
   - 対象: `src/config.ts`、`src/session.ts` の有効期間の指定
2. TOTP の検証を login に組み込む
   - 対象: `src/totp.ts`、`src/__tests__/totp.test.ts`、`src/login.ts`、`src/session.ts` の `markMfaVerified`
3. 用語集に TOTP を足す
   - 対象: `GLOSSARY.md`
EOF
cat > CONTRIBUTING.md <<'EOF'
# 開発の約束

- PR は squash merge で取り込む。
EOF
cat > GLOSSARY.md <<'EOF'
# 用語集

**Session**:
ログイン後に発行する、有効期間つきの利用者の状態。
EOF
cat > src/users.ts <<'EOF'
export type User = { id: string; password: string; totpSecret: string };

const users: User[] = [
  { id: "u1", password: "pw", totpSecret: "12345678901234567890" },
];

export function findUser(email: string): User | undefined {
  return email === "a@example.com" ? users[0] : undefined;
}
EOF
cat > src/session.ts <<'EOF'
export type Session = {
  userId: string;
  expiresAt: number;
};

export function createSession(userId: string, now: number): Session {
  return { userId, expiresAt: now + 3600 * 1000 };
}

export function isExpired(session: Session, now: number): boolean {
  return session.expiresAt <= now;
}

export function extend(session: Session, now: number): Session {
  return { ...session, expiresAt: now + 3600 * 1000 };
}

export function revoke(session: Session): Session {
  return { ...session, expiresAt: 0 };
}

export function describe(session: Session): string {
  return `${session.userId}:${session.expiresAt}`;
}
EOF
cat > src/login.ts <<'EOF'
import { createSession } from "./session";
import { findUser } from "./users";

export function login(email: string, password: string, now: number) {
  const user = findUser(email);
  if (!user || user.password !== password) {
    return null;
  }
  return createSession(user.id, now);
}
EOF
cat > src/__tests__/session.test.ts <<'EOF'
import { describe, expect, it } from "vitest";
import { createSession, isExpired } from "../session";

describe("createSession", () => {
  it("expires after an hour", () => {
    const session = createSession("u1", 0);
    expect(isExpired(session, 3599 * 1000)).toBe(false);
    expect(isExpired(session, 3600 * 1000)).toBe(true);
  });
});
EOF
git add -A
git commit -qm init
git switch -q -c feature/mfa-rollout
cat > src/config.ts <<'EOF'
export const SESSION_TTL_MS = 3600 * 1000;
EOF
cat > src/session.ts <<'EOF'
import { SESSION_TTL_MS } from "./config";

export type Session = {
  userId: string;
  expiresAt: number;
};

export function createSession(userId: string, now: number): Session {
  return { userId, expiresAt: now + SESSION_TTL_MS };
}

export function isExpired(session: Session, now: number): boolean {
  return session.expiresAt <= now;
}

export function extend(session: Session, now: number): Session {
  return { ...session, expiresAt: now + SESSION_TTL_MS };
}

export function revoke(session: Session): Session {
  return { ...session, expiresAt: 0 };
}

export function describe(session: Session): string {
  return `${session.userId}:${session.expiresAt}`;
}

export function markMfaVerified(session: Session): Session & { mfaVerified: true } {
  return { ...session, mfaVerified: true };
}
EOF
cat > src/totp.ts <<'EOF'
import { createHmac } from "node:crypto";

const STEP_SECONDS = 30;

export function generateTotp(secret: string, now: number): string {
  const counter = Math.floor(now / 1000 / STEP_SECONDS);
  const message = Buffer.alloc(8);
  message.writeBigUInt64BE(BigInt(counter));
  const digest = createHmac("sha1", secret).update(message).digest();
  const offset = digest[digest.length - 1] & 0x0f;
  const binary = digest.readUInt32BE(offset) & 0x7fffffff;
  return String(binary % 1_000_000).padStart(6, "0");
}

export function verifyTotp(secret: string, code: string, now: number): boolean {
  return generateTotp(secret, now) === code;
}
EOF
cat > src/__tests__/totp.test.ts <<'EOF'
import { describe, expect, it } from "vitest";
import { generateTotp, verifyTotp } from "../totp";

describe("verifyTotp", () => {
  const secret = "12345678901234567890";
  const now = 59 * 1000;

  it("accepts the code for the current step", () => {
    expect(verifyTotp(secret, generateTotp(secret, now), now)).toBe(true);
  });

  it("rejects a wrong code", () => {
    expect(verifyTotp(secret, "000000", now)).toBe(false);
  });
});
EOF
cat > src/login.ts <<'EOF'
import { createSession, markMfaVerified } from "./session";
import { findUser } from "./users";
import { verifyTotp } from "./totp";

export function login(email: string, password: string, code: string, now: number) {
  const user = findUser(email);
  if (!user || user.password !== password) {
    return null;
  }
  if (!verifyTotp(user.totpSecret, code, now)) {
    return null;
  }
  return markMfaVerified(createSession(user.id, now));
}
EOF
cat > GLOSSARY.md <<'EOF'
# 用語集

**Session**:
ログイン後に発行する、有効期間つきの利用者の状態。

**TOTP**:
30 秒ごとに変わる 6 桁の確認コード。認証アプリが共有鍵と時刻から作る。
EOF
```

`repo/plans/mfa-rollout.md` の計画どおりの実装が `repo/` の作業ツリーで終わりました。/create-commits
