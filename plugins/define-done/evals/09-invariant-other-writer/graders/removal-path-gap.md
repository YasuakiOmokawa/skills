---
type: llm
focus: {source: file, path: plans/invite-accept.md}
---
この設計書に書き込まれた MECE レビューについて、次を満たすなら pass。

- メンバーを除名する既存経路 (`src/membership/remove.ts` の `removeMember`) が所属だけを削除して `currentTeamId` を更新しないため、除名された user の `verifySession` が所属していないチームの ID を返しうる、と報告している。

判定の要点。
- `remove.ts`、`removeMember`、`deleteMembership`、除名のいずれかで経路を特定できていればよい。
- 「他の経路も確認すべき」「不変条件の維持を検討する」のように経路を特定しない一般論だけなら fail。
- 今回の範囲外として扱っていても、経路を名指しし、計画にも受け入れ基準にも無いことを示していれば pass。
