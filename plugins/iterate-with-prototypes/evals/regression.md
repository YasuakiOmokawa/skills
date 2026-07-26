# regression eval (empirical-prompt-tuning 収束時保存)

収束記録: 2026-06-12 (v3.28.0 PR)。Iter1-3 で fresh executor が全 [critical] ○ / accuracy 100% / retries 0。
用途: **regression 検出器** (capability 改善の信号としては使わない)。本 skill を変更する PR では
fresh executor (blank slate, Task dispatch) で下記シナリオを再実行し、全 [critical] ○ を確認してから merge する。
実行方法は empirical-prompt-tuning の「Subagent invocation contract」に従う (成果物はインライン、ファイル編集禁止)。

## シナリオ: 静的チェック + ledger 規律

structural review mode: description (negative trigger 含む) と本文の整合、および「Start here」step 3 の ledger 規律を確認する。

### Requirements checklist
1. [critical] ledger の status が unverified / grounded / killed の 3 値で、grounded の立証責任は証拠側 (照合不能なら unverified のまま step 1 へ戻る) と読み取れる
2. [critical] ガードレール: 戻しにくい決定 (DB スキーマ / 公開 API 契約) では code-first 不可 → design-first or 狭い spike + ADR、と読み取れる
3. Common mistakes「相対比較で合否を決めない (ground-truth への絶対値で出す)」が維持されている

## シナリオ: finalize-plan への合流分岐 (step 5 完走 vs ledger 駆動 vs 前提崩れ)

fresh executor に The loop 表とその直下の note (step 4→6 の note 群) を渡し、次の 3 パターンで step 6 の挙動を判定させる: (a) step 5 (`/define-acceptance-criteria` → `/mece-plan-review`) を完走し `<plan>.analysis.md` に `## 受け入れ条件` `## MECE分析結果` が揃った状態、(b) step 4-5 自体を省略し分析ファイルが一度も無いまま ledger 駆動で step 6 に進む状態、(c) 周回途中で DB スキーマ変更のような戻しにくい決定が必要になった状態。

### Requirements checklist
1. [critical] (a) では `/finalize-plan` を通常どおり起動すると判定し、AC/MECE 欠落のまま finalize-plan の即中断ゲートを迂回する提案をしない
2. [critical] 合流手順が実行順で書ける: 「step5 完走 → 分析ファイル成立 → finalize-plan 通常起動」(a) と「step4-5 省略 → ledger 追記代替」(b) の分岐を取り違えない
3. (c) では loop を中断し `When to use` のガードレールに従って design-first (`/mece-plan-review` 等の実装前ゲート) へ切り替えると判定される

収束記録: 2026-07-06 (v0.11.0 PR)。初回実行で全 [critical] ○ (合流分岐 (a)/(b)/(c) の 3 判定とも規定どおり)。

## シナリオ: 委譲実行 — 新規開始 (median)

fresh subagent (Task 経由起動、AskUserQuestion 不可) に PRD のみを渡し「ledger 未作成」の背景で Start here を実行させる。出力先ディレクトリには起動前提 (ledger 未作成) と矛盾する既存 ledger 相当ファイル (別の内容の proto-ledger.md、シードされたノイズ) を意図的に同居させ、対象特定の優先順位を確認する。

### Requirements checklist
1. [critical] 出力先ディレクトリ配下に「主張 / 検証方法 / kill 条件 / status」の 4 列を持つ ledger ファイルが新規作成されている
2. [critical] 訂正者 (人間) が介在しない状況でも仮定ランキング案を自ら確定し、ledger 作成まで処理が停止せず完了している (返答待ちで止まっていない)
3. [critical] 起動プロンプトの前提と矛盾する既存ファイル (シードされたノイズ) を対象に含めず、独立に新規 ledger を作成している (既存ファイルは削除せず、そう判断した経緯を新ファイルに残す)
4. ledger の各行の検証方法が、ground-truth 照合対象・percentile 等の閾値・代表入力のいずれかを含む実行可能な記述になっている
5. ledger の status 列が `unverified` / `grounded` / `killed` の 3 値以外を含まない
6. ledger 冒頭に方法論用語 (ledger / spike / kill 条件 等) の glossary ブロックが置かれている
7. 最終メッセージに作成した ledger の絶対パスが含まれている

