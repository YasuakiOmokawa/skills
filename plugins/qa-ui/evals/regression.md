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

---

以下は v3.1 (QA-ID 台帳ゲート方式) 追加分。収束記録: 2026-07-05。fresh executor (Task dispatch) で 4 シナリオ × Iter1-3 の 12 実行が全 [critical] ○ / accuracy 100% / retries 0。

## シナリオ: 検証不能(真の制約) がループを止めない (Step 5 判定)

親エージェントとして Step 5。台帳は初期化済みで QA-H-01〜QA-H-03・QA-E-01・QA-D-01 の 5 QA-ID が pending。ラウンド 1 の ui-evaluator 結果: 5 件中 3 PASS / 1 Major FAIL (ボタン文言不一致、QA-H-02) / 1 検証不能 (QA-D-01、multipart アップロード。ui-evaluator の Gotchas テーブル分類は「真の制約」、代替検証として curl で API を直叩きし 200 を確認済みと報告)。このラウンドで台帳に記帳する内容と、次に取るアクションを答える。

### Requirements checklist
1. [critical] QA-D-01 を「エスカレートして停止」しない。台帳に `検証不能(真の制約)` として記帳し、非ブロッキング終端として扱う
2. [critical] 残る QA-H-02 (Major FAIL) は通常どおり最小修正 → ラウンド 2 として Step 4 を再起動する (QA-D-01 のせいでループ全体を止めない)
3. ラウンド 2 の Step 4 プロンプトで QA-D-01 を `手動確認済み:` 欄に含め、再検証対象から除外する
4. 代替検証 (curl 200) の結果を記帳内容またはユーザー向け報告に含める

## シナリオ: 計画外差異が全件 QA-G 追記される (Step 5 判定)

親エージェントとして Step 5。台帳は QA-H-01〜QA-H-03 の 3 QA-ID が pending。ラウンド 1 の ui-evaluator 結果: 指定 QA-ID 3 件は全て PASS。加えて「計画外差異の詳細」節に 2 件 (正本と乖離するボタン色の相違 = Minor、正本にあるアイコンの欠落 = Major) が報告された。台帳・プランファイルへの記帳内容と、次のアクションを答える。

### Requirements checklist
1. [critical] 発見された計画外差異 2 件を両方とも QA-G-NN (例: QA-G-01, QA-G-02) として台帳とプランファイルの手動QA手順に追記する (1 件で打ち切らない)
2. [critical] 各 QA-G を報告どおりの重大度で `FAIL(Minor)` / `FAIL(Major)` として記帳する
3. Major 側 (QA-G-02) は次ラウンドの通常修正ループへ自動編入し、既存のラウンド上限 (3 + root cause 例外 1) をそのまま適用する (QA-G 専用の別上限を新設しない)

## シナリオ: 再実行ゲートが 0 examples を PASS にしない (Step 5.5)

審判 (qa-ui 本体) として Step 5.5。台帳の auto 行 QA-E-01 (手段=auto、実装者による自己申告 `PASS (実装者の自己申告、審判未検証)`) に対し、プランファイルの QA-ID カバレッジマトリクスから実行コマンド `bundle exec rspec spec/x_spec.rb -e "QA-E-01"` を取得し実行したところ、exit code は 0 だが標準出力に `0 examples, 0 failures` が含まれていた。台帳への記帳内容を答える。

### Requirements checklist
1. [critical] exit code 0 であっても `PASS` として記帳しない
2. [critical] `要人間確認` として記帳し、備考にテスト0件の兆候を検出したことを残す
3. 実装者の自己申告 PASS 行は書き換えず、新しい行として追記する (完了判定は「最新行が勝つ」規則により審判の再実行結果を優先する)

## シナリオ: 完了判定が pending 残存で完了を宣言しない (Step 6)

審判 (qa-ui 本体) として Step 6。台帳の最新行集計結果: QA-H-01 = PASS、QA-H-02 = pending (台帳生成後、一度も記帳されていない)、QA-E-01 = PASS。完了判定の結果を答える。

### Requirements checklist
1. [critical] 「## UI QA 完了」を宣言しない
2. [critical] QA-H-02 の pending 行を未完了行として明示し、「## UI QA 部分完了 (人間確認事項あり) または未完了」として応答する
3. QA-H-02 が解消 (Step 5 の判定ループまたは人間への確認) されるまで完了扱いにしない旨を示す

---

以下は v1.11.0 (preflight 契約参照) 追加分。収束記録: 2026-07-05。fresh executor で Iter1-3 全 [critical] ○ / retries 0 (Iter1 で判定順・パス結合の曖昧さを検出し SKILL.md 修正後に再収束)。

## シナリオ: preflight 参照で URL・テストデータ・権限アカウントを解決する (Step 2 / Phase A・B)

$ARGUMENTS はパスのみ `/teams/42/settings`。プランファイル特定済み、同ディレクトリの `<プラン名>.preflight.md` に ベース URL = http://localhost:3000 / ログイン手段 = 未定 / 権限アカウント一覧 = 管理者権限 (権限分岐 AC の検証用) / テストデータ準備手順 = `bin/rails db:seed:qa_fixture` / 起点ブランチ = develop / サーバ・DB 起動コマンド = `docker compose up -d` が記載されている。権限分岐 AC が 1 件ある。(1) Step 2 の URL 決定、(2) ログイン画面表示時の挙動、(3) Phase A の実行内容、(4) Phase B で尋ねる内容を答えさせる。

### Requirements checklist
1. [critical] 検証 URL は preflight のベース URL と結合して http://localhost:3000/teams/42/settings に決定し、ベース URL をユーザーに尋ねない
2. [critical] ログイン画面検出時は従来どおり停止してユーザーにログイン操作を依頼する (preflight があってもエージェントは自動ログインしない)
3. Phase A: preflight のテストデータ準備手順をドキュメント化済みコマンドと同列に扱い実行する
4. Phase B: 権限アカウントは preflight 記載を採用し、権限分岐アカウントの確認を省略する

---

以下は v1.12.0 (Orchestrated モード / escalation ledger) 追加分。**未収束 (親が収束実行予定)**。

## シナリオ: Orchestrated モードで Critical 1件が他 QA-ID の完了を止めない (Step 5 / Step 6)

Task 起動プロンプトに「orchestrated モードで実行。escalation は `plan.escalation-ledger.md` に記帳して続行せよ」の明示指示あり。台帳は QA-H-01〜QA-H-03 の 3 QA-ID が pending。ラウンド 1 の ui-evaluator 結果: QA-H-01 = Critical FAIL (決済二重送信)、QA-H-02・QA-H-03 = PASS。このラウンドで取るアクション、escalation ledger への記帳内容、Step 6 の完了判定表示を答えさせる。

### Requirements checklist
1. [critical] QA-H-01 のために停止しない。escalation ledger に Critical として記帳し、QA-H-01 を `要人間確認` のまま保留する
2. [critical] QA-H-02・QA-H-03 は台帳上 PASS 済みのため、Step 5.5・Step 6 まで通常どおり進める (QA-H-01 のせいで他 QA-ID の完了処理を止めない)
3. [critical] Step 6 の完了判定表示に「escalated 1件（うち Critical 1件）」を明示し、判定は「完了」ではなく「部分完了」を上限とする
4. escalation ledger の記帳行が `| 番号 | 出所 | 深刻度 | 内容 | 根拠 | 推奨アクション |` の列構成に従う
