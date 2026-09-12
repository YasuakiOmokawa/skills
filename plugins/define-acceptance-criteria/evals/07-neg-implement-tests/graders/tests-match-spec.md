---
type: llm
focus: trace
---
trace 中で作成されたテストファイルの内容を評価する。次がすべて成り立てば pass。
1. 30 分未満の時点でリンクが利用できる (view が reset-form) ことを検証するテストがある。
2. 30 分超の時点で期限切れ (view が expired、changed が false) を検証するテストがある。
3. 同じトークンの 2 回目の consume が used を返すことを検証するテストがある。
4. plans/reset.md に受け入れ基準 (AC-NNN) を書き込んでいない。
1 つでも欠ければ fail。
