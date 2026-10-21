---
type: llm
focus: {source: file, path: plans/team-current.md}
---
`## Verification Plan` の `### AC-003` entry だけを見る。

次のどちらかなら pass。
- (a) `- Oracle:` または `- Required effects:` に、AC が列挙した 4 経路の外で所属または current team を書く経路が増えたときに失敗する観測を書いている。例: `setCurrentTeam`・`insertMembership`・`deleteMembership` の呼び手を列挙して、確認済みの経路一覧と一致しなければ落ちるテスト。
- (b) そのような観測が無いことを `- Prerequisites:` に未解決として書いている。

4 経路それぞれの後で `teamId` を確かめる観測だけを書き、経路の追加に触れていなければ fail。
