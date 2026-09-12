---
type: llm
focus: {source: file, path: plans/session-store.md}
---
この設計書について、次のいずれかを満たすなら pass。

- ADR-0017 の Stage 2 (`src/session/usecase.ts` の port 化) と Stage 3 (`src/session/sweeper.ts` の TTL 対応) が本設計の対象外であることを、非目標・スコープ外として明示している。
- あるいは、Stage 2 と Stage 3 を実装タスクと受け入れ基準で覆っている。

Stage 2 と Stage 3 の両方が扱われている必要がある。片方だけなら fail。
Stage という語を使わず `usecase.ts` と `sweeper.ts` を名指しする形でも pass。
