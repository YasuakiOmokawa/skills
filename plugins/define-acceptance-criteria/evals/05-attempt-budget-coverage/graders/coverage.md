---
type: llm
focus: {source: file, path: plans/attempt-budget.md}
---
plans/attempt-budget.md の Acceptance Criteria 節を評価する。仕様の各条件に対応する criterion があるかを数える。
(a) 四回目失敗直後はログイン可
(b) 五回目失敗直後はロック + メッセージ表示
(c) 十四分五十九秒後はロック中
(d) 十五分一秒後はログイン可
(e) ロック前にログイン成功すると失敗回数が零に戻る
(f) ロック発生時に audit_log へ account_locked が 1 行記録される
(g) audit_log への記録が失敗してもロックは成立し、ログイン応答が記録成功時と同じ
(h) ロック解除は audit_log に記録されない
(i) Ground Review R1: src/auth/ 配下に redis への参照が増えていない
(j) Ground Review R2: ユーザー A のロック中にユーザー B が正しいパスワードでログインできる (独立した criterion)
各条件を満たす criterion が 1 つ以上あれば 1 点。10 点満点で score = 点数 / 10。
仕様に無い製品要件 (例: 管理者による手動解除、通知メール) を criterion として追加していたら 1 点減点。
