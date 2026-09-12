---
name: chain-design-phase
tags: [chain]
plugins:
  - "../../plugins/ground-design-in-codebase"
  - "../../plugins/define-acceptance-criteria"
  - "../../plugins/mece-plan-review"
  - "../../plugins/prepare-plan-for-implementation"
max_turns: 100
timeout_seconds: 3000
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p plans docs/adr docs/requirements src/session/__tests__ config
cat > docs/adr/0017-session-store.md <<'EOF'
# ADR-0017: セッションストアの外部化

## Status
Accepted

## Decision
セッションをプロセス内メモリから外部ストアへ移す。移行は次の 3 段階で行う。

- Stage 1: transport 層 (`src/session/store.ts`) の読み書きを外部ストアに切り替える。
- Stage 2: use-case 層 (`src/session/usecase.ts`) が store を直接参照している箇所を port 経由にする。
- Stage 3: 期限切れセッションの掃除 (`src/session/sweeper.ts`) を外部ストアの TTL に合わせる。

## Consequences
接続先はデプロイ環境ごとに変わるため、環境変数で与える。必要な環境変数は `config/env.example` に列挙する。
EOF
cat > docs/requirements/session-store.md <<'EOF'
# セッションストア外部化 要件

## 背景
セッションがプロセス内メモリにあるため、アプリを複数プロセスで動かすとログイン状態が失われる。

## 要件
- R-1: アプリを再起動してもセッションが失われないようにしたい。
- R-2: 複数プロセスで動かしても、どのプロセスが受けても同じセッションが読めるようにしたい。
- R-3: 接続先は本番と開発で切り替えられるようにしたい。

## 制約
- 設計方針は `docs/adr/0017-session-store.md` に従う。
- 本件は ADR の Stage 1 のみを対象とする。
EOF
cat > src/session/store.ts <<'EOF'
const memory = new Map<string, string>();

export const store = {
  async get(sid: string): Promise<string | undefined> {
    return memory.get(sid);
  },
  async set(sid: string, value: string): Promise<void> {
    memory.set(sid, value);
  },
  async delete(sid: string): Promise<void> {
    memory.delete(sid);
  },
  async keys(): Promise<string[]> {
    return [...memory.keys()];
  },
};
EOF
cat > src/session/usecase.ts <<'EOF'
import { store } from "./store";

export async function loadSession(sid: string): Promise<string | undefined> {
  return store.get(sid);
}

export async function saveSession(sid: string, value: string): Promise<void> {
  await store.set(sid, value);
}
EOF
cat > src/session/sweeper.ts <<'EOF'
import { store } from "./store";

export async function sweepExpired(olderThanMs: number): Promise<number> {
  const keys = await store.keys();
  let removed = 0;
  for (const sid of keys) {
    const value = await store.get(sid);
    if (value && Number(value.split(":")[0]) < Date.now() - olderThanMs) {
      await store.delete(sid);
      removed++;
    }
  }
  return removed;
}
EOF
cat > src/session/__tests__/containment.test.ts <<'EOF'
import { collectExternalImports } from "./helpers";

// src/session/ が依存してよい外部パッケージの全列挙。
// この一覧に無い依存が増えると、このテストは fail する。
const ALLOWED_EXTERNAL_DEPS: string[] = [];

test("src/session は外部パッケージに依存しない", () => {
  expect(collectExternalImports("src/session")).toEqual(ALLOWED_EXTERNAL_DEPS);
});
EOF
cat > src/session/__tests__/helpers.ts <<'EOF'
import { readdirSync, readFileSync } from "node:fs";

export function collectExternalImports(dir: string): string[] {
  const found = new Set<string>();
  for (const file of readdirSync(dir)) {
    if (!file.endsWith(".ts")) continue;
    const src = readFileSync(`${dir}/${file}`, "utf8");
    for (const m of src.matchAll(/from "([^"]+)"/g)) {
      if (!m[1].startsWith(".") && !m[1].startsWith("node:")) found.add(m[1]);
    }
  }
  return [...found].sort();
}
EOF
cat > config/env.example <<'EOF'
DATABASE_URL=postgres://localhost:5432/app
REDIS_URL=redis://localhost:6379
LOG_LEVEL=info
EOF
```

docs/requirements/session-store.md の要件から設計して plans/session-store.md へ出力。実装は指示まで禁止。

設計を /ground-design-in-codebase => /define-acceptance-criteria => /mece-plan-review => /prepare-plan-for-implementation して、設計を確定する。