収束記録: 2026-07-07 (本チューニング PR、version bump は後続で一括実施)。Iter1-5 で fresh executor が全 [critical] ○ / accuracy 100%。ノイズファイルの扱いは Iter3 までは「対象が曖昧」という不明点が残ったが、Iter4 (既定ファイル名 `assumption-ledger.md` + 削除せず経緯を残す規則を明文化) 以降は解消。

## シナリオ: 委譲実行 — 既存 ledger からの再開 (edge)

fresh subagent に既存 ledger (status 列に unverified/grounded が混在し、「現在地」が裏付け実体の無い完了状態を主張している proto-ledger.md) のパスのみを渡し、続きを実行させる。

### Requirements checklist
1. [critical] 既存 ledger を Read し、その status 列の内容に基づいて再開する step を判定している (仮定抽出を最初からやり直していない)
2. [critical] 最終メッセージに「更新した ledger の該当行」と「次に呼ぶべき step」の両方が明示されている
3. 「現在地」が主張する完了状態 (例: Code-A 実装済み) の裏付けとなる実体を確認できない場合、その完了状態を根拠にせず対応する仮定を unverified のまま扱っている
4. ledger 内で既に `unverified` / `grounded` / `killed` が入っている行の値を、新たな検証を経ずに書き換えていない
5. ledger 冒頭の glossary ブロックを重複生成せず、既存のものを維持している

収束記録: 2026-07-07 (本チューニング PR、version bump は後続で一括実施)。Iter1-5 で fresh executor が全 [critical] ○ / accuracy 100%。「現在地の完了状態を裏付け実体で検証する」判断自体は Iter1 から一貫して機能していたが、自分で現在地を更新する際に根拠パスを書き添えない再発が Iter2-4 で観測されたため、Iter4 で「現在地を更新する際は根拠ファイルパスを同じ文に書き添える」規則を追加した。

## シナリオ: 委譲実行 — 再開 + ノイズ (hold-out, 汎化確認用)

既存 ledger からの再開シナリオに、ツール自身の既定ファイル名 (`assumption-ledger.md`) と偶然一致するノイズファイル (起動プロンプト未言及、PRD の設計制約と矛盾する内容) を同居させ、「起動プロンプトの明示情報が対象を決める」原則がファイル名の見た目に引きずられず機能するかを確認する。

### Requirements checklist
1. [critical] 起動プロンプトが明示したファイルを対象として Read し、そこから再開している (ディレクトリ内の別ファイルに対象をすり替えていない)
2. [critical] 起動プロンプト未言及のファイルの内容を正本判断や status 更新の根拠として引用していない
3. 最終メッセージに「更新した ledger の該当行」と「次に呼ぶべき step」の両方が明示されている

収束記録: 2026-07-07 (tuner 自作 hold-out、初回実行で全 [critical] ○。直近平均 (Iter4-5: 100%) からの accuracy 低下なし → 過学習兆候なし)。

## シナリオ: PoC専用委任 vs 実装明示委任 (ledger+spike で止まる vs Code-A へ進む)

同一 PRD (クリップボードから画像を貼り付けて添付する小機能。要件は境界条件込みで PRD に明記し、うち 1 件は Node 一本の spike で実行可能、もう 1 件はブラウザ実機が要り本セッションでは検証不能、という 2 仮定構成にする) に対し、依頼文だけを変えた 2 パターンを fresh executor に渡す。

- median: 「PRD から PoC をつくりたい。検証したい仮説を『主張 / 検証方法 / kill 条件』の ledger にしてから spike して」(ledger 化と spike 検証のみを依頼)
- edge: 「最上位仮定は grounded 済み(ledger 添付)。PRD を網羅する Code-A を実装して」(grounded 済み ledger を添付し、実装を明示依頼)

