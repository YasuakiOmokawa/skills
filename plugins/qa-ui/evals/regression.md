# regression eval (empirical-prompt-tuning 収束時保存)

収束記録: 2026-06-12 (v3.28.0 PR)。Iter1-3 で fresh executor が全 [critical] ○ / accuracy 100% / retries 0。
用途: **regression 検出器** (capability 改善の信号としては使わない)。本 skill を変更する PR では
fresh executor (blank slate, Task dispatch) で下記シナリオを再実行し、全 [critical] ○ を確認してから merge する。
実行方法は empirical-prompt-tuning の「Subagent invocation contract」に従う (成果物はインライン、ファイル編集禁止)。

**注記 (人間委譲既定化 PR)**: 本 PR で manual 割当の QA-ID の既定実行手段を人間委譲に変更した (ブラウザ automation は明示指示時のみのオプションへ降格)。下記シナリオのうち ui-evaluator の結果を前提とするもの（「検証不能 + Major FAIL 混在」「検証不能(真の制約)がループを止めない」「計画外差異が全件QA-G追記される」「preflight参照でURL・テストデータ・権限アカウントを解決する」「OrchestratedモードでCritical 1件が他QA-IDの完了を止めない」の 5 件）は、いずれも「automation モード明示指定時」のシナリオとして読み替える（既定の人間委譲モードでは Step 4 で人間に実行手順書を提示し、その回答を判定入力とする）。再実行済み (2026-07-06、v1.14.0 PR): automation 指定へ読み替えた 5 本すべて全 [critical] ○ (後方互換を確認)。先頭シナリオは検証不能項目が Gotchas カタログ済みの真の制約のままで停止経路の検証意図とずれていたため初見の項目へ差し替え、改訂版の再実行で全 [critical] ○。人間委譲モードの新シナリオを本ファイル末尾に追加した。

## シナリオ: 初見の検証不能 + Major FAIL 混在 (Step 5 判定、automation モード明示指定時)

親エージェントとして Step 5。automation モードが明示指定されておりラウンド 1 の ui-evaluator 結果: AC 5 件中 3 PASS / 1 Major FAIL (ボタン文言不一致) / 1 検証不能 (外部 IdP リダイレクトが automation 環境から到達できず対象画面に到達不能 — ui-evaluator は分類「初見」と報告、Gotchas テーブルに該当エントリなし)。表示メッセージを作成し、ユーザーが「手動で確認した、OK だった」と返答した後のアクションも答える。

(改訂注記 v1.14.0: 検証不能項目を「ファイルアップロード」から初見の項目へ差し替えた。旧フィクスチャは Gotchas カタログ済みの `真の制約` に該当し、現行 Step 5 では非ブロッキング継続が正しい挙動になってシナリオの意図 — 未カタログ検証不能の停止経路の検証 — とずれていたため。真の制約の非ブロッキング側は次シナリオが担う)

### Requirements checklist
1. [critical] 修正ループに入らず停止し、初見の検証不能を `要人間確認` として記帳したうえで、メッセージに検証不能と FAIL の両方 + 返答案内文を含む
2. [critical] 返答後: 該当項目を除外して残 FAIL (Major) を最小修正し、ラウンド 2 として Step 4 を再起動する
3. 再起動時の Step 4 プロンプトで除外項目を検証対象から除き `手動確認済み:` 欄に 1 行注記する
4. 検証不能の理由 (automation 環境から到達不能) を表示に含める

---

以下は v3.1 (QA-ID 台帳ゲート方式) 追加分。収束記録: 2026-07-05。fresh executor (Task dispatch) で 4 シナリオ × Iter1-3 の 12 実行が全 [critical] ○ / accuracy 100% / retries 0。

## シナリオ: 検証不能(真の制約) がループを止めない (Step 5 判定、automation モード明示指定時)

