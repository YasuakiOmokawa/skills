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

収束記録: 2026-07-17 (v0.8.0 / empirical スリム化)。SKILL.md を 222 行 → 193 行にスリム化。低頻度・任意の 2 文脈 (INVEST 原則チェック表・大規模PJ の 3 ターン出力分割手順) を新設 `references/advanced-cases.md` へ verbatim 退避し、本文にはトリガー条件と 1 hop ポインタを残した。Step 4 の粒度過剰/粒度不足の例示は output-templates.md「タスク粒度の判断」節と重複していたためポインタへ集約 (ルール文言は本文に明示保持)。fresh executor 6 実行 (median 3・大規模 edge 2・text ソース hold-out 1) を 3 ラウンドで回し、Round 1 の median で「Step 5 縮退時に必須の `## スプリントマッピング` をどう描画するか橋渡し規則が無い」新規不明点 1 件を検出 → Step 5 縮退規則に「Sprint 列 `未割当・依存波N` / 期間 `未確定` で位相順に描画する」1 文を追記。Round 2・Round 3 とも新規不明点 0・全 [critical] ○ で 2 連続クリア収束。hold-out (別ドメイン・text ソース) も accuracy 100% で過学習兆候なし。大規模 edge 実行で両 references への 1 hop ポインタが「いつ開くか」明確と executor が確認 (退避の妥当性を実証)。挙動変更・ルール希釈なし (git show HEAD 突き合わせで消失ルール 0)。

収束記録: 2026-07-18 (regression 再検証 / 変更なし収束)。skill 本文・references を無変更のまま、保存済み「委譲実行 (対話確認手段なし)」シナリオを fresh executor (Task dispatch, blank slate) 2 実行で再検証。median (文書一括ダウンロード DD・3 機能) と edge (承認ワークフロー刷新 DD・機能1 が 8 ファイル規模の単一 US) の 2 インスタンスとも全 [critical] ○ / accuracy 100% (tool_uses 各 4、duration 238s / 294s)。median は Step 5 縮退 (スプリント長既定 1週間 + チーム人数/開発期間未確定 → 依存波順バックログ、`## スプリントマッピング` を Sprint 列 `未割当・依存波N` / 期間 `未確定` で描画) と Step 7 self-check を正しく適用し、権限チェック US をセキュリティ観点で Phase 1 へ再配置する self-correction まで到達。edge は 8 ファイル規模 US に tie-break 規定 (backend→frontend の 2 タスク連鎖 + 後続タスクにユーザー可視の完了条件) を引用・適用し、US-001 が後続タスク完了で demoable になる形に落とした。両実行の unclear points はいずれも DD 側スペックの穴 (ダウンロード成功/失敗の確定ロジック未定義・承認フロー開始起点の欠落・差し戻し戻り先未定義等) を「## 未解決事項」へ正しく退避したもので、skill 指示の曖昧さ起因の新規不明点は 0 (skill が想定どおりギャップを surfacing した挙動)。2026-07-17 収束を直前ラウンドのクリアとして 1 ラウンドで確定。修正なし収束。
