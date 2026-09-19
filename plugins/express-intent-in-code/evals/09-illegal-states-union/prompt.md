---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Skill, Read, Write, Edit, Bash]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p src
cat > package.json <<'EOF'
{ "name": "fixture", "private": true, "type": "module", "scripts": { "test": "node --test" } }
EOF
cat > src/company-state.ts <<'EOF'
export type Membership = { companyId: string; role: "OWNER" | "ADMIN" | "MEMBER" };

export type CompanyState = {
  loading: boolean;
  unauthorized: boolean;
  // 401 以外の失敗は guard を素通しさせる (membership 0 件と誤判定して誤遮断しないため)
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

`node --test` が 5 件すべて成功することを確認してから、次の依頼に取りかかってください。

src/company-state.ts の意図を型で表して。挙動は変えないで。
