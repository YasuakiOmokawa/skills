# regression eval (empirical-prompt-tuning 収束時保存)

収束記録: 2026-06-12 (v3.28.0 PR)。Iter1-3 で fresh executor が全 [critical] ○ / accuracy 100% / retries 0。
用途: **regression 検出器** (capability 改善の信号としては使わない)。本 skill を変更する PR では
fresh executor (blank slate, Task dispatch) で下記シナリオを再実行し、全 [critical] ○ を確認してから merge する。
実行方法は empirical-prompt-tuning の「Subagent invocation contract」に従う (成果物はインライン、ファイル編集禁止)。

## シナリオ: Fresh Red Team / Unknown 棄権 (agents/fresh-red-team.md + references/red-team-checklist.md)

BB/WB findings JSONL (auth で両者言及 = 補強し合う合意 / 弱い evidence「推測」の WB finding / observability は両者言及ゼロ + リポジトリ読取不能) を与え、統合評価レポートを出させる。プラン本文・AC 本文は渡さない。

### Requirements checklist
1. [critical] フォーマット通りの JSONL 4 ブロック + Markdown を出力 (0 件ブロックは根拠 1 文)
2. [critical] 裏取り材料ゼロの領域を「判定不能 (Unknown)」に理由付きで計上し、漏れ件数行に `(+ Unknown K 件は未確定)` を併記。M 行 (お見合い JSONL) に severity を捏造しない
3. 弱い evidence (推測) は原則 4 で問題側に倒す (Unknown にしない)
4. 補強し合う合意のマージ (根拠の層が仕様/コードで異なる) + Critical 閾値 (単独で害成立) で severity 決定
5. AC 判定の片側欠落時は「AC マージ検証」で subagent 不全シグナルとして再取得を指示 (両側そろえば省略)

再検証記録: 2026-07-07。M ブロックの perspective 値から「純技術リスク補完」を除外し T ブロックへ排他的に振り分ける旨、および漏れ件数を M+T 合算とする旨を明文化する改修後、fresh executor で本シナリオを 2 ラウンド再実行し該当 2 項目 (M/T 振り分け・漏れ件数式) は全 ○。ただし「証拠ゼロの領域で T ブロックへ能動的に起票してよい範囲と Unknown 棄権原則の優先順位」「AC マージ検証が件数比較のみで ID 集合比較でない」の 2 点が新たな不明点として残った (規定打ち切り、詳細は本 skill 外の運用記録を参照)。

---

以下は v1.24.0 (Orchestrated モード / escalation ledger) 追加分。収束記録: 2026-07-05。fresh executor で Iter1-3 全 [critical] ○ / retries 0 (Iter1 で採番規則・語彙揺れ等の仕様ギャップを検出し修正後に再収束)。

## シナリオ: Orchestrated モードで BB/WB 3 連続不一致が安全側に倒れて続行する (Step 1-2) — ⚠️ v1.35.0 で失効 (Orchestrated モード自体を廃止。呼び出し元オーケストレータ不在の dead code を撤去したため。委譲実行時の安全側挙動は references/delegated-execution.md の「最終メッセージに含めて終了」が正)

Task 起動プロンプトに「orchestrated モードで実行。escalation は `plan.escalation-ledger.md` に記帳して続行せよ」の明示指示あり。Step 1-2: BB/WB の AC 判定行数が `${ENUMERATED_AC}` (12 件) と 3 回連続で不一致 (AC-9 の判定行が毎回欠落、補完自体が成立しない出力破損が続く)。この状況で取るアクションを答えさせる。

### Requirements checklist
1. [critical] AskUserQuestion で停止しない。AC-9 を `judgment:"言及なし"` で補完したうえで、AC-9 を Critical 扱いとして escalation ledger に記帳する
2. [critical] 記帳後、Step 2 (Fresh Red Team) 以降の処理を続行する (レビュー全体を中断しない)
3. escalation ledger の記帳行が `| 番号 | 出所 | 深刻度 | 内容 | 根拠 | 推奨アクション |` の列構成に従う
4. Step 3-4 の 1 行サマリーで escalation ledger 記帳分を Critical 件数に算入する (安全側に倒した分を「MECE OK」に混入させない)

再検証記録: 2026-07-07。「Step 0 の即中断ゲートは Orchestrated モードの対象外」を本文に明記する改修後、fresh executor で本シナリオを再実行し全 [critical] ○ (Step 0 ゲートとの混同なく続行判定)。ただし `references/dispatch-prompts.md` のリカバリ点 2/3 (欠落 AC 数基準 vs 再現回数基準の優先順位が未規定)・BB/WB 補完の書き込み先未規定の 2 点が新たな不明点として残った (本シナリオの合否には影響せず、担当外の別ファイルのため今回は未修正)。

---

以下は「## 委譲実行 (subagent として起動された場合)」セクション追加分。収束記録: 2026-07-07。fresh executor で baseline から 2 ラウンド (Iter2/Iter3) 連続で全 [critical] ○ / accuracy 100% / retries 0。baseline 時点で既に高精度だった (executor の裁量で偶然クリアしていた) ため、入力解決優先順位・AskUserQuestion 分岐の読み替え・`${CLAUDE_PLUGIN_ROOT}` 解決・完了報告契約を明文化する改修を実施し、決定論的な挙動へ固定した。hold-out シナリオで Fresh Red Team 経由の `${CLAUDE_PLUGIN_ROOT}` 自己参照解決 (agents/fresh-red-team.md 内 2 箇所) も初めて実地検証し、正常動作を確認済み。

## シナリオ: 委譲実行 (median) — orchestrated 宣言なし、入力一式あり

Task で委譲起動。プランファイル・分析ファイル (AC 定義済み) の両方を渡し、MECE 検証の実行を指示する。

### Requirements checklist (2026-08-02 v1.34.0 改訂: standard は inline 実行になったため item 2 を読み替え)
1. [critical] 分析ファイル末尾に MECE 分析結果セクション (Critical/Important/Nice-to-have 分類を含む) が追記されている
2. [critical] Step 1 は standard inline で実行し nested Task を dispatch していない。Fresh Red Team を起動した場合のみ、その nested Task で `${CLAUDE_PLUGIN_ROOT}` が生文字列のまま埋め込まれて Read 失敗が起きた形跡がないこと
3. プランファイルの `## 品質検証` に規定フォーマットの1行が追記されている
4. プラン本文が書き換えられておらず、finding ID がプラン本文に持ち込まれていない
5. 最終メッセージに分析ファイルの絶対パスと MECE判定 (OK/要修正) および Critical 件数が含まれている

