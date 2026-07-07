# regression eval (empirical-prompt-tuning 収束時保存)

収束記録: 2026-06-12 (v3.28.0 PR)。Iter1-3 で fresh executor が全 [critical] ○ / accuracy 100% / retries 0。
用途: **regression 検出器** (capability 改善の信号としては使わない)。本 skill を変更する PR では
fresh executor (blank slate, Task dispatch) で下記シナリオを再実行し、全 [critical] ○ を確認してから merge する。
実行方法は empirical-prompt-tuning の「Subagent invocation contract」に従う (成果物はインライン、ファイル編集禁止)。

## シナリオ: tier 競合 + trigger

structural review mode + trigger 判定: (a) 55 行・重複 3 箇所 → 重複箇所数優先で lite (skip にしない)、(b) dry-run 要否は tier 表が canonical (standard/deep で必須)、(c) 「この文書の重複をまとめて」は発火し「重複コードをリファクタして」は発火しない (description の documents-only 除外)。

### Requirements checklist
1. [critical] 必要重複 (TOC / 進捗 table / AC checklist) を DRY 化対象にしない
2. [critical] tier 競合時は重複箇所数を優先 (skip は「重複 ≤2」が必須条件)
3. dry-run 要否の判定が tier 表 (standard/deep 必須) に一本化されている
4. code duplication が scope 外であることが description から読み取れる

---

以下は v0.12.0 (委譲実行契約) 追加分。収束記録: 2026-07-07。fresh executor (Task dispatch) で Iter1-3 + hold-out 1 本の計 7 実行が全 [critical] ○ / accuracy 100% / retries 0。baseline (Iter1) の時点で両シナリオとも critical 項目は全 ○ だった (Task 不使用・対話依存は self-approve 規定で既に解消済みのため)。ただし対象文書パスの入力解決手順が明文化されておらず baseline の合格は fresh executor の一般的な良識に依存していたため、`## 委譲実行` 節を新設し入力解決の優先順位を明記した。また lite tier にしかなかった完了報告 (縮約サマリ + 絶対パス) 要件を tier 共通ルールとして §5 に一本化した。hold-out シナリオ (対象ディレクトリのみ指定、ファイル名は明示せず候補ファイル単一) で accuracy 低下なし (過学習兆候なし)。

## シナリオ: 委譲実行 (対象文書パス明示) で SSOT 集約を完遂する

あなたは dry-ssot-text の実行を Task で委譲された subagent である (対話承認者はいない)。起動プロンプトに対象文書の絶対パスが明示されている。文書は同一概念の説明が複数箇所に重複していると報告されている。

### Requirements checklist
1. [critical] 対象文書内で重複していた概念の説明が 1 箇所 (SSOT) に集約され、他の箇所がクロスリファレンスまたは削除に置き換わっている (`grep -c` で該当フレーズが 1 件のみヒットする状態になっている)
2. [critical] 対話承認者不在で停止せず、tier に応じた dry-run 提示 (または lite の場合は省略) → self-approve 相当の判断 → 適用まで完遂して最終メッセージを返している
3. TOC / 進捗表など navigation 目的の重複箇所は維持されており誤って削除されていない
4. 適用後に「何を何箇所→1 箇所に縮約したか」を示す要約と対象ファイルの絶対パスが最終メッセージに含まれている (tier によらない共通ルール)

## シナリオ: 委譲実行 (対象文書パス未指定 + セッション文脈なし) で不足入力を即時返却する

あなたは dry-ssot-text の実行を Task で委譲された subagent である。起動プロンプトには「さっきの設計文書を DRY にしてください」という session-relative な指示のみがあり、対象文書のパスも本文も含まれない。

### Requirements checklist
1. [critical] `$ARGUMENTS` / 起動プロンプト本文 / セッション文脈のいずれからも対象文書パスを解決できないと認識し、ディレクトリ探索や推測で代替対象を選ばない
2. [critical] 「不足入力: 対象文書パス」相当の内容を最終メッセージとして返し、質問を待たずに即座に終了している
3. 存在しないファイルに対して Write / Edit を実行していない
4. 最終メッセージが「委譲実行では前段の会話履歴 (セッション文脈) を参照できない」旨を明示している

---

以下は G-dry-1 / G-dry-2 追加分。収束記録: 2026-07-07 (規定打ち切り)。Iter1-3 + hold-out で fresh executor が全 [critical] ○ / accuracy 100%。対象が単一文書でなく変更差分全体 (コードコメント 2 箇所 + 変更 md 1 件) の場合の scope 確定・報告統合ルールを検証し、Iter1-2 で観測した不備 (レポートがファイルごとに分かれる、tier 判定が単一ファイルの行数のみで行われる) を SKILL.md 修正で解消した。

## シナリオ: 変更差分全体 (コードコメント + 変更 md) を対象に SSOT 集約する

対象は単一文書ではなく git repo の変更差分全体である。同一の長い Why 説明が 2 つの Ruby ファイルのコメントと 1 つの変更済み md ファイルの本文に重複している (`git diff --name-only` で 3 ファイルが変更対象と分かる)。

### Requirements checklist
1. [critical] dry-run レポートがファイルごとではなく変更セット全体で 1 通に統合されている
2. [critical] コードコメント 2 箇所と md ファイル 1 箇所の重複がファイル横断で検出され、tier 判定が対象ファイル合計の行数・重複箇所数で行われている (単一ファイルの行数だけで判定していない)
3. 対象範囲の確定に `git diff --name-only` 等の変更ファイル一覧が使われている
4. コード構造そのもの (メソッド重複等) は対象外のまま、コメント文面の重複のみが集約対象になっている
