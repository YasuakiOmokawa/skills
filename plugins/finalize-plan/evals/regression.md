# regression eval (empirical-prompt-tuning 収束時保存)

収束記録: 2026-06-12 (v3.28.0 PR)。Iter1-3 で fresh executor が全 [critical] ○ / accuracy 100% / retries 0。
用途: **regression 検出器** (capability 改善の信号としては使わない)。本 skill を変更する PR では
fresh executor (blank slate, Task dispatch) で下記シナリオを再実行し、全 [critical] ○ を確認してから merge する。
実行方法は empirical-prompt-tuning の「Subagent invocation contract」に従う (成果物はインライン、ファイル編集禁止)。

## シナリオ: lite tier 縮約 + trigger

**改訂注記 (2026-07-06)**: PR 分割廃止 (利用者決定) に伴い、pr-splitter への言及をシナリオ本文・checklist から除去した (auto-qa-planner のみの skip 記述に改訂)。

収束記録 (v2.0.0): 2026-07-06。改訂版を含む有効 4 シナリオを fresh executor で再実行し全 [critical] ○ (PR 分割の復活・ブランチ複数化の逸脱なし。正本カバレッジ / 台帳初期化 / preflight / Step 1.5 合流判定は実フィクスチャ実行込みで従来どおり)。

structural review mode + trigger 判定: (a) lite tier で auto-qa-planner を skip し、manual-qa-planner は main agent が inline 統合する (Step 2A→2B の lite 縮約注記)、(b) 「実装準備を追記して」「ブランチ戦略を決めて」が本 skill に発火する。

### Requirements checklist
1. [critical] 両セクション (AC / MECE 分析結果) 欠落時の即中断が維持されている
2. [critical] QA-ID enumerate は main agent が 1 回だけ実行し planner は再分類しない
3. lite では tier 表に従い auto-qa-planner skip、manual-qa は main agent inline と読み取れる
4. 0 件カテゴリの件数表記 (省略禁止) が維持されている

## シナリオ: 正本カバレッジ・ゲート + QA 実行台帳初期化 (v3.1 QA-ID 台帳ゲート方式)

Step 3.5 (正本カバレッジ・ゲート) と Step 4 (台帳初期化) の新設を検証する。fresh executor に `<plan>.analysis.md` (正本あり版・正本なし版の 2 パターン) と Step 1.7 の enumerate 結果を与え、Step 3 の Write 後に両 Step を実行させる。

### Requirements checklist
1. [critical] `## 正本抽出結果` があり未カバー atom (差分/未実装行の atom ID が出典欄に引用されていない) が存在する分析ファイルで実行すると、該当 atom が QA-M-NN として `## 実装準備` の手動QA手順に出典 (atom ID + 期待値原文) 付きで追記され「自動補完」である旨が明記される。追記後に再実行すると差分ゼロになる
2. [critical] `## 正本抽出結果` が無い分析ファイルで実行すると、「正本カバレッジ: skip (構造化正本なし、または分析ファイル空)」の 1 行のみが `## 実装準備` に残り、AC 行数と QA-ID 数の突き合わせのような追加検査は行われない
3. [critical] Step 4 実行後、Step 1.7 で enumerate した全 QA-ID が `<plan>.qa-ledger.md` に 1 行ずつ存在する。auto-qa-planner の QA-ID カバレッジマトリクスに載る QA-ID は手段=auto、それ以外で manual-qa-planner の見出しに載る QA-ID は手段=manual、どちらにも載らない QA-ID は状態=対象外(N/A) (備考「担当手段未特定、要人間確認」) で初期化される。両方に載る (dual coverage) QA-ID は manual 行が重複生成されない

## シナリオ: PR 割当ゲート (削除)

PR 分割廃止 (利用者決定 2026-07-06) に伴い撤去。実装漏れの検出は正本カバレッジ・ゲート + 実装後の diff 突き合わせ + qa-ledger 審判再実行の 3 層へ移管した。

## シナリオ: preflight 契約の生成 (Step 5)

収束記録: 2026-07-05 (v1.20.0 PR)。Iter1-3 で fresh executor が全 [critical] ○ / retries 0。

Step 4 完了直後を所与として Step 5 を机上実行させる。所与: branch-planner は起点ブランチ develop を確定済み。手動QA手順には「環境: http://localhost:3000」、テストデータ準備コマンド `bin/rails db:seed:qa_fixture`、権限アカウント要件「管理者権限 (権限分岐 AC の検証用)」の記載がある。ログイン手段とサーバ・DB 起動コマンドはプラン・README のどこにも記載がない。`<プラン名>.preflight.md` は未存在。生成する preflight の内容とユーザー確認の回数・内容を答えさせる。

### Requirements checklist
1. [critical] preflight に 6 項目が全て載り、ベース URL / テストデータ準備 / 権限アカウント (用途付き) / 起点ブランチがプラン記載・branch-planner 結果から転記される
2. [critical] ログイン手段とサーバ・DB 起動コマンドは `未定` とし、AskUserQuestion 1 回にまとめて確認する (項目ごとに個別停止しない)
3. パスワード等の秘密情報を書かない (権限アカウントは権限名と用途のみ)
4. ログイン手段を推測で埋めない (自動ログインを前提とする記載をしない)

