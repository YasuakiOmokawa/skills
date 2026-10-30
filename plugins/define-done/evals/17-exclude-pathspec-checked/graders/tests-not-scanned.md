---
type: llm
focus: {source: file, path: repo/plans/no-app-env.md}
---
repo/plans/no-app-env.md の `## Acceptance Criteria` と `## Verification Plan` を評価する。S-1 (製品コードに `APP_ENV` が残らない) に対応する基準の観測が、変更後も `APP_ENV` を残す 2 つの試験ファイル `src/__tests__/env.test.ts` と `src/config/__tests__/log-level.test.ts` のどちらにも当たらない形なら pass。

判定の注意: git の pathspec では、`glob` 魔法の無い `src/**/__tests__/**` (`:(exclude)src/**/__tests__/**`、`:!src/**/__tests__/**` など) は `src/__tests__/env.test.ts` に一致しない。この形だけで試験を除いている観測は、`src/__tests__/env.test.ts` に当たって落ちるので fail。`:(exclude,glob)src/**/__tests__/**`、`:!*__tests__*`、走査対象を製品コードのファイルに限る、などで両方を除いていれば pass。S-1 に対応する基準が無ければ fail。
