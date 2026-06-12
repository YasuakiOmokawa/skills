# regression eval (empirical-prompt-tuning 収束時保存)

収束記録: 2026-06-12 (v3.28.0 PR)。Iter1-3 で fresh executor が全 [critical] ○ / accuracy 100% / retries 0。
用途: **regression 検出器** (capability 改善の信号としては使わない)。本 skill を変更する PR では
fresh executor (blank slate, Task dispatch) で下記シナリオを再実行し、全 [critical] ○ を確認してから merge する。
実行方法は empirical-prompt-tuning の「Subagent invocation contract」に従う (成果物はインライン、ファイル編集禁止)。

## シナリオ: 検証不能 + Major FAIL 混在 (Step 5 判定)

親エージェントとして Step 5。ラウンド 1 の ui-evaluator 結果: AC 5 件中 3 PASS / 1 Major FAIL (ボタン文言不一致) / 1 検証不能 (ファイルアップロード AC、automation 制約)。表示メッセージを作成し、ユーザーが「手動で確認した、OK だった」と返答した後のアクションも答える。

### Requirements checklist
1. [critical] 修正ループに入らず停止し、メッセージに検証不能と FAIL の両方 + 返答案内文を含む
2. [critical] 返答後: 該当項目を除外して残 FAIL (Major) を最小修正し、ラウンド 2 として Step 4 を再起動する
3. 再起動時の Step 4 プロンプトで除外項目を検証対象から除き `手動確認済み:` 欄に 1 行注記する
4. 検証不能の理由 (automation 制約) を表示に含める
