# regression eval (empirical-prompt-tuning 収束時保存)

収束記録: 2026-07-07（「## 委譲実行」節新設 PR）。fresh executor（Task dispatch）で median 2 回・edge 2 回・hold-out 1 回の計 5 実行が全 [critical] ○ / accuracy 100%。baseline（Iter1）の時点で両シナリオとも critical 項目は全 ○ だった。理由: 「委譲実行」節が入力解決の優先順位と、対話確認手段（AskUserQuestion）が無い実行文脈での Step 5 / Step 7 の既定動作を明文化済みだったため。hold-out シナリオ（起動プロンプト本文に入力ソースが一切含まれない委譲実行）でも accuracy 低下なし（過学習兆候なし）。
用途: **regression 検出器**（capability 改善の信号としては使わない）。本 skill を変更する PR では
fresh executor（blank slate, Task dispatch）で下記シナリオを再実行し、全 [critical] ○ を確認してから merge する。
実行方法は empirical-prompt-tuning の「Subagent invocation contract」に従う（成果物はインライン、ファイル編集禁止）。

## シナリオ: 委譲実行（対話確認手段なし）で Step 5 / Step 7 の確認待ちに陥らず完了報告まで到達する

あなたは map-user-stories の実行を Task で委譲された subagent である（対話確認手段は無く、応答を待てない）。起動プロンプトに設計書（DD）の絶対パスが明示されており、DD には機能が 2-3 個含まれる。チーム人数・スプリント長・開発期間の追加情報はこれ以上得られない。

### Requirements checklist
1. [critical] 最終メッセージまで完了しており、Step 5（スプリント計画）または Step 7（レビュー）で確認・承認待ちのまま停止していない
2. [critical] Step 5 で採用した既定値（スプリント長の既定値、またはチーム人数/開発期間が未確定な場合に取った依存位相順バックログ方針）が完了報告または「## 未解決事項」に明記されている
3. Step 6 の 7 セクション（Context / Phase N / スプリントマッピング / Jira↔US マッピング / タスクリスト / US TSV / 未解決事項）が全て出力されている
4. タスクリストが TSV コードフェンスで 9 列（US_ID/Task_ID/タスク名/やること/やらないこと/完了条件/依存タスク/Jira/備考）揃って出力されている
5. Step 7 のレビューについて、4 観点（粒度/依存関係/統合分割/Phase分類）の self-check を行ったことが報告に明記されている
6. 「やらないこと」列が全 US/タスクで空欄になっていない
7. Jira への実書き込みが行われていない（Jira 列は空欄またはプレースホルダのみ）

収束記録: 2026-07-11 (タスク TSV 契約同期・粒度 tie-break 追加)。create-jira-issues とのタスク TSV 契約 (専用 3 列: やること/やらないこと/完了条件) の同期を完了し、output-templates.md の追従待ち注記を解消した。タスク粒度基準に「5 ファイル上限と vertical slice が衝突する場合の tie-break (backend→frontend の 2 タスク連鎖 + 後続タスクにユーザー可視の検証を課す)」を追加した。委譲実行シナリオを fresh executor で 2 回実行し全 [critical] ○、2 回目 (8 ファイル規模 US を含む DD) で tie-break 規定の引用・適用を確認し、新規不明点 0 で収束。
