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

収束記録: 2026-07-11 (コメント分岐・複数ファイルスコープ・用語集判定・混在 canonical 規則の追加)。Workflow §3 に「対象がソースコードコメントの場合」の分岐 (canonical 選定・削除/短参照・grep ベース dry-run・express-intent-in-code との実行順序) を新設し、description に複数ファイル横断スコープ、Core Pattern 判定表に「用語集の短い定義 = 必要重複」行、コード+md 混在時の canonical 規則 (md 側の既存専用セクション優先) を追記した。既存 4 シナリオ再実行 + standard tier 強制の差分全体シナリオ + 混在 canonical 机上シナリオの計 6 実行で全 [critical] ○、最終 2 実行は新規不明点 0 で収束。既存 S4 (差分全体) は fixture が lite 境界に落ち dry-run レポートが生成されず req1 が検証不能だったため、重複 6+ 箇所で standard を強制する改訂版への差し替えが望ましい。

---

収束記録: 2026-07-17 (v0.16.0 / progressive disclosure スリム化)。SKILL.md を 150 行 16.3KB → 130 行 14.5KB に縮小。Workflow §3 のクロスリファレンス置換の具体機構 (Before/After 例・置換時の注意 6 項・anchor 生成規則・「対象がソースコードコメントの場合」の canonical 選定手順) を新規 `references/cross-reference-mechanics.md` へ verbatim 退避し、§3 本文には remedy の 3 分岐判断 (長文=アンカー / 線形短文=言い換え+lite 扱い / コードコメント=削除・短参照) を明示のまま残して 1 hop の参照ポインタを置いた。Quick Reference の anchor 生成規則の行も同 reference への参照に置換。挙動変更・ルール統合による希釈は行っていない (`git show HEAD` 突き合わせで §3 の全個別ルールが SKILL.md か reference のいずれかに残存することを確認、消失ルール 0)。description は変更なし (Iter 0 で本文カバレッジとのギャップなしを確認)。

上記 4 シナリオ (S1 tier 競合 / S2 委譲パス明示 / S3 委譲不足入力 / S4 差分全体、S4 は 6 重複で standard を強制する改訂版 fixture) を fresh executor (Task dispatch, blank slate) で 2 連続実行し、両イテレーションとも全 16 [critical] ○ (4 シナリオ × 4 checklist)。surface した不明点はいずれも本スリム化が導入したものではなく、既知の catalogued Gotcha (§3 remedy の型名 vs 行数閾値の tie-break, SKILL.md L119) か、本 PR で触れていない節 (description のキーワード隣接・dry-run override 文言・委譲実行の指示語判定) に関するもので、pre-slim baseline (2026-07-11 収束時) と同じ潜在曖昧点。moved reference の到達性は S2 (両 iter でアンカー remedy を採用し記号を除いた日本語アンカーを正しく生成) と S4 (両 iter で standard tier + コードコメント canonical 規則をワンホップ経由で適用) が実証した。過学習チェック用の hold-out (standard tier の長文 RFC + 記号入り見出しのアンカー生成) はセッションの subagent spawn 上限到達により未実行 — ただし移動した anchor 生成規則・AC 括弧規則は S2 が実質的に踏んでおり、規則本文は HEAD から verbatim で不変。`python3 scripts/validate_skills.py` pass。

---

収束記録: 2026-07-25 (Opus 5 / Fable 5 向け最適化)。以下の 3 シナリオ (S5 median / S6 edge / S3 委譲不足入力を hold-out として再利用) を fresh executor (Task dispatch, blank slate) で 9 ラウンド・計 23 実行し、**全ラウンドで全 [critical] ○ / accuracy 100% / 最終ラウンドは両シナリオ retries 0**。hold-out は 4 実行すべて 100% (過学習兆候なし)。Iter 0 で description と本文のカバレッジ乖離なしを確認 (description 無変更)。

最適化の内容: 重複記述の削除 (grep 到達性の規則が 3 箇所にあったのを §3 に一本化、Quick Reference 節が tier 表と §2 を再掲していたので削除し `grep -nE` の recipe だけ §1 へ移設) と、旧 `## Gotchas` の 3 件 (§3 remedy の型名 vs 行数閾値の tie-break / express-intent-in-code「前段」の解釈 / skip 時の完了報告) を本文の規則へ昇格。以降のラウンドで surface した曖昧点のうち outcome に影響するものを規則化した: tier 行数下限の一般化、全文包含なら削除・独自事実ありならアンカー参照 (判定は段落単位)、ADR / RFC のテンプレート必須節は見出しを残して 1 行参照 (見出しごと削除は自由記述の章のみ)、md 側候補が複数なら根拠側を canonical、正本へ識別子を書き足して到達性を作らない、検証フレーズは参照 1 文に残らない差別化句から選ぶ、Core Pattern に「同一事実の役割違い提示」行を追加 (逐語一致なら例外不可)。executor 自己申告は orchestrator 側で独立検証済み (canonical フレーズ `grep -c` 7→1 / アンカー全件疎通 / TOC・進捗表・AC 維持 / `ruby -c` Syntax OK / 非コメント行 diff 0 / ADR 必須節 5 見出し保持)。残存曖昧点 3 件は SKILL.md `## Gotchas` に記載。`python3 scripts/validate_skills.py` pass。