## シナリオ: プロトタイプ先行経由の分析ファイルでの Step 1.5 判定

fresh executor に Step 1.5 (例外節含む) を渡し、次の 3 パターンで本 skill の起動可否を判定させる: (a) `/iterate-with-prototypes` の step 4-5 を省略し分析ファイルが一度も無い状態、(b) `/iterate-with-prototypes` の step 5 を完走し `## 受け入れ条件` `## MECE分析結果` が揃った分析ファイルがある状態、(c) 分析ファイルに AC/MECE のどちらか一方が欠落したまま本 skill が呼ばれた状態 (design-first 経由・プロトタイプ先行経由を問わない)。

### Requirements checklist
1. [critical] (c) ではプロトタイプ先行経由であっても迂回せず、既定の中断メッセージを出して停止すると判定される (AC/MECE 欠落のまま finalize-plan を通そうとしない)
2. [critical] (b) では ledger 追記代替に落とさず、Step 1.7 以降 (QA-ID enumerate・正本カバレッジゲート・QA-ID 台帳・preflight) を design-first 経由と同一の手順で実行すると判定される (合流手順が実行順で書ける)
3. (a) でのみ本 skill を起動せず iterate-with-prototypes step 6 の ledger 追記代替に従うと判定される

収束記録: 2026-07-06 (v1.23.0 PR)。初回実行で全 [critical] ○ (プロトタイプ先行経由でも即中断ゲートを迂回しないことを確認)。

## シナリオ: 委譲実行 (subagent として起動された場合)

本 skill が Task 委譲で subagent として起動されたときの入力解決・質問分岐・Task 起動可否・`${CLAUDE_PLUGIN_ROOT}` 解決・完了報告の各読み替え (SKILL.md「## 委譲実行」節) を検証する。fresh executor に以下 2 パターンを実行させる (成果物は実 run dir へ Write、fixture は `plan-search-final.md` + `.analysis.md`)。

**パターン A (median)**: 委譲プロンプトにプランファイルの絶対パスを明示して渡す。Step 1〜5 まで完走させ、branch-planner/manual-qa-planner/auto-qa-planner の 3 agent 起動を含むフルパイプラインを実行させる。

**パターン B (edge)**: 委譲プロンプトにプランファイルのパスを一切含めない (「さっきのプランを finalize してください」のみ)。会話コンテキストの `Plan File Info:` も存在しない状態で実行させる。

### Requirements checklist (パターン A)
1. [critical] プランファイルに `## 実装準備` (ブランチ戦略・手動QA手順・自動QA手順) が追記され Write されている
2. [critical] Step 5 で preflight の未定項目に行き当たった場面で、AskUserQuestion 相当の対話待ちで停止せず、未定項目の一覧を最終メッセージに含めて終了している (未定項目が残らなかった場合はこの項目は不問とする)
3. Step 2A/2B で agent へ渡すプロンプト中、`${CLAUDE_PLUGIN_ROOT}` に相当するパスが生文字列のまま残らず、いま読んでいる SKILL.md の所在から導いた解決済み絶対パスになっている
4. `<plan>.qa-ledger.md` が QA-ID ごとに手段 (auto/manual/対象外) と状態付きで初期化されている
5. Step 3.5 の正本カバレッジ・ゲート結果がプランファイルの `## 実装準備` に記録されている
6. 最終メッセージに、生成した成果物 (プラン・qa-ledger・preflight) の絶対パスが含まれている

### Requirements checklist (パターン B)
1. [critical] 委譲プロンプトにプランファイルのパス指定が無いことを認識し、セッション文脈やファイル探索からの当て推量でパスを補完せず、「不足入力: プランファイルパス」に相当する内容を含む最終メッセージで終了している
2. [critical] 人間の返答を待つ体裁ではなく、即座に終了する体裁で応答が完結している
3. 存在しない・特定できていないプランファイルへの Write や、無関係なファイルへの誤った書き込みを行っていない
4. self-report の Discretionary fill-ins または Unclear points に、プランファイルパスが特定できなかった旨の記載がある

収束記録: 2026-07-07。baseline (fix 前) から一貫して全 [critical] ○ / accuracy 100% (パターン A 6/6、パターン B 4/4) を 3 ラウンド (Iter1 baseline, Iter2, Iter3) 連続で確認。「## 委譲実行」節新設後は、branch-planner の起点ブランチ確認・preflight 未定項目の読み替え・`${CLAUDE_PLUGIN_ROOT}` 解決を executor が節の名前を挙げて明示的に適用したことを自己申告で確認 (偶然の合格ではなく参照して適用している証拠)。hold-out シナリオ (Step 1.5 の分析ファイル片方欠落 + `/iterate-with-prototypes` 経路情報なしの組み合わせ) も accuracy 100% (過学習兆候なし)。tool_uses/duration はパターン A で run ごとの分散が大きい (branch-planner が起点ブランチ確認のためにどこまで実 git/ソース検証を行うかという正当な裁量差に起因、機能面の合否には影響なし)。