### Requirements checklist
1. [critical] median: 最上位仮定の spike を実際に実行し grounded/killed の verdict を確定した時点で作業を終え、Code-A (PRD 網羅実装) には着手しない
2. [critical] edge: 添付 ledger の grounded 判定を新たな検証なしに受け入れ、PRD 要件を網羅する Code-A (動くコード) の実装まで進む (ledger 追記や spike のみで終わらない)
3. median: 実行不能な仮定 (ブラウザ実機が要る等) は根拠なく grounded と判定せず unverified のまま扱われる
4. edge: 対象コードベースが渡されていない場合、Code-A は特定フレームワークに依存しない standalone モジュールとして書かれ、実システムへの組み込み点がコメントで明示される
5. 両パターンとも ledger 冒頭に glossary ブロックがあり、status 列は unverified / grounded / killed 以外を含まない

収束記録: 2026-07-07 (本チューニング PR)。Iter1-4 で median/edge とも全 [critical] ○ / accuracy 100% / retries 0 (Iter1 から一貫)。Iter2 でランキングの実行可能性 tie-break と対象コードベース無し時の Code-A 標準化を追記、Iter3 で ledger 行分割基準と「下位仮定は unverified のままでも gate に影響しない」旨を追記。[critical] が全ラウンド安定していたため、Iter4 以降に残る不明点 (外部 I/F 契約の未確定表記、ledger 優先順位列の欠如) は文言精度のロングテールと判断し規定打ち切り。

収束記録: 2026-07-17 (v0.17.0 progressive disclosure 分割)。委譲実行節の 6 bullets を references/delegated-execution.md へ verbatim 退避 (挙動変更なし)。全 7 シナリオを fresh executor で再実行し全 [critical] ○。委譲実行シナリオの全 executor が SKILL.md の太字ポインタ経由で reference へ 1 hop 到達 (tool_uses=2) し、ノイズ非採用・ledger 再開の裏付け検証・standalone 化を reference から正しく適用した。

## シナリオ: 委譲実行 — 新規開始 + PoC 専用委任 + spike 実走 (median, Opus5/Fable5 チューニング)

fresh subagent に PRD のみを渡し「ledger 未作成」の前提で Start here を実行させる。run dir には前提と矛盾する既存ファイル (別機能の `proto-ledger.md`、status に規定外 `done` を含む) を同居させる。依頼文は「台帳化と spike の検証まで」に限定し Code-A を依頼しない。fixture は「請求書 CSV 一括取込」PRD + 引用符を解釈しない共通パーサ `lib/csv_parse.js` + 正解データ `samples/expected.json` (12 レコード) で構成し、最上位候補は node 実走で必ず killed に落ちる (BOM は `trim()` の副作用で偶然通る)。別の仮定 (実機体感) は本セッションで観測不能。

### Requirements checklist

1. [critical] 出力先ディレクトリ配下に「主張 / 検証方法 / kill 条件 / status」の 4 列を持つ ledger が新規作成されている
2. [critical] 前提と矛盾する既存ファイル (`proto-ledger.md`) を対象に含めず、削除もせず、ノイズと判断した経緯を新 ledger に残している
3. [critical] 最上位仮定の spike を実際に実行し正解データと照合して verdict を確定した時点で作業を終え、Code-A に着手していない
4. [critical] 訂正者不在でも仮定ランキングを自ら確定し、返答待ちで停止せず完了している
5. 検証手段が無い仮定 (実機体感) を根拠なく grounded にせず unverified のまま扱っている
6. ledger 冒頭に glossary があり、status 列が 3 値以外を含まない
7. 最終メッセージに ledger の絶対パスと次に呼ぶべき step が書かれている

## シナリオ: 委譲実行 — 既存 ledger 再開 + 周回途中で戻しにくい決定が出現 (edge, Opus5/Fable5 チューニング)

fresh subagent に既存 ledger のパスを名指しで渡す。ledger は status 混在 (grounded 1 / unverified 2) で、grounded 行には観測値も成果物パスも無く、「現在地」が裏付け実体の無い完了状態 (Code-A 実装済み・テスト 24 件 pass) を主張している。同じ dir の `PRD-update.md` に DB migration (R5) と本番利用中の公開 API 契約変更 (R6) を要する追加要件が入っている。依頼はこの回は ledger 更新と次手の判断まで (実装・spike 実行はしない)。

