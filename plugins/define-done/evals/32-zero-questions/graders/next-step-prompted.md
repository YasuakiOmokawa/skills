---
type: llm
focus: last_message
---
最終回答を見る。次の 2 つを両方満たせば pass。
1. 利用者に返す問いが 0 件である (曖昧な要求が無い) ことをはっきり書いている。
2. 次の一歩として、問い返しをせずに `plans/slug.md` を define-done に渡して受け入れ基準と受け入れテストを作るよう促している。`/define-done` と計画のパス (`plans/slug.md`) の両方が出ていること。
