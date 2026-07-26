# regression eval (empirical-prompt-tuning 収束時保存)

収束記録: 2026-06-12 (v3.28.0 PR)。Iter1-3 で fresh executor が全 [critical] ○ / accuracy 100% / retries 0。
用途: **regression 検出器** (capability 改善の信号としては使わない)。本 skill を変更する PR では
fresh executor (blank slate, Task dispatch) で下記シナリオを再実行し、全 [critical] ○ を確認してから merge する。
実行方法は empirical-prompt-tuning の「Subagent invocation contract」に従う (成果物はインライン、ファイル編集禁止)。

## シナリオ: Fresh Red Team / Unknown 棄権 (agents/fresh-red-team.md + references/red-team-checklist.md)

BB/WB findings JSONL (auth で両者言及 = 補強し合う合意 / 弱い evidence「推測」の WB finding / observability は両者言及ゼロ + Wiki 無し + リポジトリ読取不能) を与え、統合評価レポートを出させる。プラン本文・AC 本文は渡さない。

### Requirements checklist
1. [critical] フォーマット通りの JSONL 4 ブロック + Markdown を出力 (0 件ブロックは根拠 1 文)
2. [critical] 裏取り材料ゼロの領域を「判定不能 (Unknown)」に理由付きで計上し、漏れ件数行に `(+ Unknown K 件は未確定)` を併記。M 行 (お見合い JSONL) に severity を捏造しない
3. 弱い evidence (推測) は原則 4 で問題側に倒す (Unknown にしない)
4. 補強し合う合意のマージ (根拠の層が仕様/コードで異なる) + Critical 閾値 (単独で害成立) で severity 決定
5. AC 判定の片側欠落時は「AC マージ検証」で subagent 不全シグナルとして再取得を指示 (両側そろえば省略)

再検証記録: 2026-07-07。M ブロックの perspective 値から「純技術リスク補完」を除外し T ブロックへ排他的に振り分ける旨、および漏れ件数を M+T 合算とする旨を明文化する改修後、fresh executor で本シナリオを 2 ラウンド再実行し該当 2 項目 (M/T 振り分け・漏れ件数式) は全 ○。ただし「証拠ゼロの領域で T ブロックへ能動的に起票してよい範囲と Unknown 棄権原則の優先順位」「AC マージ検証が件数比較のみで ID 集合比較でない」の 2 点が新たな不明点として残った (規定打ち切り、詳細は本 skill 外の運用記録を参照)。

---

以下は v1.24.0 (Orchestrated モード / escalation ledger) 追加分。収束記録: 2026-07-05。fresh executor で Iter1-3 全 [critical] ○ / retries 0 (Iter1 で採番規則・語彙揺れ等の仕様ギャップを検出し修正後に再収束)。

## シナリオ: Orchestrated モードで BB/WB 3 連続不一致が安全側に倒れて続行する (Step 1-2)

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

### Requirements checklist
1. [critical] 分析ファイル末尾に MECE 分析結果セクション (Critical/Important/Nice-to-have 分類を含む) が追記されている
2. [critical] Step 1/Step 2 の nested Task 起動で `${CLAUDE_PLUGIN_ROOT}` が生文字列のまま埋め込まれて Read 失敗が起きた形跡がなく、各 subagent が対応する `agents/*.md` を参照できている
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

## シナリオ: lite-mode inline 実行 (AC ≤5 件・非リスク) — 将来検証用、未実行

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

## シナリオ: lite 判定 (median) / lite→deep 格上げ (hold-out) / auth 強制 deep (edge) — Opus 5 / Fable 5 向けチューニング (2026-07-25)

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
