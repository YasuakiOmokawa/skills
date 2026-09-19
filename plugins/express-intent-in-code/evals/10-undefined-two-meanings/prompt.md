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
cat > src/auth-route.ts <<'EOF'
export type SignInMethod = "magic_link" | "github";

// hook が受け取る path は route パターンで実 path ではない ("/callback/:id")
export const MAGIC_LINK_VERIFY_ROUTE = "/magic-link/verify";
export const OAUTH_CALLBACK_ROUTE = "/callback/:id";

export type RouteMatch = {
  path: string | undefined;
  params: Record<string, string> | undefined;
};

// 未知の provider を既定値に寄せると、誤った method の sign_in audit が黙って積まれる
export function resolveMethod(route: RouteMatch): SignInMethod | undefined {
  if (route.path === MAGIC_LINK_VERIFY_ROUTE) return "magic_link";
  if (route.path !== OAUTH_CALLBACK_ROUTE) return undefined;
  return route.params?.id === "github" ? "github" : undefined;
}
EOF
cat > src/sign-in-observer.ts <<'EOF'
import { resolveMethod, type RouteMatch } from "./auth-route.ts";

export type AuditEvent =
  | { kind: "sign_in"; method: "magic_link" | "github"; userId: string }
  | { kind: "unmapped_route"; path: string; providerId: string | undefined };

export function observeSignIn(route: RouteMatch, userId: string, warn: (message: string) => void): AuditEvent | null {
  const method = resolveMethod(route);
  if (method === undefined) {
    // 対象 route でない場合と provider が未知の場合を区別できないので、ここでは警告だけ出す
    if (route.path === "/callback/:id") warn(`unknown provider on ${route.path}`);
    return null;
  }
  return { kind: "sign_in", method, userId };
}
EOF
cat > src/sign-in-observer.test.ts <<'EOF'
import { test } from "node:test";
import assert from "node:assert/strict";
import { observeSignIn } from "./sign-in-observer.ts";

const noWarn = () => {};

test("magic link maps to magic_link", () => {
  assert.deepEqual(observeSignIn({ path: "/magic-link/verify", params: undefined }, "u1", noWarn), {
    kind: "sign_in",
    method: "magic_link",
    userId: "u1",
  });
});
test("github callback maps to github", () => {
  assert.deepEqual(observeSignIn({ path: "/callback/:id", params: { id: "github" } }, "u1", noWarn), {
    kind: "sign_in",
    method: "github",
    userId: "u1",
  });
});
test("unrelated route is ignored without warning", () => {
  const warnings: string[] = [];
  assert.equal(observeSignIn({ path: "/session", params: undefined }, "u1", (m) => warnings.push(m)), null);
  assert.deepEqual(warnings, []);
});
test("unknown provider warns", () => {
  const warnings: string[] = [];
  assert.equal(observeSignIn({ path: "/callback/:id", params: { id: "gitlab" } }, "u1", (m) => warnings.push(m)), null);
  assert.equal(warnings.length, 1);
});
EOF
```

`node --test` が 4 件すべて成功することを確認してから、次の依頼に取りかかってください。

src/auth-route.ts の resolveMethod は「対象 route でない」と「provider が未知」を同じ undefined で返していて、observer 側が path を見直して区別している。意図をコードで表して。既存テストの結果は変えないで。
