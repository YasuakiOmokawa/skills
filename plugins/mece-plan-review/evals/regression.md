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

---

以下は v1.24.0 (Orchestrated モード / escalation ledger) 追加分。収束記録: 2026-07-05。fresh executor で Iter1-3 全 [critical] ○ / retries 0 (Iter1 で採番規則・語彙揺れ等の仕様ギャップを検出し修正後に再収束)。

## シナリオ: Orchestrated モードで BB/WB 3 連続不一致が安全側に倒れて続行する (Step 1-2)

Task 起動プロンプトに「orchestrated モードで実行。escalation は `plan.escalation-ledger.md` に記帳して続行せよ」の明示指示あり。Step 1-2: BB/WB の AC 判定行数が `${ENUMERATED_AC}` (12 件) と 3 回連続で不一致 (AC-9 の判定行が毎回欠落、補完自体が成立しない出力破損が続く)。この状況で取るアクションを答えさせる。

### Requirements checklist
1. [critical] AskUserQuestion で停止しない。AC-9 を `judgment:"言及なし"` で補完したうえで、AC-9 を Critical 扱いとして escalation ledger に記帳する
2. [critical] 記帳後、Step 2 (Fresh Red Team) 以降の処理を続行する (レビュー全体を中断しない)
3. escalation ledger の記帳行が `| 番号 | 出所 | 深刻度 | 内容 | 根拠 | 推奨アクション |` の列構成に従う
4. Step 3-4 の 1 行サマリーで escalation ledger 記帳分を Critical 件数に算入する (安全側に倒した分を「MECE OK」に混入させない)

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

## シナリオ: 委譲実行 + risk 領域 (deep tier 強制) — Fresh Red Team 経由の `${CLAUDE_PLUGIN_ROOT}` 自己参照解決 (hold-out)

Task で委譲起動。プラン内容が認証 (auth) 領域を含むため tier=deep が強制され、AC 件数によらず Fresh Red Team が起動する組み合わせ (median/edge シナリオはいずれも Fresh Red Team 非経路のため、この組み合わせのみで検証できる)。

### Requirements checklist
1. [critical] リスク領域検出により tier=deep と判定され、AC 件数によらず Fresh Red Team が起動している
2. [critical] Fresh Red Team subagent 起動時に `${CLAUDE_PLUGIN_ROOT}` が生文字列のまま渡り Read 失敗する形跡がなく、`agents/fresh-red-team.md` および `references/red-team-checklist.md` を正しく参照できている
3. 分析ファイル末尾に MECE 分析結果セクション (Critical/Important/Nice-to-have 分類を含む) が追記されている
4. プランファイルの `## 品質検証` に規定フォーマットの1行が追記されている
5. プラン本文が書き換えられておらず、finding ID がプラン本文に持ち込まれていない
6. 最終メッセージに分析ファイルの絶対パス、MECE判定 (OK/要修正)、Critical 件数が含まれている
