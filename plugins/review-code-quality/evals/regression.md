# regression eval (empirical-prompt-tuning 収束時保存)

収束記録: 2026-06-12 (v3.28.0 PR)。Iter1-3 で fresh executor が全 [critical] ○ / accuracy 100% / retries 0。
用途: **regression 検出器** (capability 改善の信号としては使わない)。本 skill を変更する PR では
fresh executor (blank slate, Task dispatch) で下記シナリオを再実行し、全 [critical] ○ を確認してから merge する。
実行方法は empirical-prompt-tuning の「Subagent invocation contract」に従う (成果物はインライン、ファイル編集禁止)。

## シナリオ: deep tier / billing リスク領域 / 注入エラー fallback

冒頭の自動取得節に `unknown revision 'origin/develop...HEAD'` エラーが見えている。$ARGUMENTS なし。変更 4 ファイル (plan.rb の plan_code 値追加 + billing_service.rb + spec 2 本)。手順を列挙させ、(a) diff リカバリ (b) tier と実行モード (c) business-impact-analyzer 起動 (d) auto-apply 判定軸を明答させる。

### Requirements checklist
1. [critical] フォールバック (b): default branch を特定して origin/<base>...HEAD に読み替えて再実行 (origin/develop のまま再実行しない)
2. [critical] billing リスク領域のため tier = deep (4 agent 並列) + business-impact-analyzer 必須
3. plan_code (domain model attribute) 更新のため business-impact の skip 条件に非該当
4. auto-apply は readability 軸のみ。リスク領域のため needs-judgment 側に倒す
5. 申し送り先 `$(git rev-parse --git-dir)/quality-review-handoff.md` → /polish-before-commit が受け取る contract を認識
