# regression eval (empirical-prompt-tuning 収束時保存)

収束記録: 2026-06-12 (v3.28.0 PR)。Iter1-3 で fresh executor が全 [critical] ○ / accuracy 100% / retries 0。
用途: **regression 検出器** (capability 改善の信号としては使わない)。本 skill を変更する PR では
fresh executor (blank slate, Task dispatch) で下記シナリオを再実行し、全 [critical] ○ を確認してから merge する。
実行方法は empirical-prompt-tuning の「Subagent invocation contract」に従う (成果物はインライン、ファイル編集禁止)。

## シナリオ: lite tier + 注入非対応

$ARGUMENTS なし (default base = develop)。1 commit 済み + 未コミット 1 ファイル、single domain、<50 LoC、既存 pattern 踏襲。自動取得節は生コマンド文字列のまま。コマンド列と判断を列挙させ、(a) ユーザー確認の有無 (b) tier と評価時点 (c) Step 9 観点 (d) Pre-work 点数を明答させる。

### Requirements checklist
1. [critical] ユーザーへの確認・質問を一切行わず draft PR 作成まで進む (disallowed-tools: AskUserQuestion)
2. [critical] tier = lite、評価時点は Step 1 の git log [base]..HEAD 時点 (Step 2 の commit は数えない)
3. Step 9 は [A]+[D] の 2 観点のみ、Pre-work 本質リストは 1-2 点
4. fallback で git status -sb / git log --oneline -15 を Bash 実行
5. PR body は mktemp、milestone 確認は --paginate
