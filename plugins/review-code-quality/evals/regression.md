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

---

以下は v1.19.0 (Orchestrated モード / quality ledger) 追加分。収束記録: 2026-07-05。fresh executor で Iter1-3 全 [critical] ○ / retries 0 (Iter1 で採番規則・語彙揺れ等の仕様ギャップを検出し修正後に再収束)。

## シナリオ: Orchestrated モードで quality ledger に記帳し収束判定する (Step 4)

Task 起動プロンプトに「orchestrated モードで実行。escalation は `plan.escalation-ledger.md` に記帳して続行せよ」の明示指示あり。Step 4 の振り分け結果: (1) readability の関数50行超過 1 件 → auto-apply-safe で適用・検証 pass、(2) coupling の内容結合 (`instance_variable_set`) 1 件 → needs-judgment、(3) business-impact の認可 chain 該当 1 件 → needs-judgment。quality ledger への記帳内容と、収束判定を答えさせる。

### Requirements checklist
1. [critical] 3 件全てを quality ledger に記帳する (申し送りファイルのみで終わらせない)
2. [critical] (1) は深刻度 Major (readability 構造的問題閾値超過) / 状態 `適用済み`、(2)(3) は深刻度 Critical (内容結合 / 認可 chain は Critical 条件に該当) / 状態 `escalated` として記帳する
3. quality ledger の記帳行が `| 番号 | 出所 | 深刻度 | 状態 | 内容 |` の列構成に従う
4. 3 件とも Critical/Major が `適用済み` または `escalated` のため、収束判定は「収束」と答える
