# regression eval (empirical-prompt-tuning 収束時保存)

収束記録 1: 2026-06-12 (v3.28.0 PR)。Iter1-3 で fresh executor が全 [critical] ○ / accuracy 100% / retries 0。
収束記録 2: 2026-07-02 (v0.21.0 PR、「1 行サマリー既定 / 詳細展開はユーザー指示時のみ」改訂)。Iter1-7 の 22 executor 実行で全 [critical] ○ / accuracy 100% を維持、hold-out (trivial docs PR) pass、Iter7 で retries 全員 0。
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
