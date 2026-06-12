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
