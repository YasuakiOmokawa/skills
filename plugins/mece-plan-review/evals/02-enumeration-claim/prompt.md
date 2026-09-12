---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p plans src/mfa/management src/mfa/shared src/mfa/__tests__
cat > plans/mfa-policy.md <<'EOF'
# MFA 試行回数上限の集約 設計

## 1. 目的
MFA の試行回数上限がモジュールごとにインライン定義されている状態を、一箇所に集約する。

## 2. 仕様
- S-1: 試行回数上限の定数は `src/mfa/policy/limits.ts` に一箇所だけ定義する。
- S-2: 上限値は現行の 5 から変更しない。

## 3. 変更対象
| ファイル | 変更 |
|---|---|
| src/mfa/policy/limits.ts | 新規作成 |
| src/mfa/management/enroll.ts | インライン定数を policy からの import に置き換える |

## 4. 実装タスク
- T-1: `src/mfa/policy/limits.ts` を新規作成し `MAX_ATTEMPTS = 5` を定義する。
- T-2: `src/mfa/management/enroll.ts` のインライン定数を `policy/limits` からの import に置き換える。

## Acceptance Criteria
- [ ] AC-001: `src/mfa/policy/limits.ts` が `MAX_ATTEMPTS = 5` を export する。
- [ ] AC-002: `src/mfa/management/enroll.ts` が `policy/limits` から `MAX_ATTEMPTS` を import し、インライン定数を持たない。
- [ ] AC-003: `policy/limits` を import するのは `src/mfa/management/enroll.ts` だけである。
- [ ] AC-004: 本変更で `src/mfa/__tests__/containment.test.ts` は変更されない。

## MECE Review
- AC IDs: (なし)
EOF
cat > src/mfa/management/enroll.ts <<'EOF'
import { store } from "./store";
import { TooManyAttemptsError } from "./errors";

const MAX_ATTEMPTS = 5;

export async function enroll(userId: string, code: string): Promise<void> {
  const attempts = await store.countAttempts(userId);
  if (attempts >= MAX_ATTEMPTS) {
    throw new TooManyAttemptsError(userId);
  }
  await store.saveEnrollment(userId, code);
}
EOF
cat > src/mfa/management/verify.ts <<'EOF'
import { store } from "./store";
import { TooManyAttemptsError } from "./errors";
import { now } from "../shared/clock";

const MAX_ATTEMPTS = 5;

export async function verify(userId: string, code: string): Promise<boolean> {
  const attempts = await store.countAttempts(userId);
  if (attempts >= MAX_ATTEMPTS) {
    throw new TooManyAttemptsError(userId);
  }
  await store.recordAttempt(userId, now());
  return store.matches(userId, code);
}
EOF
cat > src/mfa/management/store.ts <<'EOF'
export const store = {
  async countAttempts(userId: string): Promise<number> {
    return 0;
  },
  async recordAttempt(userId: string, at: number): Promise<void> {},
  async saveEnrollment(userId: string, code: string): Promise<void> {},
  async matches(userId: string, code: string): Promise<boolean> {
    return true;
  },
};
EOF
cat > src/mfa/management/errors.ts <<'EOF'
export class TooManyAttemptsError extends Error {
  constructor(readonly userId: string) {
    super("too many attempts");
  }
}
EOF
cat > src/mfa/shared/clock.ts <<'EOF'
export function now(): number {
  return Date.now();
}
EOF
cat > src/mfa/__tests__/containment.test.ts <<'EOF'
import { collectImports } from "./helpers";

// src/mfa/management/ が import してよいモジュールの全列挙。
// この一覧に無い import が増えると、このテストは fail する。
const ALLOWED_MANAGEMENT_IMPORTS = [
  "../shared/clock",
  "./errors",
  "./store",
];

test("management の import は許可一覧と完全に一致する", () => {
  expect(collectImports("src/mfa/management")).toEqual(
    ALLOWED_MANAGEMENT_IMPORTS,
  );
});
EOF
cat > src/mfa/__tests__/helpers.ts <<'EOF'
import { readdirSync, readFileSync } from "node:fs";

export function collectImports(dir: string): string[] {
  const found = new Set<string>();
  for (const file of readdirSync(dir)) {
    if (!file.endsWith(".ts")) continue;
    const src = readFileSync(`${dir}/${file}`, "utf8");
    for (const m of src.matchAll(/from "([^"]+)"/g)) found.add(m[1]);
  }
  return [...found].sort();
}
EOF
```

plans/mfa-policy.md 設計を /mece-plan-review して、レビュー結果を設計書に反映して、設計を確定する。
