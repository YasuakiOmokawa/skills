---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p plans docs/adr src/session config
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
cat > plans/session-store.md <<'EOF'
# セッションストア外部化 設計

## 1. 目的
ADR-0017 に従い、セッションを外部ストアへ移す。

## 2. 仕様
- 根拠: `docs/adr/0017-session-store.md`
- S-1: `src/session/store.ts` の読み書きが外部ストアに対して行われる。
- S-2: 接続先は環境変数 `SESSION_STORE_URL` から読む。

## 3. 変更対象
| ファイル | 変更 |
|---|---|
| src/session/store.ts | 外部ストア接続に置き換える |

## 4. 実装タスク
- T-1: `src/session/store.ts` を外部ストア接続に書き換える。
- T-2: `SESSION_STORE_URL` を読み込み、未設定なら起動時に落とす。

## Acceptance Criteria
- [ ] AC-001: `src/session/store.ts` の `get` と `set` が外部ストアに対して読み書きする。
- [ ] AC-002: `SESSION_STORE_URL` が未設定のとき、起動時に例外を送出する。

## MECE Review
- AC IDs: (なし)
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
cat > config/env.example <<'EOF'
DATABASE_URL=postgres://localhost:5432/app
REDIS_URL=redis://localhost:6379
LOG_LEVEL=info
EOF
```

plans/session-store.md 設計を /mece-plan-review して、レビュー結果を設計書に反映して、設計を確定する。
