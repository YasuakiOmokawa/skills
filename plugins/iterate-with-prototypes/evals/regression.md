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

収束記録: 2026-07-18 (regression 再検証、skill 変更なし)。全 7 シナリオ (静的チェック / finalize-plan 合流分岐 / 委譲新規開始 median / 既存 ledger 再開 edge / 再開+ノイズ hold-out / PoC median / 実装 edge) を fresh executor で並列再実行し、全 [critical] ○ / accuracy 100%。委譲系 executor は SKILL.md の太字ポインタ経由で references/delegated-execution.md へ到達し、ノイズ非採用 (scenario3 の payment-retry proto-ledger と scenario5 の既定名一致 assumption-ledger.md をいずれも正本判断から除外)・既存 status の無検証書き換え回避・裏付け実体なき Code-A 完了主張の unverified 格下げ・standalone Code-A の組み込み点コメント化を規定どおり適用した。PoC median は Node spike を実走し top 仮定を grounded 確定した時点で Code-A に着手せず終了、実装 edge は添付 grounded を無検証で受理し 30 tests pass の Code-A まで到達。新規に出た不明点 2 件 (scenario4「Code-A 完了主張の対応仮定が prose であいまい」、PoC median「5MB が MiB か MB か」) はいずれもフィクスチャ設計 (未裏付け完了を prose に混在・PRD が単位未指定) 起因で、前者の fix は delegated-execution.md の「完了状態には根拠ファイルパスを同じ文に併記」で既にカバー済み、後者は Start here step 3 の「scalar 予算を固定し観測で確定」に沿って executor が境界を固定して処理済み。いずれも skill 欠陥ではないため本文・reference の修正なし。
