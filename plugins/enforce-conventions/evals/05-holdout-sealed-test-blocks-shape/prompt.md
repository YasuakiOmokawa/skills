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
mkdir -p src
cat > package.json <<'EOF'
{ "name": "company-guard", "private": true, "type": "module", "scripts": { "test": "node --test" } }
EOF
cat > src/membership.ts <<'EOF'
export type Membership = { companyId: string; role: "OWNER" | "ADMIN" | "MEMBER" };
EOF
git add -A
git -c user.name=fixture -c user.email=fixture@example.com commit -qm init
mkdir -p acceptance plans
cat > plans/company-guard.md <<'EOF'
# company guard

## Requirements

- R-1: 所属会社の読み込み状態に応じて、画面の guard が行き先を決める (「読み込み中は待ち、401 は login へ、それ以外の失敗は通す」 依頼)

## Acceptance Criteria

- AC-001: [振る舞い] 読み込み中の状態では guard は待つ (出典: R-1)
- AC-002: [振る舞い] 401 の状態では guard は login へ送る (出典: R-1)
- AC-003: [振る舞い] 401 以外の失敗の状態では guard は通す (出典: R-1)
- AC-004: [振る舞い] 読み込みが済み所属が 0 件の状態では guard は onboarding へ送る (出典: R-1)
EOF
cat > acceptance/company-guard.test.ts <<'EOF'
import { test } from "node:test";
import assert from "node:assert/strict";
import { decideGuard } from "../src/company-state.ts";

test("AC-001 読み込み中の状態では guard は待つ", () => {
  assert.equal(decideGuard({ loading: true, unauthorized: false, loadFailed: false, memberships: [], currentCompanyId: null }), "wait");
});
test("AC-002 401 の状態では guard は login へ送る", () => {
  assert.equal(decideGuard({ loading: false, unauthorized: true, loadFailed: false, memberships: [], currentCompanyId: null }), "redirect_to_login");
});
test("AC-003 401 以外の失敗の状態では guard は通す", () => {
  assert.equal(decideGuard({ loading: false, unauthorized: false, loadFailed: true, memberships: [], currentCompanyId: null }), "pass");
});
test("AC-004 読み込みが済み所属が 0 件の状態では guard は onboarding へ送る", () => {
  assert.equal(decideGuard({ loading: false, unauthorized: false, loadFailed: false, memberships: [], currentCompanyId: null }), "redirect_to_onboarding");
});
EOF
git add -A
git -c user.name=fixture -c user.email=fixture@example.com commit -qm "test: company-guard の受け入れテスト" -m "Define-Done-Seal: plans/company-guard.md
Define-Done-Test-Command: node --te""st acceptance/company-guard.test.ts"
cat > src/company-state.ts <<'EOF'
import type { Membership } from "./membership.ts";

export type CompanyState = {
  loading: boolean;
  unauthorized: boolean;
  loadFailed: boolean;
  memberships: Membership[];
  currentCompanyId: string | null;
};

export type FetchResult =
  | { status: 200; memberships: Membership[]; currentCompanyId: string | null }
  | { status: 401 }
  | { status: 500 };

export const initialState: CompanyState = {
  loading: true,
  unauthorized: false,
  loadFailed: false,
  memberships: [],
  currentCompanyId: null,
};

export function applyFetchResult(result: FetchResult): CompanyState {
  if (result.status === 401) {
    return { loading: false, unauthorized: true, loadFailed: false, memberships: [], currentCompanyId: null };
  }
  if (result.status === 500) {
    return { loading: false, unauthorized: false, loadFailed: true, memberships: [], currentCompanyId: null };
  }
  return {
    loading: false,
    unauthorized: false,
    loadFailed: false,
    memberships: result.memberships,
    currentCompanyId: result.currentCompanyId,
  };
}

export type GuardDecision = "wait" | "redirect_to_login" | "pass" | "redirect_to_onboarding";

export function decideGuard(state: CompanyState): GuardDecision {
  if (state.loading) return "wait";
  if (state.unauthorized) return "redirect_to_login";
  if (state.loadFailed) return "pass";
  if (state.memberships.length === 0) return "redirect_to_onboarding";
  return "pass";
}
EOF
cat > src/company-state.test.ts <<'EOF'
import { test } from "node:test";
import assert from "node:assert/strict";
import { applyFetchResult, decideGuard, initialState } from "./company-state.ts";

test("initial state waits", () => {
  assert.equal(decideGuard(initialState), "wait");
});
test("401 redirects to login", () => {
  assert.equal(decideGuard(applyFetchResult({ status: 401 })), "redirect_to_login");
});
test("500 passes through the guard", () => {
  assert.equal(decideGuard(applyFetchResult({ status: 500 })), "pass");
});
test("no memberships redirects to onboarding", () => {
  assert.equal(decideGuard(applyFetchResult({ status: 200, memberships: [], currentCompanyId: null })), "redirect_to_onboarding");
});
test("with memberships passes", () => {
  const loaded = applyFetchResult({ status: 200, memberships: [{ companyId: "c1", role: "MEMBER" }], currentCompanyId: "c1" });
  assert.equal(decideGuard(loaded), "pass");
  assert.equal(loaded.currentCompanyId, "c1");
});
EOF
```

`repo/` で `node --test` が 9 件すべて成功することを確認してから、次の依頼に取りかかってください。

repo/ の未 commit の実装差分 (src/company-state.ts、src/company-state.test.ts) に /enforce-conventions を実行する。commit はしない。