親エージェントとして Step 5。automation モードが明示指定されており、台帳は初期化済みで QA-H-01〜QA-H-03・QA-E-01・QA-D-01 の 5 QA-ID が pending。ラウンド 1 の ui-evaluator 結果: 5 件中 3 PASS / 1 Major FAIL (ボタン文言不一致、QA-H-02) / 1 検証不能 (QA-D-01、multipart アップロード。ui-evaluator の Gotchas テーブル分類は「真の制約」、代替検証として curl で API を直叩きし 200 を確認済みと報告)。このラウンドで台帳に記帳する内容と、次に取るアクションを答える。

### Requirements checklist
1. [critical] QA-D-01 を「エスカレートして停止」しない。台帳に `検証不能(真の制約)` として記帳し、非ブロッキング終端として扱う
2. [critical] 残る QA-H-02 (Major FAIL) は通常どおり最小修正 → ラウンド 2 として Step 4 を再起動する (QA-D-01 のせいでループ全体を止めない)
3. ラウンド 2 の Step 4 プロンプトで QA-D-01 を `手動確認済み:` 欄に含め、再検証対象から除外する
4. 代替検証 (curl 200) の結果を記帳内容またはユーザー向け報告に含める

## シナリオ: 計画外差異が全件 QA-G 追記される (Step 5 判定、automation モード明示指定時)

親エージェントとして Step 5。automation モードが明示指定されており、台帳は QA-H-01〜QA-H-03 の 3 QA-ID が pending。ラウンド 1 の ui-evaluator 結果: 指定 QA-ID 3 件は全て PASS。加えて「計画外差異の詳細」節に 2 件 (正本と乖離するボタン色の相違 = Minor、正本にあるアイコンの欠落 = Major) が報告された。台帳・プランファイルへの記帳内容と、次のアクションを答える。

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

## シナリオ: preflight 参照で URL・テストデータ・権限アカウントを解決する (Step 2 / Phase A・B、automation モード明示指定時)

automation モードが明示指定されている。$ARGUMENTS はパスのみ `/teams/42/settings`。プランファイル特定済み、同ディレクトリの `<プラン名>.preflight.md` に ベース URL = http://localhost:3000 / ログイン手段 = 未定 / 権限アカウント一覧 = 管理者権限 (権限分岐 AC の検証用) / テストデータ準備手順 = `bin/rails db:seed:qa_fixture` / 起点ブランチ = develop / サーバ・DB 起動コマンド = `docker compose up -d` が記載されている。権限分岐 AC が 1 件ある。(1) Step 2 の URL 決定、(2) ログイン画面表示時の挙動、(3) Phase A の実行内容、(4) Phase B で尋ねる内容を答えさせる。

### Requirements checklist
1. [critical] 検証 URL は preflight のベース URL と結合して http://localhost:3000/teams/42/settings に決定し、ベース URL をユーザーに尋ねない
2. [critical] ログイン画面検出時は従来どおり停止してユーザーにログイン操作を依頼する (preflight があってもエージェントは自動ログインしない)
3. Phase A: preflight のテストデータ準備手順をドキュメント化済みコマンドと同列に扱い実行する
4. Phase B: 権限アカウントは preflight 記載を採用し、権限分岐アカウントの確認を省略する

---

以下は v1.12.0 (Orchestrated モード / escalation ledger) 追加分。収束記録: 2026-07-05。fresh executor で Iter1-3 全 [critical] ○ / retries 0 (Iter1 で採番規則・語彙揺れ等の仕様ギャップを検出し修正後に再収束)。

## シナリオ: Orchestrated モードで Critical 1件が他 QA-ID の完了を止めない (Step 5 / Step 6、automation モード明示指定時)

Task 起動プロンプトに「orchestrated モードで実行。escalation は `plan.escalation-ledger.md` に記帳して続行せよ」および automation モードの明示指示あり。台帳は QA-H-01〜QA-H-03 の 3 QA-ID が pending。ラウンド 1 の ui-evaluator 結果: QA-H-01 = Critical FAIL (決済二重送信)、QA-H-02・QA-H-03 = PASS。このラウンドで取るアクション、escalation ledger への記帳内容、Step 6 の完了判定表示を答えさせる。

