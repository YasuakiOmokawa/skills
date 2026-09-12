---
type: llm
focus: {source: file, path: plans/session-store.md}
---
この設計書に書き込まれた MECE レビューについて、次を満たすなら pass。

- ADR-0017 が定める Stage 2 (`src/session/usecase.ts` の port 化) と Stage 3 (`src/session/sweeper.ts` の TTL 対応) が、この設計書の実装タスクにも受け入れ基準にも含まれておらず、対象外であるという明示もないことを報告している。

Stage 2 と Stage 3 の両方に触れている必要がある。片方だけなら fail。
「対象外と明示すべき」「別 Phase とする宣言が必要」といった上流への修正要求の形でも、レビュー中に非目標として設計書へ追記した形でも pass。
ADR の内容を転記しているだけで、受け入れ基準側との対応の欠落を指摘していない場合は fail。