## シナリオ: 委譲実行 (edge) — orchestrated 宣言あり、分析ファイルパスを渡さない

Task で委譲起動。orchestrated モード宣言 + escalation ledger パスを明示し、プランファイルパスのみ渡す (分析ファイルは意図的に用意しない)。

### Requirements checklist
1. [critical] 起動プロンプト本文で明示されたプランファイルパスを入力として採用しており、`$ARGUMENTS` や `Plan File Info:` の不在を理由に「不足入力」と誤判定していない
2. [critical] 分析ファイルの不在 (`## 受け入れ条件` 未定義) を検知し、SKILL.md 0-2 で規定された中断を実行して Step 1 以降を開始せずに終了している
3. AC を自前で捏造したり、分析ファイルを新規作成して埋めたりしていない
4. 最終メッセージに、分析ファイルが見つからないため検証を中断した旨とプランファイルパスが明記されている
5. Step 1 (Analyst 並列起動) や Step 2 (Fresh Red Team) に対応する nested Task dispatch が発生していない (中断前の無駄な起動がない)

再検証記録: 2026-07-07。Step 0-2 中断テンプレートに「`{分析ファイルパス}` は絶対パスに置換する」を追記する改修後、fresh executor で本シナリオを再実行し全 [critical] ○ (プレースホルダのまま出力される事象なし)。

## シナリオ: 委譲実行 + risk 領域 (deep tier 強制) — Fresh Red Team 経由の `${CLAUDE_PLUGIN_ROOT}` 自己参照解決 (hold-out)

Task で委譲起動。プラン内容が認証 (auth) 領域を含むため tier=deep が強制され、AC 件数によらず Fresh Red Team が起動する組み合わせ (median/edge シナリオはいずれも Fresh Red Team 非経路のため、この組み合わせのみで検証できる)。

### Requirements checklist
1. [critical] リスク領域検出により tier=deep と判定され、AC 件数によらず Fresh Red Team が起動している
2. [critical] Fresh Red Team subagent 起動時に `${CLAUDE_PLUGIN_ROOT}` が生文字列のまま渡り Read 失敗する形跡がなく、`agents/fresh-red-team.md` および `references/red-team-checklist.md` を正しく参照できている
3. 分析ファイル末尾に MECE 分析結果セクション (Critical/Important/Nice-to-have 分類を含む) が追記されている
4. プランファイルの `## 品質検証` に規定フォーマットの1行が追記されている
5. プラン本文が書き換えられておらず、finding ID がプラン本文に持ち込まれていない
6. 最終メッセージに分析ファイルの絶対パス、MECE判定 (OK/要修正)、Critical 件数が含まれている

---

## シナリオ: lite-mode inline 実行 (AC ≤5 件・非リスク) — ⚠️ v1.34.0 で失効 (lite tier は standard に統合)。現行版は本ファイル末尾「2026-08-02 v1.34.0 改訂」のシナリオ A を使うこと

lite-mode inline 実行経路 (退避案は見送り、現在は SKILL.md inline 記載のまま) を fresh executor で検証する目的のシナリオ。既存 5 シナリオはいずれも lite 経路を通らないため、この経路は本セッションの検証で未カバーだった。将来 lite-mode 周りを変更する際、または退避案を再提案する際に初回 PASS を確認すること。Task で委譲起動、AC 4 件・非リスク領域 (フロント変更のみ) のプラン + 分析ファイル (`### Tier` = lite) を渡す。

### Requirements checklist
1. [critical] AC 件数 (4) と非リスク領域から tier=lite と判定し、Step 1/Step 2 の並列 subagent を dispatch せず BB/WB 2 視点を main agent が inline 実行している (nested Task を起動しない)
2. [critical] Wiki Researcher と Fresh Red Team を skip し、inline BB/WB で Critical 候補 0 のとき「MECE OK / Critical 0」を確定値として 1 行サマリーに記載している
3. inline BB/WB で Critical 候補が 1 件でも出た場合の格上げ (standard へ、auth/billing/payment/migration 露呈時は deep へ) を正しく説明できている
4. 出力が標準と同じ Step 3 形式 (分析ファイル末尾セクション + プラン 1 行サマリー) で提示されている
5. 最終メッセージに分析ファイルの絶対パスと MECE判定 (OK/要修正)・Critical 件数が含まれている

---

再検証記録: 2026-07-17 (v1.30.0)。SKILL.md の DRY 集約を 1 点だけ適用: Step 2 の JSONL 抽出正規表現・2 ブロック連結手順を本文から除き、既に verbatim 保持する [references/dispatch-prompts.md](../skills/mece-plan-review/references/dispatch-prompts.md) Step 2 節 (SSOT) への参照に集約 (⚠️ Red Team freshness 不変条件・二重用途・Task 不可フォールバックは本文に維持)。判定ロジック段梯・チェックリスト・出力テンプレート・skill 間契約の文言 (BB-N/WB-N finding ID・分析ファイル書式) は本文に維持。`git show HEAD` 突き合わせと dispatch-prompts.md 側の content-match で消失ルール 0 を確認。`python3 scripts/validate_skills.py` pass。description は無変更 (Iter 0 でカバレッジ整合を確認)。

検証は保存 5 シナリオを fresh executor (blank slate, Task dispatch) で 1 ラウンド実行し、全シナリオで全 [critical] ○ / 変更起因の新規不明点 0。deep hold-out と median の executor がいずれも Step 2 抽出正規表現を dispatch-prompts.md から特定・適用でき、本集約が navigation を壊さないことを実地確認した。median executor はセッションの nested subagent 上限到達により Red Team を synthesis-and-errors.md 記載の Red Team フォールバックへ決定的に退避したが、これは既定分岐で [critical] は満たしている。deep executor が挙げた新規不明点 2 件 (ac-enumerate.md の観点ラベル既定・init-common.md の委譲時リポ解決順) はいずれも本改修が触れていない別ファイルの既知論点で、過去の再検証記録 (2026-07-07) でも担当外として計上済み。

