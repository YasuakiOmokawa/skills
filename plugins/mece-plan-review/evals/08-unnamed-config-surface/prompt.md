---
max_turns: 40
timeout_seconds: 900
allowed_tools: [Skill, Read, Grep, Glob, Bash, Write, Edit]
runs: 3
---
まず次のコマンドをそのまま実行して、作業ディレクトリに fixture を用意してください。

```bash
mkdir -p plans src/cache config
cat > plans/cache-ttl.md <<'EOF'
# キャッシュ有効期限の外部設定化 設計

## 1. 目的
キャッシュの有効期限をコード内の定数から環境変数に移し、環境ごとに変えられるようにする。

## 2. 仕様
- S-1: `src/cache/ttl.ts` の `resolveTtlSeconds` は環境変数 `CACHE_TTL_SECONDS` を読み、正の整数ならその値を返す。
- S-2: `CACHE_TTL_SECONDS` が未設定、数値でない、または 0 以下のときは既定値 300 を返す。

## 3. 変更対象
| ファイル | 変更 |
|---|---|
| src/cache/ttl.ts | 環境変数の読み取りと既定値 |

## 4. 実装タスク
- T-1: `src/cache/ttl.ts` に `resolveTtlSeconds` を実装する。
- T-2: `src/cache/index.ts` が定数ではなく `resolveTtlSeconds` を使うように差し替える。

## Acceptance Criteria
- [ ] AC-001: `CACHE_TTL_SECONDS` が `"600"` のとき `resolveTtlSeconds` は 600 を返す。
- [ ] AC-002: `CACHE_TTL_SECONDS` が未設定、`"abc"`、`"0"`、`"-1"` のいずれのときも `resolveTtlSeconds` は 300 を返す。
- [ ] AC-003: `src/cache/index.ts` は有効期限をコード内の定数から取らず、`resolveTtlSeconds` の戻り値を使う。

## MECE Review
- AC IDs: (なし)
EOF
cat > src/cache/ttl.ts <<'EOF'
export const DEFAULT_TTL_SECONDS = 300;

export function resolveTtlSeconds(): number {
  const raw = process.env.CACHE_TTL_SECONDS;
  if (raw === undefined) return DEFAULT_TTL_SECONDS;
  const parsed = Number.parseInt(raw, 10);
  if (!Number.isInteger(parsed) || parsed <= 0) return DEFAULT_TTL_SECONDS;
  return parsed;
}
EOF
cat > src/cache/index.ts <<'EOF'
import { resolveTtlSeconds } from "./ttl";

const entries = new Map<string, { value: string; expiresAt: number }>();

export function put(key: string, value: string): void {
  entries.set(key, {
    value,
    expiresAt: Date.now() + resolveTtlSeconds() * 1000,
  });
}

export function get(key: string): string | undefined {
  const hit = entries.get(key);
  if (!hit) return undefined;
  if (hit.expiresAt <= Date.now()) {
    entries.delete(key);
    return undefined;
  }
  return hit.value;
}
EOF
cat > config/env.example <<'EOF'
DATABASE_URL=postgres://localhost:5432/app
LOG_LEVEL=info
EOF
```

plans/cache-ttl.md 設計を /mece-plan-review して、レビュー結果を設計書に反映して、設計を確定する。