### Requirements checklist
1. [critical] QA-H-01 のために停止しない。escalation ledger に Critical として記帳し、QA-H-01 を `要人間確認` のまま保留する
2. [critical] QA-H-02・QA-H-03 は台帳上 PASS 済みのため、Step 5.5・Step 6 まで通常どおり進める (QA-H-01 のせいで他 QA-ID の完了処理を止めない)
3. [critical] Step 6 の完了判定表示に「escalated 1件（うち Critical 1件）」を明示し、判定は「完了」ではなく「部分完了」を上限とする
4. escalation ledger の記帳行が `| 番号 | 出所 | 深刻度 | 内容 | 根拠 | 推奨アクション |` の列構成に従う

---

以下は v1.14.0 (人間委譲既定化) 追加分。収束記録: 2026-07-06。fresh executor で Iter1-3 の 3 実行が全 [critical] ○ / retries 0。

## シナリオ: 人間委譲（既定）で実行手順書を提示する (Step 1 / Step 4)

台帳は QA-H-01〜QA-H-03 の 3 QA-ID（手段 = manual）が pending。同ディレクトリの `<プラン名>.preflight.md` にベース URL = `http://localhost:3000` / ログイン手段 = 「テストユーザー test@example.com でログイン」/ テストデータ準備手順 = `bin/rails db:seed:qa_fixture`（Phase A で実行済み）が記載されている。ユーザーからの起動指示は「UI を確認して」のみで、automation・ui-evaluator・ブラウザ等の語は含まれない。エージェントが Step 1〜Step 4 で取るアクションを答えさせる。

### Requirements checklist
1. [critical] 実行モードを人間委譲（既定）と判定し、`mcp__chrome-devtools-direct__list_pages` を含む ChromeDevTools MCP のツールを一切呼び出さない
2. [critical] QA-H-01〜03 それぞれについて、前提（URL・ログイン手段・テストデータ準備状況）・操作手順・確認点（チェックボックス）を含む実行手順書を QA-ID ごとに 1 ブロックで提示する
3. [critical] 手順書提示後は ui-evaluator を Task 起動せず、人間の返答（PASS / FAIL+内容 / 検証不能+理由）を待って停止する。返答を台帳へ記帳してから Step 5.5（auto 判定の再実行ゲート）へ進む
4. 提示前に automation オプションを使わない（ユーザーが「automation で」等と明示していないため）

---

以下は v1.18.0 (委譲実行 / 分割実行契約) 追加分。収束記録: 2026-07-07。fresh executor (Task dispatch) で Iter1-2 + hold-out 1本の計 5 実行が全 [critical] ○ / accuracy 100% / retries 0。Iter1 の時点で既に baseline が全項目 ○ だった (subagent は単一ターン内で文字どおり「待つ」ことが構造的にできず、既定動作でも「手順書を返して終了」に自然収束するため)。ただし挙動が仕様として明文化されていなかったため `## 委譲実行` 節を新設し、分割実行契約・入力解決の優先順位を明記した。hold-out シナリオ (ベース URL 未解決) で accuracy 低下なし (過学習兆候なし)。

## シナリオ: 委譲実行 (Task dispatch) で Step 4 人間委譲の分割実行契約に従う (人間委譲既定モード)

あなたは qa-ui の実行を Task で委譲された subagent である（AskUserQuestion が利用可能ツールに無い）。プランファイル・台帳（QA-H-01〜03 manual pending, QA-E-01〜02 auto pending）・preflight（ベース URL・ログイン手段・テストデータ準備手順いずれも記載済み）が揃っている。起動プロンプトに automation・ブラウザ等の語は含まれない。QA を実行し、完了したら結果を報告するよう指示されている。

