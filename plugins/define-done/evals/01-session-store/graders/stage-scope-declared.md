---
type: llm
focus: {source: file, path: plans/session-store.md}
---
この設計書の `## MECE Review` について、次のどちらかを満たすなら pass。

- ADR-0017 の Stage 2 (`src/session/usecase.ts` の port 化) と Stage 3 (`src/session/sweeper.ts` の TTL 対応) が本設計の対象外だという宣言が計画に無いことを、欠落 (または必要な上流の修正) として挙げている。
- 計画が Stage 2 と Stage 3 を対象外と宣言済みであることを確かめている。

Stage 2 と Stage 3 の両方が扱われている必要がある。片方だけなら fail。Stage という語を使わず `usecase.ts` と `sweeper.ts` を名指しする形でも pass。