当初は lite-mode inline 実行手順の references 退避も候補にしたが、その退避内容を検証する lite シナリオが保存 5 シナリオに無く、初回検証に必要な追加ラウンドが共有セッションの subagent 累積上限 (200/200) 到達で dispatch 不可だった。fresh executor 未検証の変更を出荷しない方針で lite-mode 退避は見送り、SKILL.md inline のまま維持した (別セッションで上記 lite-mode シナリオを検証のうえ再提案する)。本セッションで出荷するのは Step 2 集約のみで、これは 1 ラウンドの全 [critical] ○ が完全にカバーしている。

---

再検証記録: 2026-07-18。skill 本文は無変更 (Iter 0 で description の謳うトリガー/範囲と本文カバレッジの整合を確認、乖離なし)。保存 6 シナリオ (Fresh Red Team Unknown 棄権 / Orchestrated 3 連続不一致 / 委譲 median standard / 委譲 edge 中断 / 委譲 deep hold-out / lite-mode inline) を fresh executor (blank slate, Task dispatch) で 1 ラウンド実行し、全シナリオで全 [critical] ○ / accuracy 100% / retries 0。特に **2026-07-17 に「別セッションで検証」と保留されていた lite-mode inline 実行シナリオ (未実行分) を初めて実行し全 [critical] ○** — AC 4 件・非リスクから tier=lite を判定して nested Task を 1 件も起動せず BB/WB を main agent 内で inline 統合、Wiki Researcher / Fresh Red Team を skip、Critical 候補 0 で「MECE OK / Critical 0」を確定値として 1 行サマリーに記載し、格上げ規則 (standard へ、auth/billing/payment/migration 露呈時 deep へ) も正しく説明した。median (standard) は BB が条件付き Critical 候補を挙げたため「迷ったら問題側に倒す」で Fresh Red Team を起動し、タグ付き記事の本文のみ編集時に未送信キーの nil 上書きで既存タグが消える data-loss を Critical 1 件として検出 (要修正)。deep hold-out (auth) は Fresh Red Team 経由の `${CLAUDE_PLUGIN_ROOT}` 自己参照解決を再検証し、検出された auth 系欠陥がいずれも hardening=容易化で Critical 閾値 (単独で害成立) 未達のため Critical 0 / MECE OK と正しく判定 (Critical=0 + Important 多数 = 「MECE OK」の閾値運用が機能)。全 full-flow シナリオ (median/deep) で nested Task の `${CLAUDE_PLUGIN_ROOT}` は絶対パスへ置換されて Read 失敗ゼロ、プラン本文への finding ID 混入ゼロ (orchestrator 側の独立 grep で確認)、プラン本文は `## 品質検証` 1 行追記のみで無改変。executor が挙げた新規不明点は (a) scaffolding 起因 (Fresh Red Team のリポ未チェックアウト条件・decision test で stub した非焦点 AC の充足内訳推論)、(b) 既知の documented 点 (orchestrated 宣言と Step 0-2 即中断ゲートの「記帳しない」規定の優先関係 = orchestrated-mode.md `## Gotchas` に既出)、(c) 結果を歪めない judgment latitude (testable なお見合いのみ `[MECE追加]` AC 化する cutoff・analyst 自己申告 severity と「Critical 候補」ゲートの関係) のいずれかで、[critical] 合否に影響せず skill 欠陥ではないため未修正。100% pass 飽和シナリオは劣化検出器として機能を確認 (capability 改善信号としては扱わない)。skill 無変更のため SKILL.md `## Gotchas` 追記なし。

---

## シナリオ: lite 判定 (median) / lite→deep 格上げ (hold-out) / auth 強制 deep (edge) — Opus 5 / Fable 5 向けチューニング (2026-07-25) — ⚠️ チェックリストは v1.34.0 で改訂済み。現行版は本ファイル末尾「2026-08-02 v1.34.0 改訂」を使うこと (fixture 仕様は下記を継続使用)

保存済み 6 シナリオのうち lite 経路と deep 経路を、今回の変更箇所 (lite-mode inline 手順・tier 表 lite 行・0-4.5 preflight・Step 2) に狙って当てるよう作り直した 3 シナリオ。
チェックリストは凍結済み。**実行は評価意図秘匿 (blind) — executor にチェックリストを渡さない。**

### 実行時の必須注意 (executor 招集契約)

`~/.claude/skills/mece-plan-review/` に **npx skills add 由来の旧コピーが存在しうる**。executor が `/mece-plan-review` を
名前で起動するとその旧コピーを読み、working tree の変更が検証されない。dispatch prompt では checkout 内の
`plugins/mece-plan-review/skills/mece-plan-review/SKILL.md` を **絶対パスに展開して明示し、それを Read させる**こと
(併せて「`~/.claude/skills/mece-plan-review/` は読むな」と明記する)。references / agents も同ディレクトリ配下の絶対パスで解決させ、
`${CLAUDE_PLUGIN_ROOT}/skills/mece-plan-review/` の読み替え先として渡す。

### fixture 仕様 (再作成用)

- **scenA (median, lite)**: `plan_tooltip_copy.md` = 共有ボタン tooltip の文言変更 + hover 遅延 300ms + `aria-label` 追随。フロント表示のみで API / DB / 権限 / 課金に触れないと本文に明記。実装コードは fixture に置かない (WB がコード不可読になる経路)。`plan_tooltip_copy.analysis.md` は `### Tier` = lite、AC 4 件 (正常 2 / 異常 1 / 境界 1、AC-ID 未付与で 0-3 enumerate を通す)。
- **scenB (hold-out, lite→deep 格上げ)**: `plan_invoice_tax_label.md` = 請求書 PDF の合計欄に税率区分内訳行を追加。内訳金額を明細の `tax_rate` から `amount * tax_rate` で再計算し円未満四捨五入と規定。`app/models/invoice.rb` は「端数処理は明細単位で確定させ、合計は確定済み税額の単純合算」とコメント付きで実装済み (`recalculate_total`)、`app/services/invoice_pdf_renderer.rb` は確定済み `item.tax_amount` を描画。→ プラン通りに再計算すると二重丸めで PDF 内訳と経理上の確定税額が食い違う (単独で害が成立する金額誤り = Critical 候補)。`analysis.md` の `### Tier` は上流が **lite と誤分類** (AC 5 件 / 「PDF 表示追加のみ」)。
- **scenC (edge, auth 強制 deep + Devin 未収録)**: `plan_session_reauth.md` = 機密操作前の step-up 再認証 (`require_recent_authentication!` を `ApplicationController` に追加、`ApiTokensController#create` / `Users::EmailsController#update` に `before_action`、`session[:reauthenticated_at]` に記録)。`app/controllers/application_controller.rb` (`require_login!` / `current_user`) と `api_tokens_controller.rb` を実装済みで置く。`analysis.md` の `### Tier` は **standard** (AC 8 件) — auth 領域による強制 deep が記録済み tier に優先するかを見る。fixture は git repo 外なので Devin preflight は `none` に落ちる。