### Requirements checklist
1. [critical] 「automation で」等の明示指示が無いため Step 1 で人間委譲モード（既定）と判定し、ChromeDevTools MCP を一切使用していない
2. [critical] Step 4 で手段=manual の QA-ID ごとの実行手順書を組み立て、「人間の返答を待って停止する」を、`## 委譲実行` 節の分割実行契約に従って「手順書を最終メッセージとして返し、返答を待たずに終了する」に読み替えている
3. 最終メッセージに、手順書全文に加えて「人間の回答を得たうえで台帳から再開する」旨、または台帳が状態正本であるため再起動時に安全に再開できる旨の言及がある
4. `<プラン名>.qa-ledger.md` の既存記帳を破棄せず追記のみで扱っている（Step 3.5「最新行が勝つ」規則の維持）

## シナリオ: 委譲実行 + orchestrated 宣言時も Step 4 の分割実行契約は変わらない

あなたは qa-ui の実行を Task で委譲された subagent である。起動プロンプトに「orchestrated モードで実行。escalation は `<path>` に記帳して続行せよ」の明示指示があり、シナリオ・入力は前シナリオと同一（人間委譲モード、QA-H-01〜03 manual pending）。

### Requirements checklist
1. [critical] orchestrated 宣言があっても Step 4 の人間委譲初回手順書提示には「escalation ledger に記帳して続行」を適用せず、実回答が無い状態で判定を進めず、通常どおり手順書を最終メッセージとして返して終了している（orchestrated の読み替えは Step 5 以降の判定分岐が対象であり Step 4 の初回提示には及ばない）
2. [critical] 手順書自体が orchestrated 宣言の有無に関わらず通常モードと同等の完全な形式で提示されている
3. `escalation-ledger.md` への記帳が Step 4 の初回提示時点では発生していない

## シナリオ: 委譲実行で入力解決の優先順位に従いベース URL 不足を即時返却する

あなたは qa-ui の実行を Task で委譲された subagent である（AskUserQuestion が利用可能ツールに無い）。プランファイルは存在するが `<プラン名>.preflight.md` が存在せず、プラン本文にもベース URL の具体的記載が無く、起動プロンプトにも URL 相当の入力が無い。

### Requirements checklist
1. [critical] ベース URL 解決の候補（起動プロンプト明示指定・preflight・プラン本文記載）がすべて不成立と判定し、`## 委譲実行 > 入力解決の優先順位` に従って「不足入力: ベース URL」等、不足入力を名指しした文言を最終メッセージとして返し、返答を待たずに終了している
2. [critical] URL 未確定のまま Step 4 の実行手順書を組み立てていない
3. Step 3 のプランファイル読み込み・QA-ID 抽出や Step 3.5 の台帳初期化など、URL 決定より後続の処理へ進んでいない

---

以下は v1.19.0 (正本抽出結果直接読込みフォールバック) 追加分。収束記録: 2026-07-07。fresh executor (Task dispatch) で median/edge Iter1-2 + hold-out 1本の計 5 実行が全 [critical] ○ / accuracy 100% / retries 0。Iter1 時点で既に全項目 ○ だったため Iter2 は再現性確認のみ。

## シナリオ: 正本抽出結果直接読込みフォールバックで検証項目を FIG 行から列挙する (Step 3、automation モード明示指定時)

automation モードが明示指定されている。対象は PoC プランファイルで、`## 実装準備 > 手動QA手順` の QA-ID 台帳・`<plan>.analysis.md` はいずれも存在せず、プランファイル自体の末尾に `## 正本抽出結果`（`| atom ID | 期待値 | 状態 |` 形式、FIG-01〜05。うち FIG-02・FIG-04 が「差分」、残り3件は「一致」）がある。ChromeDevTools MCP が利用不可の環境という前提で、Step 3 がどの経路を発火させ検証項目を何件・どの内容で列挙するかを答えさせる。

