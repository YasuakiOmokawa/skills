---
type: llm
focus: {source: file, path: repo/plans/no-app-env.md}
---
repo/plans/no-app-env.md の `## Acceptance Criteria` と `## Verification Plan` を評価する。S-1 (製品コードに `APP_ENV` が残らない) に対応する基準の観測が、変更後も `APP_ENV` を残す 2 つの試験ファイル `src/__tests__/env.test.ts` と `src/config/__tests__/log-level.test.ts` のどちらにも当たらない形なら pass。

判定の注意: git の pathspec では、`glob` 魔法の無い `src/*.ts` は `src/__tests__/env.test.ts` にも一致する (`*` が `/` をまたぐ)。走査範囲がこの形だけなら試験に当たって落ちるので fail。`:(glob)src/*.ts` と `:(glob)src/config/*.ts` のように試験の dir を含まない範囲だけを挙げる、禁じる文字列を製品コードにしか現れない形に絞る、などで両方の試験に当たらなければ pass。S-1 に対応する基準が無ければ fail。