### シナリオ A (median, lite) requirements checklist

1. [critical] AC 4 件 + 非リスク領域から tier=lite と判定し、Step 1 / Step 2 の nested Task を 1 件も dispatch せず BB / WB 2 視点を main agent が inline 実行している
2. [critical] Wiki Researcher と Fresh Red Team を起動せず、Critical 候補 0 のとき「MECE OK / Critical 0」を確定値として 1 行サマリーに記載している
3. [critical] 分析ファイル末尾に MECE 分析結果セクション (Critical / Important / Nice-to-have 分類を含む) を追記し、プランファイル `## 品質検証` に規定フォーマットの 1 行を追記している
4. inline BB / WB の指摘件数を人為的な上限 (1-3 件等) で切らず、該当分のみ挙げている (0 件なら根拠 1 文)
5. コードが fixture に無いことを AC 不備と混同せず、WB 判定を `言及なし` 既定にしたうえで低充足率の理由をコード不可読と明記している
6. プラン本文が書き換えられておらず、finding ID (BB-N / WB-N / IM-N) がプラン本文に持ち込まれていない
7. 最終メッセージに分析ファイルの絶対パスと MECE判定 (OK / 要修正)・Critical 件数が含まれている

### シナリオ B (hold-out, lite→deep 格上げ) requirements checklist

1. [critical] inline BB / WB で Critical 候補 (確定済み明細税額と PDF 側再計算・再丸めの二重丸めによる金額不一致) を検出している
2. [critical] lite 確定を破棄して格上げし、lite サマリーを残さず格上げ後の出力で上書きしている
3. [critical] 格上げ先を standard で止めず **deep** とし、根拠を「finding が lite 分類時に見落とした billing (請求金額) の関与を露呈した」ことに置いている
4. [critical] 格上げ後に Step 1 の Analyst 並列 dispatch と Step 2 Fresh Red Team を実際に実行している (Red Team を skip していない)
5. 上流分析ファイルの `### Tier` = lite の記録を、自身の格上げ判定より優先させていない
6. プラン本文が書き換えられておらず、finding ID がプラン本文に持ち込まれていない
7. 最終メッセージに分析ファイルの絶対パスと MECE判定・Critical 件数が含まれている

### シナリオ C (edge, auth 強制 deep + Devin 未収録) requirements checklist

1. [critical] 分析ファイルの `### Tier` = standard の記録より auth 領域を優先して tier=deep と判定し、Fresh Red Team を必ず起動している
2. [critical] 0-4.5 preflight を 1 回だけ実行して `${DEVIN_COVERAGE}` を確定し、`none` のとき Wiki Researcher を dispatch せず BB + WB の 2 並列にしている (deep でも 3 並列にしない)
3. [critical] Red Team の dispatch 入力に plan 本文 / AC 本文を含めず、BB / WB の JSONL + Wiki 結果のみを渡している
4. [critical] nested Task 起動時に `${CLAUDE_PLUGIN_ROOT}` が生文字列のまま埋め込まれて Read 失敗した形跡がなく、各 subagent が対応する `agents/*.md` を参照できている
5. preflight に `ask_question` を使っていない
6. hardening 不足のみの指摘を Critical へ昇格させず、「それ単独で害が成立するか」で severity を決めている
7. 分析ファイル末尾セクション + プラン 1 行追記があり、プラン本文は無改変 / finding ID 混入なし
8. 最終メッセージに分析ファイルの絶対パスと MECE判定・Critical 件数が含まれている


### Round 1 結果 (2026-07-26, blind 実行・成果物直読みで採点)

| シナリオ | 成否 | accuracy | tool_uses | duration | retries |
|---|---|---|---|---|---|
| A (median, lite) | ○ | 100% (7/7) | 19 | 392s | 0 |
| B (hold-out, lite→deep 格上げ) | ○ | 100% (7/7) | 25 | 1537s | 0 |
| C (edge, auth 強制 deep) | ○ | 100% (8/8) | 24 | 1480s | 0 |

全 [critical] ○。A: lite で dispatch 0・Red Team 非起動・「漏れ 0 は非起動由来」注記。B: 仕込みの二重丸め欠陥を inline で検出→lite 破棄→deep 格上げ (billing 露呈根拠)→Red Team 必須起動、Red Team CR1 は Core rule 4 再適用で Important へ格下げ (監査記録付き)。C: 上流 Tier=standard を auth 強制で deep 上書き・Devin none で BB+WB 2 並列・Red Team が唯一の Critical を検出 (severity 監査記録つき)。

適用した修正 (1 テーマ「dispatch 経路だけが運んでいた契約を bypass/縮退経路へ明示的に運ぶ」、3 点いずれも複数 executor が自力で同一解決に到達した挙動の成文化):
1. tier: リスク領域強制 deep > 上流 `### Tier` 継承の優先順位 + 判定主体 (変更が書き換える対象) + 上書き記録義務 (B/C の 2/2 が指摘)
2. lite inline: agents/bb・wb-analyst.md の事前 Read と Critical 閾値・出力契約の適用、「Critical 候補」= 閾値現該当のみ (A/B の 2/2 が指摘)
3. 0-4.5: `${REPO_NAME}` 構成不能 (non-git) 時は probe を打たず `${DEVIN_COVERAGE}=none` 即確定の分岐 0 を明文化 (A/B/C の 3/3 が同一 short-circuit を自力適用)

記録のみの残差 (各 1 件・出力影響なし): `${WIKI_RESULT}` リテラルの原因別対応表 / その他(MECE追加) の挿入位置アンカー / [MECE追加 変更] のサマリー欄 / タグ条件の操作基準明示 / Red Team の能動取得禁止 / X/M の解釈とワンライナー可読性 / 漏れ 0 の lite 表記 / Task(Agent) 表記統一。

