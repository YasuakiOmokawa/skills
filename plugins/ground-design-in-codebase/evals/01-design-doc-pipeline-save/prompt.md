---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Skill, Read, Write, Edit, Bash]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリ直下に小さなリポジトリを用意してください。

```bash
mkdir -p docs src/__tests__
cat > docs/spec.md <<'EOF'
# 認証仕様

- S-1: 認証が必要なすべての API エンドポイントは、期限切れセッションのリクエストを 401 で拒否する。
- S-2: セッション token の署名検証と期限検証は、どちらも欠けてはならない。
EOF
cat > src/session.ts <<'EOF'
export type Session = { userId: string; exp: number };

// 署名だけを検証する。期限 (exp) の検査は requireFreshSession (middleware.ts) が担う。
export function validateSession(token: string): Session | null {
  const [payload, sig] = token.split(".");
  if (!payload || !sig || sig !== sign(payload)) return null;
  const { userId, exp } = JSON.parse(Buffer.from(payload, "base64url").toString());
  return { userId, exp };
}

function sign(payload: string): string {
  return "sig-" + payload.length;
}
EOF
cat > src/middleware.ts <<'EOF'
import { validateSession } from "./session";

export const PROTECTED_ROUTES = ["/api/me", "/api/companies"] as const;

// 保護対象 route の前段。署名と期限の両方をここで検査する。
export function requireFreshSession(token: string, now: number) {
  const s = validateSession(token);
  if (!s) return { status: 401 as const };
  if (s.exp <= now) return { status: 401 as const };
  return { status: 200 as const, session: s };
}
EOF
cat > src/__tests__/middleware.test.ts <<'EOF'
import { describe, it, expect } from "vitest";
import { requireFreshSession, PROTECTED_ROUTES } from "../middleware";

describe("requireFreshSession", () => {
  it("期限切れ token は 401", () => {
    const payload = Buffer.from(JSON.stringify({ userId: "u1", exp: 100 })).toString("base64url");
    const token = payload + ".sig-" + payload.length;
    expect(requireFreshSession(token, 200).status).toBe(401);
  });
  it("保護 route の一覧は固定", () => {
    expect(PROTECTED_ROUTES).toEqual(["/api/me", "/api/companies"]);
  });
});
EOF
cat > design.md <<'EOF'
# 設計: エクスポート API の新設

## 1. 範囲

- 対象: /api/export の新設
- 対象外: 既存 route の変更

## 2. 前提事実

- validateSession (src/session.ts) は署名と期限の両方を検証し、期限切れなら null を返す。
- PROTECTED_ROUTES は middleware の適用対象を列挙している。

## 3. 設計

- GET /api/export を新設する。
- ハンドラは validateSession を直接呼び、null なら 401、それ以外は CSV を返す。前提事実により期限検査は済んでいるので requireFreshSession は経由しない。
- PROTECTED_ROUTES には追加しない (エクスポートは独立 route として扱う)。

## 4. 検証計画

- tsc --noEmit が通ること。

## 6. Ground review (境界適合と risk)

- 未実施。ground-design-in-codebase の結果をここではなく所定の節に記録する。

## Acceptance Criteria

- AC-1: 期限切れ token で GET /api/export が 401 を返す。
- AC-2: 有効な token で GET /api/export が 200 と CSV を返す。
EOF
```

用意できたら、設計を /ground-design-in-codebase して、設計を確定する。レビューは design.md に記録すること。
