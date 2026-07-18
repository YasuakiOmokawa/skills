# regression eval (empirical-prompt-tuning 収束時保存)

収束記録 1: 2026-06-12 (v3.28.0 PR)。Iter1-3 で fresh executor が全 [critical] ○ / accuracy 100% / retries 0。
収束記録 2: 2026-07-02 (v0.21.0 PR、「1 行サマリー既定 / 詳細展開はユーザー指示時のみ」改訂)。Iter1-7 の 22 executor 実行で全 [critical] ○ / accuracy 100% を維持、hold-out (trivial docs PR) pass、Iter7 で retries 全員 0。
収束記録 3: 2026-07-07 (`Task` 委譲実行摩擦の解消。「## 委譲実行」節を新設し branch-validation.md / labels-and-milestones.md / Step 6 を委譲実行に読み替え)。Iter1(baseline)〜Iter4 + hold-out シナリオ C で収束、既存シナリオ 1-4 は fresh executor で全 [critical] ○ を再確認 (回帰なし)。詳細はシナリオ 5-6。
収束記録 4: 2026-07-07 (既定 draft / 明示指定時のみ ready・既存 open PR 検出時の更新経路・タイトル prefix と本文冒頭注記の受け方を追加)。fresh executor 7 本 (baseline 3 シナリオ×2 ラウンド + hold-out 1 本) で全 [critical] ○ / accuracy 100%、修正なしで収束 (2 ラウンド連続で新規不明点 0)。回帰ゲートはシナリオ 1・5 を再実行し全 [critical] ○ を再確認。詳細はシナリオ 7。
用途: **regression 検出器** (capability 改善の信号としては使わない)。本 skill を変更する PR では
fresh executor (blank slate, Task dispatch) で下記シナリオを再実行し、全 [critical] ○ を確認してから merge する。
実行方法は empirical-prompt-tuning の「Subagent invocation contract」に従う (成果物はインライン、ファイル編集禁止)。

## シナリオ 1: lite tier + 注入非対応

$ARGUMENTS なし (default base = develop)。1 commit 済み + 未コミット 1 ファイル、single domain、<50 LoC、既存 pattern 踏襲。自動取得節は生コマンド文字列のまま。コマンド列と判断を列挙させ、(a) ユーザー確認の有無 (b) tier と評価時点 (c) Step 9 観点 (d) Pre-work 点数を明答させる。

### Requirements checklist
1. [critical] ユーザーへの確認・質問を一切行わず draft PR 作成まで進む (disallowed-tools: AskUserQuestion)
2. [critical] tier = lite、評価時点は Step 1 の git log [base]..HEAD 時点 (Step 2 の commit は数えない)
3. Step 9 は [A]+[D] の 2 観点のみ、Pre-work 本質リストは 1-2 点
4. fallback で git status -sb / git log --oneline -15 を Bash 実行
5. PR body は mktemp、milestone 確認は --paginate

## シナリオ 2: 展開指示なし (1 行サマリー既定)

$ARGUMENTS なし。feature ブランチ 3 commits + migration 1 本 (→ deep tier)、テンプレは「設計判断」「やらなかったこと」「レビューしてほしい観点」見出しを含むが本質列挙系セクション (「このPRでやること」) は無し。セッション文脈に設計判断議論 (採用 1 + 棄却案 2 件・却下理由付き)、明示スコープ外 (後続チケット番号付き)、動作確認 (spec 結果 + 手動確認) を与える。

### Requirements checklist
1. [critical] 定型 (Revert 手順 / チェックリスト) 以外の各セクションが 1 行サマリーのみ (複数文段落・bullet・表・コードブロック無し。「やらなかったこと」1 項目 1 行は可)
2. [critical] 詳細展開指示が無いため「設計判断」に棄却案の散文展開を書かない (棄却案は完了報告の「展開可能」列挙へ)
3. [critical] ユーザー確認なしで draft PR 作成まで進む
4. 完了報告に展開可能素材の列挙がある
5. deep の本質リスト 5+ 点は「やったこと」1 文畳み込み + 残点分配 (番号リスト格上げしない)
6. 「やらなかったこと」1 行に「何を + なぜ + 次にどこで」を含む

## シナリオ 3: 「設計判断は詳しく」展開指示あり

$ARGUMENTS = `develop 設計判断は詳しく` でシナリオ 2 と同一文脈。

### Requirements checklist
1. [critical] 「設計判断」がサマリー行 + 直下散文展開の構成で棄却案 2 件と却下理由を含む
2. [critical] 指示のない他セクションは 1 行サマリーのまま
3. [critical] ユーザー確認なしで draft PR 作成まで進む
4. 先頭トークンをベースブランチ (`git ls-remote --heads origin` で確認)、残りを詳細展開指示として解釈
5. 展開部は散文中心 (bullet 3+ の羅列でない)、1 段落目 = 選択結果

## シナリオ 4: perf PR + 実測表素材 (baseline 失敗 = C-FO/ninja-sign#39914 の再現)

$ARGUMENTS なし。perf ブランチ 2 commits (standard tier)、テンプレに「設計判断」系見出し無し。セッション素材に EXPLAIN ANALYZE 実測 4 条件・spec parity 結果・設計判断議論 (既存パターン踏襲・旧経路温存) を与える。

### Requirements checklist
1. [critical] 「動作確認結果」が 1 行サマリー (実測表・spec 出力のコードブロックを本文に入れない)。キー数値 (改善前後ペア + 前提条件の括弧注記) を含む
2. [critical] 「やったこと」「なぜやるのか」が各 1 文
3. [critical] テンプレに無い「設計判断」見出しを追加しない (反映先候補も無ければ本文非反映、完了報告で「展開可能」通知)
4. 関連セクションが説明段落にならない (1 行リンク + 関係ラベル 1 句まで)
5. 完了報告に展開可能素材の列挙がある

## シナリオ 5: 委譲実行 (base 明示指定、gh pr create 失敗時の縮退)

`Task` ツールで委譲され、起動プロンプトの `$ARGUMENTS` 相当に base branch `main` を明示指定。対象リポジトリの `origin` はローカル bare repo に付け替え済みで、push は成功するが `gh pr create` は GitHub ホスト未解決で失敗する (実 GitHub への push・PR 作成は発生しない)。委譲実行では会話履歴が渡らないため、Step 4c/6 の情報源は起動プロンプトへの明示転記かファイルベース (diff・commit メッセージ) に限られる。

### Requirements checklist
1. [critical] push が実行され成功している
2. [critical] `gh pr create` 失敗時、組み立て済みコマンド全文と生成済みタイトル・本文を最終メッセージに含めて終了している (存在しない PR URL を捏造しない)
3. タイトルが `<type>(<scope>): <説明>` 形式かつ 72 文字以内
4. 明示指定した base branch が実際に使用され、デフォルトブランチへの誤ったフォールバックが起きていない
5. PR 本文がテンプレに無い見出しを追加していない、またはテンプレ未検出の旨が明示されている
6. push 失敗など別要因で中断せず、`gh pr create` (Step 10) まで到達している

## シナリオ 6: 委譲実行 (詳細展開指示を委譲プロンプトで受信、base 未指定)

`Task` ツールで委譲され、詳細展開指示 (「設計判断は詳しく」) を起動プロンプトの `$ARGUMENTS` 相当で受信。base branch 指定なしのためデフォルトブランチ解決に進む。対象リポジトリにテンプレートが無い場合、フォールバック構成に「設計判断」相当の見出しが無いため、新規見出しを追加せず完了報告での提示に回すのが正しい (テンプレ実在時は該当セクションを散文展開する)。

### Requirements checklist
1. [critical] テンプレに「設計判断」相当セクションがあれば散文展開されている。無ければ新規見出しを追加せず完了報告で展開可能素材として提示している (どちらも許容。テンプレ非実在を理由に×とはしない)
2. [critical] 詳細展開の材料を、存在しないセッション発話から捏造せず diff・commit メッセージ等ファイルベースの根拠から構成している
3. base branch 未指定のため、リポジトリのデフォルトブランチが正しく解決されている
4. 詳細展開の対象が「設計判断」相当セクションに限定され、他セクションは 1 行サマリーのまま
5. `gh pr create` 失敗時、組み立て済みコマンドと本文が最終メッセージに含まれている (実 PR URL を捏造しない)

## シナリオ 7: 既存 open PR がある対象ブランチへの再呼び出し

$ARGUMENTS なし (「PR を作って」のみ)。対象ブランチに未 push のコミットが 1 本あり、`gh pr list --head <branch> --state open` は既存 open PR (#42) を返す (事前確認済みの前提として与える)。

### Requirements checklist
1. [critical] `gh pr create` を実行しようとせず、既存 PR (#42) を検出して push + `gh pr edit --body-file` の更新経路を選ぶ
2. [critical] 未 push コミットを反映する `git push` が実行され成功している
3. `gh pr edit <対象PR番号>` の PR 番号が事前確認結果の番号と一致する (捏造しない)
4. `gh pr edit` は実行せず、組み立てた完全なコマンド文字列を最終メッセージで報告して終了している
5. 完了報告に既存 PR の番号または URL を含めている

収束記録: 2026-07-17 (v0.26.0 progressive disclosure 分割)。委譲実行節を references/delegated-execution.md、積み PR gotcha を references/stacked-pr-base.md へ verbatim 退避し、Quick start の三重記述を短縮 (挙動変更なし)。全 7 シナリオを fresh executor で再実行し全 [critical] ○ (17/17)。委譲実行シナリオ 5/6 で delegated-execution.md への 1 hop 到達を確認。
収束記録: 2026-07-18 (empirical-prompt-tuning 再検証、skill 本文・references 変更なし)。全 7 シナリオを fresh executor (blank slate, Task dispatch、ローカル git fixture + bare origin、`gh` は実行禁止で実行予定コマンド文字列を成果物化) で再実行し全 [critical] ○ (17/17)、非 critical 項目含め accuracy 100% (retries は fixture 起因の裁量再判断のみ)。委譲シナリオ 5/6 で delegated-execution.md 到達・base 明示 (main) の使用・base 未指定時の symbolic-ref フォールバック解決 (→main) を確認。シナリオ 4 で session 素材 (旧経路を Flipper で温存する設計判断) が最終 diff (straight NOT IN→NOT EXISTS 置換) とドリフトしたケースを executor が検知し、description-style.md 113 行の空欄優先に従い「レビューしてほしい観点」を空欄 + 完了報告退避、「動作確認結果」は 12,400ms→640ms の代表値 1 行に圧縮。シナリオ 5 で commit メッセージの過剰主張 (「指数バックオフ」「恒久エラー即時 raise」) が diff に不在なのを検知し diff を真実として title/body を再構成。executor が挙げた不明点は全て scaffolding 起因 (gh 実行禁止・sandbox で spec 実行不可・fixture の事前生成コミットゆえ AI provenance 観測不能) かラベル値の裁量で、checklist を崩す新規 skill 欠陥なし。回帰なし・修正なしで収束 (2026-07-17 記録を直前クリアとして本日 1 ラウンドで確定)。