### Round 2 (2026-07-26, 修正後の A 再走 — pristine fixture A2 で実行)

A: ○ 100% (7/7)、tool_uses 16 (Round1 の 19 から改善) / 326s / retries 0。3 修正すべてが実行過程に顕在: (1) agent 定義の事前 Read + Critical 閾値の inline 適用を自己報告で明示 (2) `${REPO_NAME}` 解決不能→probe 省略で外部 MCP 呼び出し 0 (3) lite 維持 + Red Team skip + プラン本文無改変。収束: Round1 A/B/C 全 100% + 修正後 A 再走 100% で実質収束 (修正は全て観測済み正解挙動の成文化であり、B/C 経路の該当修正 (tier 優先順位) も B/C executor の実挙動と同型)。

次回 PR の筆頭修正候補 (lite 経路 2/2 で再発、出力正しさへの影響なし): 「漏れ [Y]件」は lite で構造的に 0 になるため `0件 (Red Team skip のため未検出)` 表記を規定する。他の新規残差 (REPO_NAME の解決不能状態の命名 / enumerate 部分欠落の契約行 / Critical=0 テンプレの見出し DRY / findings 0 件時の空 JSONL 形) は各 1 件・記録のみ。

---

## 2026-08-02 v1.34.0 改訂 — P1-P5 (inline 既定化 / Wiki opt-in / 全文転記廃止 / サマリー強化 / doctor 繰越) 後の現行シナリオ

v1.34.0 の変更: (P1) lite/standard を standard に統合し既定を main agent の inline BB+WB 実行に変更、並列 dispatch は deep のみ。(P2) Wiki Researcher を明示 opt-in 化 (既定非起動)。(P3) 分析ファイルへの元 Markdown 全文 `<details>` 転記を廃止 (JSONL + 合成表のみ)。(P4) 1 行サマリーに `Important [I]件 (うちAC反映 [R]件)` を追加、分析サマリーに実行メタ行を追加。(P5) AC マージ検証節の出力先規定 + M 行 severity 必須フィールド明記。

fixture は 2026-07-25 節の「fixture 仕様 (再作成用)」をそのまま使う (scenA=tooltip / scenB=invoice / scenC=session_reauth)。実行時の必須注意 (checkout 内 SKILL.md を絶対パス指定で Read させる / `~/.claude/skills/` の旧コピーを読ませない) も同節に従う。**実行は評価意図秘匿 (blind) — executor にチェックリストを渡さない。**

### シナリオ A (median, standard inline) requirements checklist

1. [critical] 上流 `### Tier`=lite を standard として読み替え、Step 1 / Step 2 の nested Task を 1 件も dispatch せず BB / WB 2 視点を main agent が inline 実行している (agents/bb・wb-analyst.md を Read し Critical 閾値・出力契約を適用)
2. [critical] Wiki Researcher と Fresh Red Team を起動せず、Critical 候補 0 のとき「MECE OK / Critical 0」を確定し、漏れ件数を `0件 (Red Team skip のため未検出)` と表記している
3. [critical] 分析ファイル末尾に MECE 分析結果セクションを追記し、プラン `## 品質検証` に `Important [I]件 (うちAC反映 [R]件)` 列を含む新フォーマット 1 行を追記している
4. 分析サマリーに実行メタ行 (tier / dispatch 体数 / 経過分) がある
5. 分析ファイルに BB / WB の元 Markdown 全文 (Self-report 等) の `<details>` 転記が無い (JSONL のみ)
6. コードが fixture に無いことを AC 不備と混同せず、WB 判定を `言及なし` 既定にして低充足率の理由をコード不可読と明記している
7. プラン本文が書き換えられておらず、finding ID がプラン本文に持ち込まれていない
8. 最終メッセージに分析ファイルの絶対パスと MECE判定・Critical 件数が含まれている

### シナリオ B (hold-out, standard→deep 格上げ) requirements checklist

1. [critical] inline BB / WB で Critical 候補 (確定済み明細税額と PDF 側再計算・再丸めの二重丸めによる金額不一致) を検出している
2. [critical] finding が billing の関与を露呈したため standard 確定を破棄して deep へ格上げし、inline サマリーを残さず格上げ後の出力で上書きしている
3. [critical] 格上げ後に Step 1 の BB / WB 並列 dispatch と Step 2 Fresh Red Team を実際に実行している (Red Team を skip していない)。Wiki Researcher は opt-in が無いため dispatch していない
4. 上流分析ファイルの `### Tier`=lite の記録を、自身の格上げ判定より優先させていない
5. プラン本文が書き換えられておらず、finding ID がプラン本文に持ち込まれていない
6. プラン 1 行サマリーが新フォーマット (`Important [I]件 (うちAC反映 [R]件)` 列を含む)
7. 最終メッセージに分析ファイルの絶対パスと MECE判定・Critical 件数が含まれている

### シナリオ B2 (hold-out, standard inline → deep 格上げ — コードを読んで初めてリスク領域が露呈する形) requirements checklist

シナリオ B の fixture はプラン文面に「`amount * tax_rate` で再計算」と書かれており、Step 0 の tier 判定 (リスク領域の振る舞い検算) が正しく働くと inline を経由せず直接 deep に入る (Round 1 で観測)。inline → 格上げ経路そのものを検証するには、**プラン文面は非リスクに見え、コードを読んで初めて billing 関与が露呈する** fixture が要る。

**fixture 仕様 (再作成用) — scenB2**: `plan_usage_mail_footer.md` = 月次利用レポートメールのフッターに「今月のご利用合計」を追加表示。値は画面と同じ `StatementSummary.total_for(user)` を**参照**する、メール表示のみで DB 変更なし、と本文に明記 (自己申告としては真正 — 書き手はヘルパーの副作用を知らない想定)。`app/services/statement_summary.rb` は `total_for` 内で利用実績を再集計し `statement_cache` を `update!(total: 再計算値, confirmed: false)` で**上書き**する実装 + 「confirmed: true は請求書発行済みを意味する。上書きすると送付済み請求書と金額がズレる」のコメント付き。`app/mailers/usage_report_mailer.rb` は既存 monthly_report のみ。`analysis.md` の `### Tier` は lite (メールテンプレート 1 ファイル / 表示のみ)、AC 4 件。git repo 外。