### Requirements checklist
1. [critical] 検証項目を FIG-02・FIG-04（「差分」の2件）から列挙し、「一致」の3件は対象外とする
2. [critical] 発火する分岐が「正本抽出結果直接読込みフォールバック」であり、AC無しモード（汎用 git diff ベースの推論）に縮退していないと明言する
3. 出力冒頭に警告文言「⚠️ QA プラン/台帳なし: 正本抽出結果直接読込み (台帳・ゲート無効)」を含める
4. この分岐が QA-ID 台帳前提の Step 1 人間委譲/automation 判定の対象外であり、現行どおり automation（ui-evaluator）で検証する旨に言及する

収束記録: 2026-07-11 (description/keywords の人間委譲既定への同期)。plugin.json の description/keywords を SKILL.md の人間委譲既定に同期した (SKILL.md 本文は無変更)。人間委譲既定の代表シナリオ (Step 1-4 机上) を fresh executor で再実行し全 [critical] ○ / 新規不明点 0 で後方互換を確認した。

収束記録: 2026-07-17 (v1.23.0 progressive disclosure 分割)。SKILL.md 483 行を 311 行へ再配置し、委譲実行 / automation モード / 台帳・ゲート Bash を references 3 ファイル (delegated-execution.md / automation-mode.md / ledger-gates.md) へ分離した (挙動変更なし)。本ファイルの全 12 シナリオを fresh executor (Task dispatch, blank slate) で再実行し全 [critical] ○ / retries 0。分割後の reference 到達 (automation の Gotchas 判定・ledger-gates の 0 examples 判定・delegated-execution の分割実行契約) も各シナリオ内で確認した。executor 1 体が orchestrated 時の Critical の台帳記帳トークン (`要人間確認` — orchestrated-mode.md L20 — と SKILL.md Step 6 の manual 由来 `FAIL(Critical)` 残存分岐) の揺れを指摘した — 旧版から存在する記述で外形挙動 (保留・継続・部分完了上限) は一致するため本 PR では未修正、一本化は別 PR で検討。

収束記録: 2026-07-18 (SKILL.md/agents/references の regression 再検証、no-fix)。SKILL.md・agents/ui-evaluator.md・references 4 ファイル (automation-mode / delegated-execution / ledger-gates / orchestrated-mode) に対し、本ファイルの全 12 シナリオを fresh executor (Task dispatch, blank slate) で 1 ラウンド再実行し全 [critical] ○ / accuracy 100% / retries 0。Iter-0 静的チェックで frontmatter description の謳うトリガー・範囲 (人間委譲既定 / automation オプション / 3 フォールバック / 台帳ゲートと機械集計完了判定) と本文 Step 1-6 の実カバーに乖離なしを確認し、executor 実行前の修正は不要だった。ChromeDevTools MCP が無い環境のため automation 系シナリオは inline 供給の ui-evaluator 結果を判定入力とする机上再現で実行し (S12 は MCP 非依存の Step 3 分岐判定に限定)、実ブラウザ必須で blocked としたシナリオは無し。SKILL.md/agents/references への修正は入れていない (converged, no-fix)。executor が挙げた新規指摘は (a) fixture/環境由来の scaffolding (S1 被験ソース欠如で最小修正が記述止まり・S6 preflight が権限片側のみ記載・S9 read-only sandbox で seed 実行不可・S12 MCP 不可) と (b) 挙動を歪めない軽微な記述明確化余地 (S2 automation で 手段=manual の台帳ラウンド列番号・S3 混在ラウンドで PASS 側 QA-ID の記帳) のみで、いずれも全 executor が正しい挙動に到達しており修正対象外と判断した (regression=劣化検出器の用途に照らし過学習を避ける。S2/S3 の一本化は 2026-07-17 記録が先送りした記述揺れと同系で別 PR 検討)。