### Requirements checklist

1. [critical] 既存 ledger を Read し status 列と現在地から再開すべき step を判定している (仮定抽出をやり直していない)
2. [critical] R5 / R6 を戻しにくい決定と判定し、loop を中断して design-first か「狭い spike + ADR を先に固める」へ切り替える判断を書いている
3. [critical] 裏付け実体を確認できない完了主張を根拠にせず、現在地を「あと step 6 だけ」として扱っていない
4. [critical] 最終メッセージに「更新した ledger の該当行」と「次に呼ぶべき step」の両方が書かれている
5. 既に grounded / killed が入っている行の status 値を新たな検証を経ずに書き換えていない
6. 現在地の更新時に完了状態の根拠となるファイルパスを同じ文に書き添えている (裏付けが無い場合はその旨を明記)
7. 既存の glossary ブロックを重複生成せず維持している

## シナリオ: step 6 合流分岐 + 委任文言の読み分け (hold-out, 判定タスク)

The loop 表とその直下の note 群、`iterate の実体` から、(a) step 5 完走で分析ファイルが揃った状態、(b) step 4-5 省略の ledger 駆動、(c) 周回途中で DB スキーマ変更が必要になった状態、の 3 パターンで step 6 の挙動を判定させる。あわせて委任文言 2 種 (台帳化+spike のみ / PRD 網羅実装を明示依頼) でどこまで進めるかを判定させる。ファイル作成は不要 (インライン回答)。

### Requirements checklist

1. [critical] (a) では `/finalize-plan` を通常どおり起動すると判定し、AC/MECE 欠落のまま即中断ゲートを迂回する提案をしない
2. [critical] 「step5 完走 → 分析ファイル成立 → finalize-plan 通常起動」(a) と「step4-5 省略 → ledger 追記代替」(b) の分岐を取り違えない
3. [critical] 委任文言が台帳化+spike までなら verdict 確定で終了、PRD 網羅実装の明示依頼なら Code-A まで進む、と読み分けている
4. (b) の ledger 追記には最低限ブランチ戦略と QA 手順の 2 点が入る (PR 分割はしない) と判定される
5. (c) では loop を中断し design-first (`/mece-plan-review` 等の実装前ゲート) へ切り替えると判定される
6. Code-A 着手 gate が「最上位仮定が grounded」であり、下位仮定が unverified でも gate に影響しないと読み取れている

収束記録: 2026-07-25 (Opus5/Fable5 チューニング PR)。上記 3 シナリオを Iter1-8 で fresh executor により実行 (median/edge は毎ラウンド、hold-out は Iter6・Iter8)。**全 8 ラウンド × 全シナリオで [critical] 100% ○ / accuracy 100%**。retries は Iter1 の 2 件から Iter6-8 で 0-1 件に低下、tool_uses は median 19→14 / edge 10→12 で安定。hold-out は Iter6・Iter8 とも 100% (直近平均からの低下なし → 過学習兆候なし)。**Iter9 は本セッションの subagent 上限 (200) に達し実行できず**、Iter8 後に入れた 4 点の文言修正 (行間参照に `#N` を単独で使わない / 離脱先二択の判別条件 / ADR 起票は依頼 cap に依らない・迷ったら 1 本 / ledger 駆動時の QA は `/qa-ui` の台帳なしフォールバックへ) は **fresh executor 未検証**。merge 前に median + edge を 1 ラウンド流して [critical] を確認すること。いずれも決定表・gate・出力契約を変えない加筆のみ。

### ラウンド別実測 (2026-07-25 チューニング)

metrics は Task 戻り値の usage meta。accuracy は上記凍結チェックリスト (median 7 / edge 7 / hold-out 6 項目)。