> **2026-08-02 改訂 (経路非依存化)**: 当初の checklist は「Step 0 では standard と判定 → inline WB で検出 → 格上げ」という機構を [critical] で固定していたが、Round 2 の実行で executor は tier 節の「振る舞いで検算する」規則に従い **Step 0 で参照先サービスのコードまで確認して billing 該当を検出し、直接 deep に入った** (Round 1 の scenB でも同型)。2 fixture × 2 executor が一貫して Step 0 で先行検出しており、コードから見えるリスクは inline 格上げ経路 (standard 手順 4) より Step 0 検算が構造的に先に発火する。手順 4 は「Step 0 が見落とした場合」の defense-in-depth として本文に残すが、fixture で決定的に到達させることはできない (Step 0 検算と inline WB の読み手が同一 main agent のため)。機構前提の checklist はより安全な正しい挙動を罰する regression になるため、以下の**経路非依存版**へ改訂した。

1. [critical] 上流 `### Tier`=lite の記録を最終判定に優先させず、実行が deep (BB / WB 並列 dispatch + Fresh Red Team 起動) で完結している。deep への到達経路は「Step 0 の振る舞い検算」「standard inline からの格上げ (手順 4)」のどちらでもよいが、billing 関与の根拠が分析サマリーに記録されている
2. [critical] 仕込みの billing 欠陥 (`StatementSummary.total_for` が表示経路から請求確定キャッシュを再計算値で上書きし confirmed を解除する — 送付済み請求書と金額がズレる) を Critical として検出している
3. [critical] Red Team の dispatch 入力に plan 本文 / AC 本文を含めていない
4. Wiki Researcher は opt-in が無いため dispatch していない
5. プラン本文が書き換えられておらず、finding ID がプラン本文に持ち込まれていない。プラン 1 行サマリーが新フォーマット (`Important [I]件 (うちAC反映 [R]件)` 列を含む)
6. 最終メッセージに分析ファイルの絶対パスと MECE判定・Critical 件数が含まれている

### シナリオ C (edge, auth 強制 deep + opt-in なし) requirements checklist

1. [critical] 分析ファイルの `### Tier`=standard の記録より auth 領域を優先して tier=deep と判定し、BB / WB を並列 dispatch し Fresh Red Team を必ず起動している
2. [critical] Wiki Researcher はユーザー opt-in が無いため (preflight 結果によらず) dispatch せず、BB + WB の 2 並列にしている
3. [critical] Red Team の dispatch 入力に plan 本文 / AC 本文を含めず、BB / WB の JSONL + `${WIKI_RESULT}` のみを渡している
4. [critical] nested Task 起動時に `${CLAUDE_PLUGIN_ROOT}` が生文字列のまま埋め込まれて Read 失敗した形跡がなく、各 subagent が対応する `agents/*.md` を参照できている
5. preflight に `ask_question` を使っていない
6. hardening 不足のみの指摘を Critical へ昇格させず、「それ単独で害が成立するか」で severity を決めている
7. 分析ファイルに元 Markdown 全文の `<details>` 転記が無く (JSONL のみ)、分析サマリーに実行メタ行がある
8. プラン本文無改変 / finding ID 混入なし。プラン 1 行サマリーが新フォーマット
9. 最終メッセージに分析ファイルの絶対パスと MECE判定・Critical 件数が含まれている

### 実行記録 (2026-08-02, blind・成果物直読み + self-report 採点)

**Round 1** (v1.34.0 実装直後):

| シナリオ | 成否 | accuracy | retries | 実行メタ | 備考 |
|---|---|---|---|---|---|
| A (standard inline) | ○ | 100% (8/8) | 1 | dispatch 0体 / 4分 | 全 [critical] ○。retries は WB 判定を greenfield 既定へ自己修正した 1 回 |
| B (invoice, 旧機構 checklist) | × (形式) | criticals 実質○ | 0 | dispatch 3体 / 16分 | Step 0 の振る舞い検算で直接 deep 入り。仕込み欠陥は Critical 1 で検出 (Red Team important → main agent がロールバック不能=外部成果物で格上げ、監査記録付き)。機構前提 checklist 項 1 のみ未通過 |
| C (auth 強制 deep) | ○ | 100% (9/9) | 0 | dispatch 3体 / 19分 | Critical 0 維持の閾値運用・Unknown 棄権 2 件・freshness (plan/AC 不送信) すべて適合 |

Round 1 適用修正 (1 テーマ「縮退経路・集計契約の SSOT 穴の成文化」、全件 executor の実挙動の成文化): WIKI_RESULT 確定規則の 0-4.5 一元化 / Red Team skip 時の Step 3 供給規則 / リスク領域の振る舞い検算 / Y=M*+T* の SSOT 化 / [MECE追加 変更]・その他配置の X/M 規則 / Unknown 独立軸 / ロールバック不能の外部成果物条項 (checklist+BB/WB) / area タグはヒント / [MECE追加] 連番採番 / 付随ラベル温存。

**Round 2** (Round 1 修正適用後、pristine fixture):

| シナリオ | 成否 | accuracy | retries | 実行メタ | 備考 |
|---|---|---|---|---|---|
| A2 (standard inline) | ○ | 100% (8/8) | 0 | dispatch 0体 / 3分 | Round 1 修正が実挙動に顕在 (実行メタに振る舞い検算根拠・skip 時 4 分類付与) |
| B2 (mail footer, 経路非依存 checklist) | ○ | 100% (6/6) | 0 | dispatch 3体 / 17分 | Step 0 検算が参照先コードまで確認し billing 検出 → deep。仕込み CR1 + fixture 内在の実バグ 2 件 (全期間合計と当月明細の不一致 / 対象月引数欠落) も Critical 検出。要修正 (Critical 3) で正判定 |

Round 2 適用修正 (同一テーマの続き、全件 1 行の成文化): 境界値欠落時の `不明` 補完 / Critical 未満の実装漏れの操作先 / R と無タグ補足 / 既存欠陥の Critical スコープ (新設出力面での顕在化) / Critical=0 テンプレの列構成 SSOT 宣言 / [MECE追加] 書き戻しは上流の元形式 / X/M 指標の母数下限。

**収束判定**: 全実行シナリオで [critical] 全 ○ (A 系は 2 ラウンド連続 100%)。残 unclear はすべて文書規定の穴で executor が同一解決に自力到達済み → 各 1 行で成文化済み。deep 系の追加ラウンドは 1 回 ~17-20 分で、機構到達不能が確定した格上げ経路の再挑戦に価値が無いため resource cutoff で終了 (ship at 全-critical-pass)。

