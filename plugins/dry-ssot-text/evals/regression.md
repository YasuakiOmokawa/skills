# regression eval

Worktree fixtures include unstaged, staged-only, and untracked reader-facing files; all three participate in occurrence counts and tier selection.

## シナリオ: tier 競合 + trigger

trigger 判定: (a) 55 行・重複 3 箇所 → 重複箇所数優先で lite (skip にしない)、(b) dry-run 要否は tier 表が canonical (standard/deep で必須)、(c) 「この文書の重複をまとめて」とコードコメントの重複整理では発火し、コード構造・ロジックの重複整理では発火しない。

### Requirements checklist
1. [critical] 必要重複 (TOC / 進捗 table / AC checklist) を DRY 化対象にしない
2. [critical] この fixture では行数だけで skip にせず、重複 3 箇所を優先して lite と判定する
3. dry-run 要否の判定が tier 表 (standard/deep 必須) に一本化されている
4. prose / code-comment と code structure / logic の境界が description から読み取れる

## シナリオ: 明示 dry-run

単一の linear document に同一説明が4箇所あり、呼び出し側は dry-run のみを明示する。

### Requirements checklist
1. [critical] lite の集約候補と `4 → 1` 計画を報告する
2. [critical] ファイルを編集せず、専用SSOT節やanchorも新設しない
3. 最も完全な既存箇所を保持候補に選ぶ

---

## シナリオ: 委譲実行 (対象文書パス明示) で SSOT 集約を完遂する

あなたは dry-ssot-text の実行を Task で委譲された subagent である (対話承認者はいない)。起動プロンプトに対象文書の絶対パスと「編集まで行う」という親の authority が明示されている。文書は同一概念の説明が複数箇所に重複していると報告されている。

### Requirements checklist
1. [critical] 対象文書内で重複していた概念の説明が 1 箇所 (SSOT) に集約され、他の箇所がクロスリファレンスまたは削除に置き換わっている (`grep -c` で該当フレーズが 1 件のみヒットする状態になっている)
2. [critical] 対話承認者不在でも親から継承した edit authority に従い、tier に応じた inline report (lite の場合は省略可) → 適用まで完遂して最終メッセージを返している
3. TOC / 進捗表など navigation 目的の重複箇所は維持されており誤って削除されていない
4. 適用後に「何を何箇所→1 箇所に縮約したか」を示す要約と対象ファイルの絶対パスが最終メッセージに含まれている (tier によらない共通ルール)
5. [critical] 同じ依頼を review-only / no-edit で委譲した対照 fixture では report 後に停止し、委譲された事実を自己承認の根拠にせず編集しない

## シナリオ: 委譲実行 (対象文書パス未指定 + セッション文脈なし) で不足入力を即時返却する

あなたは dry-ssot-text の実行を Task で委譲された subagent である。起動プロンプトには「さっきの設計文書を DRY にしてください」という session-relative な指示のみがあり、対象文書のパスも本文も含まれない。

### Requirements checklist
1. [critical] `$ARGUMENTS` / 起動プロンプト本文 / セッション文脈のいずれからも対象文書パスを解決できないと認識し、ディレクトリ探索や推測で代替対象を選ばない
2. [critical] 「不足入力: 対象文書パス」相当の内容を最終メッセージとして返し、質問を待たずに即座に終了している
3. 存在しないファイルに対して Write / Edit を実行していない

---

## シナリオ: 変更差分全体 (コードコメント + 変更 md) を対象に SSOT 集約する

対象は単一文書ではなく git repo の変更差分全体である。同一の長い Why 説明が 2 つの Ruby ファイルのコメントと 1 つの変更済み md ファイルの本文に計 6 箇所ある (`git diff --name-only` で 3 ファイルが変更対象と分かる)。

### Requirements checklist
1. [critical] dry-run レポートがファイルごとではなく変更セット全体で 1 通に統合されている
2. [critical] 3 ファイル計 6 箇所の重複がファイル横断で検出され、tier 判定が対象ファイル合計の行数・重複箇所数で行われている (単一ファイルの行数だけで判定していない)
3. 対象範囲の確定に `git diff --name-only` 等の変更ファイル一覧が使われている
4. コード構造そのもの (メソッド重複等) は対象外のまま、コメント文面の重複のみが集約対象になっている
5. [critical] dry-run 後に編集まで完了し、差別化 phrase が 6 箇所から 1 箇所へ集約されている

## シナリオ S5 (median): 重複過多の設計書を委譲実行で SSOT 集約する

82 行の参照付き設計書 (目次 + PR 進捗表 + 受け入れ条件 checklist を含む) に、同一の設計判断の説明が 7 箇所ある。対話承認者不在の委譲実行。

### Requirements checklist
1. [critical] 同一概念の反復説明が 1 箇所 (SSOT) に集約され、残りが削除・クロスリファレンス・縮約のいずれかで解消されている (適用後その説明の本文が 1 箇所だけ)
2. [critical] navigation 目的の重複 (目次 / PR 進捗表 / AC checklist) が維持され、誤って削除・統合されていない
3. [critical] 重複 7 箇所を根拠に standard と判定し、行数を出力 invariant や skip 条件として扱わず、required dry-run を実施している
4. referenced long-form document の置換規則に従っている
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

## シナリオ S7 (edge): scope 外文書から参照される anchor

明示 diff 内の設計書に重複説明があり、その SSOT 見出しを diff 外の README が参照している。README は editable scope に含まれない。

### Requirements checklist
1. [critical] scope 外参照を読むだけで検出し、参照先の既存見出しと anchor をその場に温存する。README は編集しない。
2. [critical] anchor 制約と scope 外参照元を report に記載し、navigation を壊さない配置で重複を集約する。

## シナリオ S8 (holdout): scope 外にも同じ説明がある

editable scope に同一説明が4件あり、入力は scope 外にもより完全な説明1件と別の重複1件があると明示する。

### Requirements checklist
1. [critical] tier、SSOT、`N` は editable 4件だけで決め、scope 外2件を加算・選択・編集しない。
2. [critical] editable scope 内を `4 → 1` にし、scope 外の残存説明を別記する。
3. [critical] scope 外の本文と inbound anchor を変更しない。