## シナリオ S5 (median): 重複過多の設計書を委譲実行で SSOT 集約する

82 行の設計書 (目次 + PR 進捗表 + 受け入れ条件 checklist を含む) に、同一の設計判断の説明が 7 箇所ある。対話承認者不在の委譲実行。tier は行数 (skip 帯) と重複箇所数 (standard 帯) が競合し、remedy は文書型 (design doc) と行数閾値 (~150 行以下) が競合する。

### Requirements checklist
1. [critical] 同一概念の反復説明が 1 箇所 (SSOT) に集約され、残りがクロスリファレンスまたは縮約に置き換わっている (適用後その説明の本文が 1 箇所だけ)
2. [critical] navigation 目的の重複 (目次 / PR 進捗表 / AC checklist) が維持され、誤って削除・統合されていない
3. [critical] tier 判定を明示し、行数と重複箇所数が別 tier を指す競合を規定どおり解決している (根拠の行数と重複箇所数を報告)。判定 tier が要求する dry-run の扱いも規定どおり
4. remedy の 3 分岐のどれを選んだか明示し、分岐規定 (tie-break 含む) に整合している
5. 各 PR 章が参照リンクだけの章になっておらず、章のスコープ説明が残っている
6. 最終メッセージに「何箇所 → 1 箇所」の要約と対象文書の絶対パスが含まれている

## シナリオ S6 (edge): 変更差分全体 (コードコメント + ADR) を SSOT 集約する

git repo の未コミット差分 3 ファイル (Ruby 2 ファイル + ADR 1 ファイル、合計 104 行) に同一の why 説明が 6 箇所。ADR 内では §背景 と §根拠 が逐語一致し、§影響 は同じ数値を役割違いで持つ。2 クラスに `with_backoff` / `backoff_interval` のコード構造重複があり、これは対象外。

### Requirements checklist
1. [critical] dry-run レポートが変更セット全体で 1 通に統合されている (ファイルごとに分割していない)
2. [critical] tier 判定を明示し、判定単位が変更セット全体 (対象ファイル合計行数・重複箇所数) になっている (単一ファイルの行数だけで判定していない)
3. [critical] コード構造 (重複メソッド定義・ロジック) は無改変で、コメント文面の重複だけが集約対象 (`ruby -c` Syntax OK)
4. 対象範囲の確定に `git diff --name-only` 等の変更ファイル一覧を使っている
5. canonical の置き場所と非正本の扱い (削除 / 短い参照 / 見出し保持) が規定どおり
6. 最終メッセージに「何箇所 → 1 箇所」の要約と対象ファイルの絶対パスが含まれている

---

収束記録: 2026-07-18 (regression 再実行 / skill 無変更で収束確認)。上記 4 シナリオ (S1 tier 競合 40 行3重複 / S2 委譲パス明示 94 行3重複 / S3 委譲不足入力 / S4 差分全体 6 重複 standard 強制) を fresh executor (Task dispatch, blank slate) で各 1 本ずつ実行し、全 16 [critical] ○ (4 シナリオ × 4 checklist) / accuracy 100% / retries 0。Iter 0 で description と本文のカバレッジ乖離なしを確認 (2026-07-17 と同じ、description 無変更)。executor 自己申告を orchestrator 側で独立検証: S2 は canonical フレーズ `grep -c` 3→1・アンカー参照 4 箇所・TOC/進捗表/AC 維持、S4 は Why occurrence 6→1 (canonical=md 専用セクション)・`with_backoff`/`backoff_interval` 両ファイル温存 (コード構造無改変)・両 Ruby に md への grep 到達可能な 1 行参照残置・`ruby -c` Syntax OK、S1 は review-only で fixture 無改変、いずれも real skill 本体 (`git status` clean) 無改変。surface した不明点はいずれも新規の skill 欠陥ではない: S1/S2 は既知 catalogued Gotcha (§3 remedy の型名 vs 行数閾値 tie-break, SKILL.md L119)、S4-(a) 混在 canonical (md) 時の削除 vs 1 行参照は cross-reference-mechanics.md L30「コード側コメントは全て短い参照に統一する」が既に規定済みで executor は正しく参照側を選択 (一般則「削除可」との perceived tension だが specific rule が支配)、S4-(b)「箇所=ファイル数か occurrence 数か」は eval checklist の文言 (「コードコメント 2 箇所」=2 ファイルの意) 起因の scaffolding 語彙差で skill 欠陥ではない。新規 skill 欠陥不明点 0。skill 本文・references 無変更 (2026-07-17 収束を直前クリアとして本日 1 ラウンドで確定)。`python3 scripts/validate_skills.py` pass。