**failure pattern ledger 追記**:
- **bypass/縮退経路への契約明示漏れ** (初出 2026-07-26): Round 1 で再出現 (WIKI_RESULT 交差 / Red Team skip 時の class 付与者 / 漏れ表記)。dispatch 経路が運んでいた契約を inline / skip 経路が引き継ぐ規定を、経路を新設した同じ PR で書くこと
- **集計定義の対象集合が複数文書に分散して片側更新** (新規): Y の M*/T* 帰属が 3 文書で食い違い。集計値の定義は synthesis-and-errors の SSOT 節 1 箇所に置き他は参照のみ
- **機構前提の regression checklist が正しい挙動の進化で失効** (新規): 「どの経路を通ったか」を [critical] にすると、より安全な early-detection への改善を罰する。checklist は観測可能な結果 (検出・記録・無改変) で書き、経路は備考に落とす

---

## 2026-08-09 v1.35.0 改訂 — スリム化 PR1 (Devin 全削除 / Orchestrated 廃止 / Self-report 縮小 / サマリー簿記縮小 / bb・wb 統合) 後の現行シナリオ

v1.35.0 の変更: (P1) Devin wiki 統合を全削除 (Wiki Researcher subagent / related-repos / 0-4・0-4.5 preflight / BB の wiki 読み。BB の情報源は AC + プラン + 一般知識のみ)。(P2) Orchestrated モード廃止 (呼び出し元オーケストレータ不在の dead code。委譲時の AskUserQuestion 不可分岐は「最終メッセージに含めて終了」に一本化、references/delegated-execution.md へ退避)。(P3) Self-report から「分析所要 (体感)」「確信度」を削除 (「参照したくなった場面」と Red Team の「BB/WB 独立性の質」は分離の計測器として温存)。(P4) プラン 1 行サマリーを `MECE判定 / Important [I]件 (うちAC反映 [R]件) → 分析ファイル名` に縮小 (ACカバレッジ・漏れ・重複・Unknown は分析ファイルの分析サマリーにのみ記録。I/R は tier 実測判定の計器として温存)。(P5) agents/bb-analyst.md + wb-analyst.md を references/analyst-contract.md へ統合 (Critical 閾値の複製は analyst-contract + red-team-checklist の 2 箇所に縮約、sync 義務注記付き)。(P6) output-format.md の Critical=0 複製テンプレを省略規則 1 行に置換。tier 構造 (standard/deep・リスク領域強制・格上げ) と wb 構造化精読 (nested attributes 検出器含む)・greenfield 既定は無変更。

fixture は 2026-07-25 節の「fixture 仕様 (再作成用)」をそのまま使う (scenA=tooltip / scenB2=mail footer / scenC=session_reauth)。実行時の必須注意 (checkout 内 SKILL.md を絶対パス指定で Read させる / `~/.claude/skills/` の旧コピーを読ませない) も同節に従う。**実行は評価意図秘匿 (blind) — executor にチェックリストを渡さない。**

現行 suite は以下 5 本: A (standard inline) / B2 (standard→deep 格上げ) / C (auth 強制 deep) / 委譲 edge (中断) / Fresh Red Team Unknown 棄権。

### シナリオ A (median, standard inline) requirements checklist (v1.35.0 版)

1. [critical] 上流 `### Tier`=lite を standard として読み替え、Step 1 / Step 2 の nested Task を 1 件も dispatch せず BB / WB 2 視点を main agent が inline 実行している (references/analyst-contract.md を Read し BB 節 / WB 節の情報源制約・Critical 閾値・出力契約を適用)
2. [critical] Fresh Red Team を起動せず、Critical 候補 0 のとき「MECE OK / Critical 0」を確定し、分析サマリーの漏れ件数を `0件 (Red Team skip のため未検出)` と表記している
3. [critical] 分析ファイル末尾に MECE 分析結果セクションを追記し、プラン `## 品質検証` に `- MECE判定: OK (Critical: 0) / Important [I]件 (うちAC反映 [R]件) → [分析ファイル名]` 形式の 1 行を追記している (ACカバレッジ・漏れ・重複を 1 行サマリーに含めない)
4. 分析サマリーに実行メタ行 (tier / dispatch 体数 / 経過分) がある
5. 分析ファイルに BB / WB の元 Markdown 全文 (Self-report 等) の `<details>` 転記が無い (JSONL のみ)
6. コードが fixture に無いことを AC 不備と混同せず、WB 判定を `言及なし` 既定にして低充足率の理由をコード不可読と明記している
7. プラン本文が書き換えられておらず、finding ID がプラン本文に持ち込まれていない
8. 最終メッセージに分析ファイルの絶対パスと MECE判定・Critical 件数が含まれている
9. Devin / wiki 系ツールの呼び出し (ToolSearch("+devin") 等) を一切行っていない

### シナリオ B2 (hold-out, standard→deep 格上げ) requirements checklist (v1.35.0 版)

1. [critical] 上流 `### Tier`=lite の記録を最終判定に優先させず、実行が deep (BB / WB 並列 dispatch + Fresh Red Team 起動) で完結している。deep への到達経路は「Step 0 の振る舞い検算」「standard inline からの格上げ (手順 3)」のどちらでもよいが、billing 関与の根拠が分析サマリーに記録されている
2. [critical] 仕込みの billing 欠陥 (`StatementSummary.total_for` が表示経路から請求確定キャッシュを再計算値で上書きし confirmed を解除する — 送付済み請求書と金額がズレる) を Critical として検出している
3. [critical] Red Team の dispatch 入力に plan 本文 / AC 本文を含めていない
4. [critical] BB / WB の dispatch prompt が references/analyst-contract.md を絶対パスで参照し、`${CLAUDE_PLUGIN_ROOT}` が生文字列のまま渡って Read 失敗した形跡がない
5. プラン本文が書き換えられておらず、finding ID がプラン本文に持ち込まれていない。プラン 1 行サマリーが v1.35.0 形式 (`Important [I]件 (うちAC反映 [R]件)` 列を含み、ACカバレッジ・漏れ・重複を含まない)
6. 最終メッセージに分析ファイルの絶対パスと MECE判定・Critical 件数が含まれている