| Iter | median | edge | hold-out | その回の修正テーマ |
|---|---|---|---|---|
| 1 | 100% / 19 steps / 468s / retry 2 | 100% / 10 / 250s / 0 | — | (最適化直後のベースライン) |
| 2 | 100% / 17 / 378s / 1 | 100% / 9 / 243s / 1 | — | ledger 表スキーマの SSOT (順位を主張欄 `#N` に) |
| 3 | 100% / 29 / 597s / 1 | 100% / 10 / 318s / 1 | — | 判定は観測でのみ動く (初版 unverified・不信対象の限定・主観判定) |
| 4 | 100% / 19 / 585s / 1 | 100% / 13 / 448s / 0 | — | 再入と証拠の抜け穴 (境界 gate 化・killed 遷移・観測の置き場) |
| 5 | 100% / 16 / 468s / 1 | 100% / 13 / 375s / 1 | — | 3 回目の再発を閉じる (暫定値・未監査 grounded・型不一致) |
| 6 | 100% / 15 / 468s / 0 | 100% / 12 / 308s / 0 | **100%** / 3 / 150s | 自分が入れた矛盾の修復 + hold-out 初投入 |
| 7 | 100% / 15 / 542s / 0 | 100% / 12 / 375s / 1 | — | 修復のみ (機構追加なし) |
| 8 | 100% / 14 / 529s / 1 | 100% / 12 / 309s / 2 | **100%** / 4 / 162s | 最終修正 + hold-out 再投入 |

[critical] は全 8 ラウンドで 1 度も落ちていない (median 4×8 + edge 4×8 + hold-out 3×2 = 70 判定すべて ○)。

### 失敗パターン台帳 (この skill 専用・累積)

