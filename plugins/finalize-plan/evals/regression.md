# regression eval (empirical-prompt-tuning 収束時保存)

収束記録: 2026-06-12 (v3.28.0 PR)。Iter1-3 で fresh executor が全 [critical] ○ / accuracy 100% / retries 0。
用途: **regression 検出器** (capability 改善の信号としては使わない)。本 skill を変更する PR では
fresh executor (blank slate, Task dispatch) で下記シナリオを再実行し、全 [critical] ○ を確認してから merge する。
実行方法は empirical-prompt-tuning の「Subagent invocation contract」に従う (成果物はインライン、ファイル編集禁止)。

## シナリオ: lite tier 縮約 + trigger

structural review mode + trigger 判定: (a) lite tier で pr-splitter / auto-qa-planner を skip し、manual-qa-planner は main agent が inline 統合する (Step 2A→2B の lite 縮約注記)、(b) 「実装準備を追記して」「ブランチ戦略と PR 分割を決めて」が本 skill に発火する。

### Requirements checklist
1. [critical] 両セクション (AC / MECE 分析結果) 欠落時の即中断が維持されている
2. [critical] QA-ID enumerate は main agent が 1 回だけ実行し planner は再分類しない
3. lite では tier 表に従い pr-splitter / auto-qa-planner skip、manual-qa は main agent inline と読み取れる
4. 0 件カテゴリの件数表記 (省略禁止) が維持されている

## シナリオ: 正本カバレッジ・ゲート + QA 実行台帳初期化 (v3.1 QA-ID 台帳ゲート方式)

Step 3.5 (正本カバレッジ・ゲート) と Step 4 (台帳初期化) の新設を検証する。fresh executor に `<plan>.analysis.md` (正本あり版・正本なし版の 2 パターン) と Step 1.7 の enumerate 結果を与え、Step 3 の Write 後に両 Step を実行させる。

### Requirements checklist
1. [critical] `## 正本抽出結果` があり未カバー atom (差分/未実装行の atom ID が出典欄に引用されていない) が存在する分析ファイルで実行すると、該当 atom が QA-M-NN として `## 実装準備` の手動QA手順に出典 (atom ID + 期待値原文) 付きで追記され「自動補完」である旨が明記される。追記後に再実行すると差分ゼロになる
2. [critical] `## 正本抽出結果` が無い分析ファイルで実行すると、「正本カバレッジ: skip (構造化正本なし、または分析ファイル空)」の 1 行のみが `## 実装準備` に残り、AC 行数と QA-ID 数の突き合わせのような追加検査は行われない
3. [critical] Step 4 実行後、Step 1.7 で enumerate した全 QA-ID が `<plan>.qa-ledger.md` に 1 行ずつ存在する。auto-qa-planner の QA-ID カバレッジマトリクスに載る QA-ID は手段=auto、それ以外で manual-qa-planner の見出しに載る QA-ID は手段=manual、どちらにも載らない QA-ID は状態=対象外(N/A) (備考「担当手段未特定、要人間確認」) で初期化される。両方に載る (dual coverage) QA-ID は manual 行が重複生成されない

## シナリオ: PR 割当ゲート (実装QA-ID 列の完全性、v1.22.0 で追加)

Step 3.5 の PR 割当ゲートを検証する。所与: QA-ID カバレッジマトリクスに auto QA-ID 6 件 (QA-H-01 / QA-E-01 / QA-E-02 / QA-D-02 / QA-M-01 / QA-M-02)、PR 分割計画は 3 PR で「実装QA-ID」列を持つが QA-M-02 だけどの PR の実装QA-ID 列にも載っていないプランファイルをフィクスチャとして与え、Step 3.5 の PR 割当ゲートを実行させる (実行は scratchpad フィクスチャで可)。checklist 3 の検証には single-branch 縮約 (「現ブランチ 1 コミット」表記) のフィクスチャも別途構築させ、fail 系 / pass 系 / skip 系の 3 系を実行させる。根拠: 実案件で auto 23 件中 6 件が無割当のまま実装漏れし、qa-ui の再実行ゲートで初めて検出された。

収束記録: 2026-07-06 (v1.22.0 PR)。初回実行で [critical] 2/2 ○ (executor が実フィクスチャで Bash を実行し fail→Edit 補完→pass を実機確認)。skip 系は実装エージェントのフィクスチャ 3 系検証で確認済み。

### Requirements checklist
1. [critical] ゲート Bash が未割当 1 件 (QA-M-02) を検出して fail し、未割当 QA-ID を列挙する。全件割当済みに直したフィクスチャでは pass する
2. [critical] fail 時、未割当 QA-ID をいずれかの PR の実装QA-ID 列へ Edit で補完し、ゲートを再実行して未割当 0 件を確認してから先へ進む (未割当を残したまま Step 4 に進まない)
3. single-branch / no-PR モード (PR 分割なし) では skip 1 行で通過する

## シナリオ: preflight 契約の生成 (Step 5)

収束記録: 2026-07-05 (v1.20.0 PR)。Iter1-3 で fresh executor が全 [critical] ○ / retries 0。

Step 4 完了直後を所与として Step 5 を机上実行させる。所与: branch-planner は起点ブランチ develop を確定済み。手動QA手順には「環境: http://localhost:3000」、テストデータ準備コマンド `bin/rails db:seed:qa_fixture`、権限アカウント要件「管理者権限 (権限分岐 AC の検証用)」の記載がある。ログイン手段とサーバ・DB 起動コマンドはプラン・README のどこにも記載がない。`<プラン名>.preflight.md` は未存在。生成する preflight の内容とユーザー確認の回数・内容を答えさせる。

### Requirements checklist
1. [critical] preflight に 6 項目が全て載り、ベース URL / テストデータ準備 / 権限アカウント (用途付き) / 起点ブランチがプラン記載・branch-planner 結果から転記される
2. [critical] ログイン手段とサーバ・DB 起動コマンドは `未定` とし、AskUserQuestion 1 回にまとめて確認する (項目ごとに個別停止しない)
3. パスワード等の秘密情報を書かない (権限アカウントは権限名と用途のみ)
4. ログイン手段を推測で埋めない (自動ログインを前提とする記載をしない)