### シナリオ C (edge, auth 強制 deep) requirements checklist (v1.35.0 版)

1. [critical] 分析ファイルの `### Tier`=standard の記録より auth 領域を優先して tier=deep と判定し、BB / WB を並列 dispatch し Fresh Red Team を必ず起動している
2. [critical] dispatch が BB + WB の 2 並列であり、Wiki 系 subagent の起動や Devin 系ツールの呼び出しが無い
3. [critical] Red Team の dispatch 入力に plan 本文 / AC 本文を含めず、BB / WB の JSONL のみを渡している
4. [critical] nested Task 起動時に `${CLAUDE_PLUGIN_ROOT}` が生文字列のまま埋め込まれて Read 失敗した形跡がなく、各 subagent が references/analyst-contract.md / agents/fresh-red-team.md を参照できている
5. hardening 不足のみの指摘を Critical へ昇格させず、「それ単独で害が成立するか」で severity を決めている
6. 分析ファイルに元 Markdown 全文の `<details>` 転記が無く (JSONL のみ)、分析サマリーに実行メタ行がある
7. プラン本文無改変 / finding ID 混入なし。プラン 1 行サマリーが v1.35.0 形式
8. 最終メッセージに分析ファイルの絶対パスと MECE判定・Critical 件数が含まれている

### シナリオ 委譲 edge (中断) requirements checklist (v1.35.0 版 — orchestrated 宣言前提を除去)

Task で委譲起動。プランファイルパスのみ渡す (分析ファイルは意図的に用意しない)。

1. [critical] 起動プロンプト本文で明示されたプランファイルパスを入力として採用しており、`$ARGUMENTS` や `Plan File Info:` の不在を理由に「不足入力」と誤判定していない
2. [critical] 分析ファイルの不在 (`## 受け入れ条件` 未定義) を検知し、SKILL.md 0-2 で規定された中断を実行して Step 1 以降を開始せずに終了している
3. AC を自前で捏造したり、分析ファイルを新規作成して埋めたりしていない
4. 最終メッセージに、分析ファイルが見つからないため検証を中断した旨とプランファイルパス (分析ファイルパスは絶対パス) が明記されている
5. Step 1 (Analyst 並列起動) や Step 2 (Fresh Red Team) に対応する nested Task dispatch が発生していない (中断前の無駄な起動がない)

### シナリオ Fresh Red Team Unknown 棄権 (v1.35.0 版)

入力から Wiki を除いた 2 入力 (BB / WB JSONL) で本ファイル冒頭のシナリオと同じ。checklist は冒頭の 5 項目のまま有効 (Self-report は「BB と WB の独立性の質」「プラン本文 / AC 本文を欲しいと思った場面」の 2 行構成に縮小されている点のみ読み替え)。

### 実行記録 (2026-08-10, v1.35.0 スリム化後の初回 regression。blind・成果物直読み + self-report 採点)

| シナリオ | 成否 | accuracy | retries | 実行メタ | 備考 |
|---|---|---|---|---|---|
| A (standard inline) | ○ | 100% (9/9) | 0 | dispatch 0体 / 4分 | lite→standard 読み替え・Red Team skip・新サマリー形式・analyst-contract 経由の greenfield 既定すべて適合。Devin 系ツール呼び出し 0 |
| B2 (mail footer) | ○ | 100% (6/6) | 0 | dispatch 3体 / 15分 | **inline→deep 格上げ経路 (standard 手順 3) が初めて実地で発火**し正動作。仕込み billing 欠陥を Critical 検出、Red Team severity 1 件を監査記録付き格下げ |
| C (auth 強制 deep) | ○ | 100% (8/8) | 0 | dispatch 3体 / 19分 | 上流 standard を auth 強制で上書き。BB+WB 2 並列 + Red Team 必須。Red Team の Critical 2 件を「現に該当」規則で格下げ (再格上げ条件併記)。freshness (plan/AC 不送信) 維持 |
| 委譲 edge (中断) | ○ | 100% (5/5) | 0 | dispatch 0体 | 0-2 即中断・捏造なし・絶対パス置換済み |
| Fresh Red Team Unknown | ○ | 100% (5/5) | 0 | — | 裏取り全滅 area を severity 捏造せず Unknown 棄権、`(+ Unknown K 件)` 併記。書き込み禁止 1 行が機能しファイル書込 0 |

**収束判定**: 全 5 シナリオ [critical] 全 ○ / 1 ラウンド / 修正 0。bb・wb 統合 (analyst-contract 経由の 2 段参照)・Critical 閾値 2 複製化・新サマリー形式・Devin 全削除・Orchestrated 廃止のいずれも劣化なし。

**記録のみの残差** (全件 executor が自力で妥当解に到達、出力影響なし。次回該当 PR で成文化を検討):
- 中断時 (Step 0-2) の委譲完了報告契約が未明文 (delegated-execution.md は Step 3 完了時のみ規定) / 中断経路で 0-1 の副次取得 (REPO_NAME・T_START) をスキップしてよいか
- 裏取り全滅時の起票回避規則が M 行にのみ明文 (T 行への準用が暗黙) / Red Team `sources` に AC-N を取りうるか / AC 総数のみ (本文抜き) を Red Team dispatch に含めれば AC マージ検証が完全化する改善案
- 標準カテゴリ節が元 AC に無い場合の `[MECE追加]` 追記先 / `### その他（[MECE追加]）` の配置位置と行形式 / コード不可読時の 4 分類ラベル「実装漏れ」の誤読防止注記 (executor は自発的に注記) / WB コード不可読理由 1 行の details 内残置と「元 Markdown 転記禁止」の優先関係
- Critical 閾値類型 4 (回収不能) と「現に該当」規則の噛み合わせ (誤りの成立自体が未確認の仕様前提に依存するケース) / 格上げが分析ファイル書込前に確定した場合の inline サマリー扱い / `[MECE追加]` の採番順 (複数カテゴリ時) / X/M が中間域 (M 10〜25) のときの読み方
- `${REPO_NAME}`=unknown-repo かつ `${CODE_ROOT}` 実在の組み合わせの明示 / main agent が severity 確定のためコードを読んでよいか (Core rule 2 は subagent 役割への制約で main agent の Step 3-1 は未規定) / Critical 0 が格下げ由来の場合の記録先粒度 / 委譲実行時の Agent name パラメータ拒否 (harness 制約)