- **メタデータの置き場がスキーマの正本と分離する**: 順位が Gotchas にだけあり canonical 表に場所がない。Fix Rule: フォーマットにフィールドを足す指示は canonical example と同じ箇所で示す。Seen in: iter1 (median/edge 同時)
- **観測前に判定を書ける**: 文書作成が観測より前に来る工程で観測依存の欄を初版で埋められる。Fix Rule: 時系列制約は段落内の禁止文でなく**ステップ境界の受入条件**として書く (段落内では検出器にしかならない)。Seen in: iter2, iter3 → iter4 の境界 gate 化で解決
- **不信の適用先が artifact 種別で名指しされていない**: 「裏付けが無いなら unverified 扱い」が型付き status 列への降格と読める。Fix Rule: 不信の対象を種別で名指しし、型付きフィールドは新規観測なしに動かさないと併記。Seen in: iter1, iter2, iter3, iter4 → iter5 の「gate を通す根拠にしない」で決着
- **正本に無い数値を要求されて捏造する**: scalar 予算の固定を要求されるが正本に数値がない。Fix Rule: 数値要求には調達規則 (`(暫定)` + 確定者) を併記。Seen in: iter2, iter3, iter4 → iter5 で解決
- **委譲先の型が step の契約に合わない**: `/prototype` が数値照合型 spike を作れない。Fix Rule: step を外部 skill に委譲する指示は契約を親側に置き型不一致時のフォールバックも規定。Seen in: iter1, iter3 (steps 29 の主因), iter4 → iter5 で両起動モードに適用し steps 16 へ
- **自分の修正が新しい境界問題を生む**: 順位規則→剥奪遷移、証拠置き場→セル肥大、節名固定→空節の可否、killed 遷移→依頼 cap との優先順位。Fix Rule: 規則を足したら、その規則が新たに作る状態遷移と例外の出口を同じ箇所に書く。Seen in: iter3→5, iter4→5, iter6→7, iter7→8, iter8→9 (**5 連続。過剰規定スパイラルの兆候として打ち切り判断の根拠にした**)
- **振り直すラベルを唯一の識別子に使う**: `#N` が周回ごとに動くのに行間参照で使われ、参照先が黙って別行に移った (実害観測)。Fix Rule: 並べ替え可能なラベルは単独で相互参照させず内容の要約を添える。Seen in: iter8 → iter9 で修正 → **2026-07-25 の確認ラウンドで検証済み** (median は glossary に規則を写して TODO 参照に主張の要約を付け、edge は振り直し (旧 #1→#2 / 旧 #2→#3) を実行しつつ fixture に仕込んだ裸の `#2` 参照を残さなかった)

### tuning 進行状態 (2026-07-25)

- **完了**: Iter0 (description/本文整合、ギャップなし) + Iter1-8 の empirical ラウンド + **2026-07-25 の確認ラウンド (Iter8 後の 4 点の文言修正を fresh executor で検証、下記「確認ラウンド」節)**。`python3 scripts/validate_skills.py` OK。version ファイル (plugin.json / marketplace.json) は未変更 (中央で一括 bump)。
- **収束は partial**。厳格基準 (新規不明点 0 が 2 連続) は未達で、Resource cutoff で打ち切った。根拠: accuracy 8 ラウンド 100% / [critical] 70 判定すべて ○ / retries 2→0-1 / steps 安定 (median 19→14, edge 10→12) / hold-out 2 回とも 100% で過学習なし / 加筆するたびその加筆への境界質問が生まれるパターンが 5 連続。新規不明点は executor あたり毎回 3 件前後で横ばいだが、内訳が iter1-3 の矛盾・遷移欠落 (defect 級) から iter6-8 の粒度問い合わせ (成果物は毎回正しい) に変質した。
- **収束に残っていた作業 → 解消済み (2026-07-25 確認ラウンド)**: Iter8 後に入れた 4 点を fresh executor で検証すること。median + edge + hold-out を 1 ラウンド流し [critical] 全項目 ○ を確認した (下記「確認ラウンド」節)。以降この skill を変更する PR では、通常どおり保存済みシナリオの再実行のみでよい。
- **着手しなかった候補** (実害が観測されたら検討): ①委譲実行の読み替えが上書き対象 (Start here) より後ろに置かれている — 委譲系 16 executor 全てが正しく到達し実害なし、構造の並べ替えは効果を測れないため見送り ②step 3 の密度 (references への progressive disclosure 分割) — accuracy が 1 項目も落ちていないため根拠なし ③「戻しにくい決定」カテゴリの判別テスト — 例示のみだが全ラウンド正しく分類された ④非 gating な診断観測のセル内マーカー。
- **他 plugin への影響**: ledger 駆動セッションの QA 引き渡し先として `/qa-ui` の台帳なしフォールバックを SKILL.md に明記した。qa-ui 側に該当フォールバック (AC 直接読込み → 正本抽出結果 → AC 無しモード) が実在することは確認済み。qa-ui をチューニングする際にこの参照の整合を確認すること。

## 確認ラウンド (2026-07-25) — Iter8 後の 4 点を fresh executor で検証

上の「収束記録: 2026-07-25」で **fresh executor 未検証**として残した 4 点の文言修正を検証する 1 ラウンド (最適化ではなく検証のみ)。実行したのは Opus5/Fable5 チューニングの 3 シナリオ (median / edge / hold-out)。fixture は各シナリオの spec から新規構築し executor ごとに独立ディレクトリへ配置、凍結チェックリストを invocation contract どおり executor prompt に同梱。**採点は self-report ではなく成果物実物** (ledger / spike ログ / ADR / grep による機械確認) から行った。

| シナリオ | accuracy | [critical] | tool_uses | duration | retries |
|---|---|---|---|---|---|
| median (新規開始 + PoC 専用委任 + spike 実走) | **100%** (7/7) | 4/4 ○ | 12 | 495s | 2 |
| edge (既存 ledger 再開 + 戻しにくい決定の出現) | **100%** (7/7) | 4/4 ○ | 12 | 352s | 2 |
| hold-out (step 6 合流分岐 + 委任文言の読み分け) | **100%** (6/6) | 3/3 ○ | 2 | 153s | 0 |

**4 点の検証結果 (すべて hold)**:

1. **行間参照に `#N` を単独で使わない** (実害修正) — median は glossary にこの規則を写し、`## TODO` の行参照を「`#5` 体感 = 経理担当 2 名への実機ヒアリング」形式 (番号 + 主張の要約) で書いた。edge は最も強い検証になった: fixture の `## 現在地` に「残るは #2 の検証」という裸の参照を仕込んでおき、executor は追加要件で行を振り直した (旧 `#1` 縮小 p95 → `#2`、旧 `#2` 体感 → `#3`) にもかかわらず、更新後 ledger にこの裸参照は残っておらず (grep 0 件)、振り直しの事実を主張の要約つきで明記し TODO の 4 参照すべてに要約を添えた。**黙って別行を指す再発は起きない**。
2. **離脱先二択の判別条件** — edge が実適用: R5 (バックフィル) は決め手が本番非接触の複製環境で取れるとして「狭い spike + ADR」、R6 (公開 API 契約) は決め手がパートナー 3 社の合意だとして design-first、と条件どおり切り分けた。hold-out も (c) で同じ判別条件を再現。
3. **ADR 起票は依頼 cap に依らない / 迷ったら 1 本** — edge の依頼は「ledger 更新と次手の判断まで (実装・spike 実行はしない)」と cap されていたが、executor は ADR 2 本 (`Status: Proposed`、観測は ledger 該当行に委譲) を起票した。1 本 vs 2 本の判断も規則に沿って明示的に行っている (ロールバック単位と決定者が別 = 迷いではない、と理由を述べた)。hold-out も cap 非依存を明言。
4. **ledger 駆動時の QA は `/qa-ui` の台帳なしフォールバックへ** — hold-out が (b) で「QA 実行は QA-ID 台帳が無いので `/qa-ui` の台帳なしフォールバックに渡す」と判定し、同時に (a) では「台帳ありなので QA-ID 台帳を渡す (台帳なしフォールバックは使わない)」と**過剰一般化せず**書き分けた。median / edge は step 6 に到達しないため、この点はこの hold-out でのみ観測できる。

skill 本文・reference の修正は **なし**。新規不明点は median 4 / edge 3 / hold-out 3 件で横ばいだが、内訳はいずれも粒度問い合わせ (中間状態の証跡の残し方、同居 spike で計測対象が killed になった場合の補助指標の扱い、順位規則と執行可否の合成順序、ノイズ判断の記載先の節名) で、成果物自体は全項目正しい。上の「加筆するたびその加筆への境界質問が生まれる」5 連続パターンに合致するため、規定打ち切りの判断を維持した。厳格収束基準 (新規不明点 0 が 2 連続) は**依然未達**であり、収束状態は partial のまま — ただし Iter8 後の未検証差分は解消したので、merge 前提としては完了扱いでよい。

収束記録: 2026-07-18 (regression 再検証、skill 変更なし)。全 7 シナリオ (静的チェック / finalize-plan 合流分岐 / 委譲新規開始 median / 既存 ledger 再開 edge / 再開+ノイズ hold-out / PoC median / 実装 edge) を fresh executor で並列再実行し、全 [critical] ○ / accuracy 100%。委譲系 executor は SKILL.md の太字ポインタ経由で references/delegated-execution.md へ到達し、ノイズ非採用 (scenario3 の payment-retry proto-ledger と scenario5 の既定名一致 assumption-ledger.md をいずれも正本判断から除外)・既存 status の無検証書き換え回避・裏付け実体なき Code-A 完了主張の unverified 格下げ・standalone Code-A の組み込み点コメント化を規定どおり適用した。PoC median は Node spike を実走し top 仮定を grounded 確定した時点で Code-A に着手せず終了、実装 edge は添付 grounded を無検証で受理し 30 tests pass の Code-A まで到達。新規に出た不明点 2 件 (scenario4「Code-A 完了主張の対応仮定が prose であいまい」、PoC median「5MB が MiB か MB か」) はいずれもフィクスチャ設計 (未裏付け完了を prose に混在・PRD が単位未指定) 起因で、前者の fix は delegated-execution.md の「完了状態には根拠ファイルパスを同じ文に併記」で既にカバー済み、後者は Start here step 3 の「scalar 予算を固定し観測で確定」に沿って executor が境界を固定して処理済み。いずれも skill 欠陥ではないため本文・reference の修正なし。
