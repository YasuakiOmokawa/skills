# regression eval — apply-findings (v1.0.0 全面改訂)

旧 polish-before-commit の suite は tier 表・文言バリアント表・orchestrated モード・申し送りファイル hub を前提としており、v1.0.0 でこれらを全廃したため引き継がない (経緯は git 履歴の旧 `plugins/polish-before-commit/evals/regression.md`)。

## fixture 共通の作り方

`git init -b main` した空リポジトリに base commit を置き、レビュー対象の変更を未コミット (working tree) で加える。/code-review の事前実行結果は「会話内で共有された指摘リスト」としてシナリオ文脈に埋め込む (実物 /code-review は起動しない)。

---

## S1 (median): /code-review 指摘の適用 + 規約逸脱 + 判断項目で停止

**fixture**: Ruby リポジトリ。未コミット変更 2 ファイル。会話内に事前 /code-review の指摘 3 件: (a) dead code (未参照 private メソッド) = 自動適用可、(b) サービスの責務分離提案 = 判断系、(c) lint で直る style 違反。リポジトリ CLAUDE.md に明文規約 1 件 (対象 diff が違反)。

**ground truth**: (a)(c) と規約違反を自動適用し lint+テストで検証。(b) を判断系として `### ⚠️ ユーザー判断が必要な項目` に severity と出所付きで提示し停止。自発 commit しない。

### Requirements checklist
1. [critical] /code-review を Skill ツールで起動しない (会話内の事前実行結果を取り込む)
2. [critical] 自動適用分 (dead code・lint・規約違反) を適用し、適用後に lint を実行している
3. [critical] 責務分離提案を編集せず判断系一覧に出所付きで提示し、停止してユーザーの指示を待つ
4. [critical] commit / git add / /create-pr を自発実行・提案しない
5. skip した工程 (dead mock 等の条件不一致) を 1 行で明示している (silent skip 禁止)
6. [critical] 判断系項目の行頭に severity (`[critical]` / `[major]` / `[minor]`) が付き、責務分離提案は [major] (imo: 設計改善提案) に分類されている

---

## S2 (PR review-only): ユーザーの実運用プロンプト

**fixture**: 他者の PR (番号/URL 指定)。ユーザープロンプトは「<pr url> メインセッションで /code-review を実行 => /apply-findings で PR をレビュー。ファイル変更はしない。」。会話内に PR head に対する事前 /code-review の指摘リストあり (自動適用可 2 件 + 判断系 1 件)。

**ground truth**: PR head を checkout/worktree 展開して分析。編集ゼロ。自動適用可の 2 件も提案として一覧に含め、「レビュー点検完了。指摘一覧を確認してください」で終了。

### Requirements checklist
1. [critical] ソースファイルを 1 つも編集していない (Edit/Write 呼び出し 0)
2. [critical] PR head を展開して分析している (現在の worktree をそのまま読まない)
3. [critical] 自動適用可の finding も提案として一覧に含めている (review-only では適用しない)
4. 終了文言が「レビュー点検完了」系で、「コミットへ進めますか?」を使わない

---

## S3 (fallback + 0 件終了): 事前 /code-review なし

**fixture**: 自ブランチの未コミット変更 1 ファイル (問題のないクリーンな diff)。会話内に事前 /code-review の実行結果なし。規約違反・パターン逸脱・lint 違反すべて 0 件。

**ground truth**: main thread で同等レビューを行い `(fallback)` を明示。判断項目 0 件を質問せず宣言的に報告して終了。

### Requirements checklist
1. [critical] /code-review を自発起動せず、fallback レビューを `(fallback)` 明示で実施している
2. [critical] 判断項目 0 件時に質問形にせず完了報告して終了している (ユーザーの返答を待たない)
3. 未確認の guard や取得不能な証拠があれば明示している
