# regression eval (empirical-prompt-tuning 収束時保存)

収束記録: 2026-06-12 (v3.28.0 PR)。Iter1-3 で fresh executor が全 [critical] ○ / accuracy 100% / retries 0。
用途: **regression 検出器** (capability 改善の信号としては使わない)。本 skill を変更する PR では
fresh executor (blank slate, Task dispatch) で下記シナリオを再実行し、全 [critical] ○ を確認してから merge する。
実行方法は empirical-prompt-tuning の「Subagent invocation contract」に従う (成果物はインライン、ファイル編集禁止)。

## シナリオ: Fresh Red Team / Unknown 棄権 (agents/fresh-red-team.md + references/red-team-checklist.md)

BB/WB findings JSONL (auth で両者言及 = 補強し合う合意 / 弱い evidence「推測」の WB finding / observability は関与シグナルなし) を与え、統合評価レポートを出させる。プラン本文・AC 本文は渡さない。

### Requirements checklist
1. [critical] フォーマット通りの JSONL 4 ブロック + Markdown を出力 (0 件ブロックは根拠 1 文)
2. [critical] 関与シグナルのない observability を Unknown や M 行へ起票せず、「レビュー範囲外」に記録する。関与シグナルはあるが必要証拠がない領域だけを Unknown とし、該当時は漏れ件数行へ `(+ Unknown K 件は未確定)` を併記する
3. 弱い evidence (推測) は原則 4 で問題側に倒す (Unknown にしない)
4. 補強し合う合意のマージ (根拠の層が仕様/コードで異なる) + Critical 閾値 (単独で害成立) で severity 決定
5. AC 判定の片側欠落時は「AC マージ検証」で subagent 不全シグナルとして再取得を指示 (両側そろえば省略)

再検証記録: 2026-07-07。M ブロックの perspective 値から「純技術リスク補完」を除外し T ブロックへ排他的に振り分ける旨、および漏れ件数を M+T 合算とする旨を明文化する改修後、fresh executor で本シナリオを 2 ラウンド再実行し該当 2 項目 (M/T 振り分け・漏れ件数式) は全 ○。ただし「証拠ゼロの領域で T ブロックへ能動的に起票してよい範囲と Unknown 棄権原則の優先順位」「AC マージ検証が件数比較のみで ID 集合比較でない」の 2 点が新たな不明点として残った (規定打ち切り、詳細は本 skill 外の運用記録を参照)。

---

以下は v1.24.0 (Orchestrated モード / escalation ledger) 追加分。収束記録: 2026-07-05。fresh executor で Iter1-3 全 [critical] ○ / retries 0 (Iter1 で採番規則・語彙揺れ等の仕様ギャップを検出し修正後に再収束)。

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

## 2026-08-09 v1.35.0 改訂 — スリム化 PR1 (Devin 全削除 / Orchestrated 廃止 / Self-report 縮小 / サマリー簿記縮小 / bb・wb 統合) 後の現行シナリオ

v1.35.0 の変更: (P1) Devin wiki 統合を全削除 (Wiki Researcher subagent / related-repos / 0-4・0-4.5 preflight / BB の wiki 読み。BB の情報源は AC + プラン + 一般知識のみ)。(P2) Orchestrated モード廃止 (呼び出し元オーケストレータ不在の dead code。委譲時の AskUserQuestion 不可分岐は「最終メッセージに含めて終了」に一本化、references/delegated-execution.md へ退避)。(P3) Self-report から「分析所要 (体感)」「確信度」を削除 (「参照したくなった場面」と Red Team の「BB/WB 独立性の質」は分離の計測器として温存)。(P4) プラン 1 行サマリーを `MECE判定 / Important [I]件 (うちAC反映 [R]件) → 分析ファイル名` に縮小 (ACカバレッジ・漏れ・重複・Unknown は分析ファイルの分析サマリーにのみ記録。I/R は tier 実測判定の計器として温存)。(P5) agents/bb-analyst.md + wb-analyst.md を references/analyst-contract.md へ統合 (Critical 閾値の複製は analyst-contract + red-team-checklist の 2 箇所に縮約、sync 義務注記付き)。(P6) output-format.md の Critical=0 複製テンプレを省略規則 1 行に置換。tier 構造 (standard/deep・リスク領域強制・格上げ) と wb 構造化精読 (nested attributes 検出器含む)・greenfield 既定は無変更。

fixture は上の scenA=tooltip / scenC=session_reauth を使う。scenB2 は自己完結した次の fixture: plan は「月次 statement mail footer に表示用の予測合計を追加」とだけ記載し、上流 Tier=lite、AC 7件。コードの `StatementSummary.total_for` は表示経路から請求確定 cache を再計算値で上書きして `confirmed` を解除する。この billing 副作用は plan/AC からは分からず、standard WB のコード確認で初めて判明する。実行は評価意図秘匿とし、executor に checklist を渡さない。

現行 suite は以下 5 本: A (standard inline) / B2 (standard→deep 格上げ) / C (auth 強制 deep) / 委譲 edge (中断) / Fresh Red Team Unknown 棄権。

### シナリオ A (median, standard inline) requirements checklist (v1.35.0 版)

1. [critical] 上流 `### Tier`=lite を standard として読み替え、Step 1 / Step 2 の nested Task を 1 件も dispatch せず BB / WB 2 視点を main agent が inline 実行している (references/analyst-contract.md を Read し BB 節 / WB 節の情報源制約・Critical 閾値・出力契約を適用)
2. [critical] Fresh Red Team を起動せず、Critical 候補 0 のとき「MECE OK / Critical 0」を確定し、分析サマリーの漏れ件数を `0件 (Red Team skip のため未検出)` と表記している
3. [critical] 分析ファイル末尾に MECE 分析結果セクションを追記し、プラン `## 品質検証` に `- MECE判定: OK (Critical: 0) / Important [I]件 (うちAC反映 [R]件) → [分析ファイル名]` 形式の 1 行を追記している (ACカバレッジ・漏れ・重複を 1 行サマリーに含めない)
4. 分析サマリーに実行メタ行 (tier / dispatch 体数) がある
5. 分析ファイルに BB / WB の元 Markdown 全文 (Self-report 等) の `<details>` 転記が無い (JSONL のみ)
6. コードが fixture に無いことを AC 不備と混同せず、WB 判定を `言及なし` 既定にして低充足率の理由をコード不可読と明記している
7. プラン本文が書き換えられておらず、finding ID がプラン本文に持ち込まれていない
8. 最終メッセージに分析ファイルの絶対パスと MECE判定・Critical 件数が含まれている
9. Devin / wiki 系ツールの呼び出し (ToolSearch("+devin") 等) を一切行っていない

### シナリオ B2 (hold-out, standard→deep 格上げ) requirements checklist (v1.35.0 版)

1. [critical] 上流 `### Tier`=lite を standard として inline BB/WB を開始し、WB がコードだけから billing 副作用を検出した時点で standard 結果を破棄して deep の BB/WB 並列 + Fresh Red Team をやり直す。billing 関与の根拠を分析サマリーに記録する
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
6. 分析ファイルに元 Markdown 全文の `<details>` 転記が無く (JSONL のみ)、分析サマリーに tier / dispatch の実行メタ行がある
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
