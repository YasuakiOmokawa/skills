---
name: iterate-with-prototypes
description: Use when starting a complex feature where a PRD or spec exists but load-bearing assumptions (technical feasibility, UX effect, reuse of an existing API or data structure) are still unverified, most implementation is done by an AI agent, the work spans several design docs and a PR chain, AND the change is reversible with a small blast radius. Do NOT use when the core risk is a hard-to-reverse decision (DB schema / migration, public API contract, cross-team boundary) — use design-first there. Symptom — about to design a complex feature on paper before any of it is proven to run, or confident-but-wrong design propagating across documents.
---

# Iterate With Prototypes

## Overview

不確実な機能で危ないのは、**机上の設計から始める**こと。AI は紙の上で自信満々に間違った骨格を作り、設計書はやがて実コードから乖離する。このスキルは順序を反転する: **動くコードで設計を発見し、設計書はコードから最後に起こす**。設計書を working code から導出するので、**机上設計とコードの初期ギャップを構造的に消す**(導出時点で一致)。継続的な drift には doc の再導出 or code-as-SSOT 運用が要る。

有能なエージェントは spike や throwaway、独立 QA は放っておいてもやる。このスキルが効かせるのは「**コードを先に 100% 動かし、設計は後でリファクタ、設計書は最後にコードから**」という反転と、その規律。

## When to use

- PRD/仕様はあるが、実現可能性 / UX効果 /「既存API・データ構造を流用できる」が未検証
- 機能が複数のプラン文書に跨る規模
- 実装の大半を AI エージェントに任せる

使わない場合: 未検証の仮定が無い既知機能(`/define-acceptance-criteria` → 実装に直行) / 1 つの問いに答える単発 throwaway(`/prototype` を直接)。

**ガードレール(最重要・誤適用防止)**: code-first が正しいのは、危険な未知が **feasibility / UX / 流用可否** で、**かつ blast radius が小さく Code-A を捨てやすい**とき(例: view 層・BE 凍結)。危険な未知が**戻しにくい決定**(DB スキーマ / migration / 公開 API 契約 / チーム間境界)なら code-first は**不可** — 「まず 100% 動かす」と間違った土台を Code-A に焼き込み、リファクタで剥がせない。その場合は **design-first か「狭い spike + ADR を先に固める」**に切り替える。ここでの spike は **本番非接触の throwaway**(本番リソース/migration/データ・公開エンドポイントを作らない)に限り、結論は ADR に固める(Code-A にしない)。reversible な部分(UI 等)を code-first で切り出すのは、それが依存する irreversible 決定の ADR が固まった後。

## Start here

起動直後の第一手(`The loop` step 1 は「最も危険な仮定」を知っている前提なので、その前に必ず):

1. **対象を特定** — PRD/仕様/プランを探す。取れなければ 1 度だけ聞く(**branch 名から決めつけない**)。`When to use` で使用可否を判定し、不適なら `/prototype` か `/define-acceptance-criteria` へ誘導して抜ける。
2. **仮定を自分で抽出してランク** — load-bearing な未検証仮定を**自分で**列挙し、**不確実性 × 外れた時の手戻り**で順位付け(ユーザーに丸投げせず、順位案を出して訂正してもらう)。
3. **単一正本(ledger)を作る = 最初の成果物** — `主張 / 検証方法 / kill 条件 / status` の表で 1 ファイル。**検証方法と kill 条件は実行可能に書く**: ①何を ground-truth(source-of-truth)として数値照合するか名指す ②scalar な予算(レイテンシ/精度等)は percentile + 計測窓に固定(例: p95 ≤ 1s)③代表入力を列挙(正常/エッジ)④境界は推測せず観測で確定(put→get・実測)。以後の TODO・決定・AC はすべてここに集約する。方法論用語 (ledger / spike / kill 条件 / grounded 等) を使う ledger は、**冒頭に用語定義 (glossary) 1 ブロックを最初から置く** — 後から読む人・別エージェントが decode できない造語を書いた時点で防ぐ (事後に数十箇所を除染するより安い。規律 3 の「書いた時点で漏らさない」と同根)。

   例(1 行):

   | 主張 | 検証方法 | kill 条件 | status |
   |---|---|---|---|
   | 既存 SearchIndex API を流用して全文検索を賄える | 本番 SearchIndex に代表クエリ 20 件(正常 15 / エッジ 5)を投げ、返却 ID 集合を本番 DB の期待集合(=ground-truth)と照合。レイテンシは p95 計測 | recall < 0.9 もしくは p95 > 1s が再現 | unverified |

   この行は **1 仮定に複数観測基準(recall と latency)**を持つ例(同一データ経路なので 1 行に同居)。**別仮定は行を分ける**(`The loop` step 1 の「verdict を仮定ごとに分ける」と整合)。

   status は **unverified / grounded / killed** の 3 値(本文の「接地」= grounded、表の「kill 条件」成立 = killed。この 3 トークン以外を status 列に書かない)。**grounded の立証責任は証拠側にある** — ground-truth 照合が取れない・観測が kill / grounded どちらの条件にも届かない場合は grounded にせず unverified のまま step 1 へ戻る(判定をでっち上げない。楽観 grounded は「最上位仮定が grounded になってから Code-A 着手」の gate をすり抜けさせる)。
4. 最上位仮定の spike へ → `The loop` step 1。

> **iterate の実体**: spike は 1 回で終わらないことが多い。spike を配信して触らせる → ledger の仮定/status を更新 → 未解決なら step 1 へ戻る、という**周回**を回す。`The loop` step 2(Code-A)着手は、最上位仮定が grounded になってから。

## The loop (code-first・全 6 ステップ)

| # | やること | スキル | 成果物 |
|---|---|---|---|
| 1 | 最リスキー箇所を使い捨て検証(構成/テスト不問・**本番正本と数値照合**)。同一データ経路で連鎖する高手戻り仮定は 1 spike に同居させ verdict を仮定ごとに分ける(経路が独立なら別 spike) | `/prototype` | 接地 verdict(ledger 更新) |
| 2 | PRD 100% 網羅の動くコード(ファイル分割 + テスト) | (code gen / TDD) | **Code-A**(動く・設計は粗くてよい) |
| 3 | 設計 = delivery 品質までリファクタ(機能固定・構造を整える) | `/review-design` | Code-A′(動く・delivery 品質) |
| 4 | コードから設計書を逆生成(磨く前の素材) | — | Doc-1 |
| 5 | 設計書を磨く(ドメイン/用語で叩く → AC → MECE → SSOT) | `/grill-with-docs` → `/define-acceptance-criteria` → `/mece-plan-review` → `/dry-ssot-text` | Doc-2(AC + ADR 込み) |
| 6 | レビュー + デリバリー可能に仕上げる(QA 手順・対外語彙浄化・最終 SSOT) | `/finalize-plan` + `/dry-ssot-text` + `/purge-private-vocab` | Doc-3 + QA 台帳 (PR 梱包は出荷時に `/create-pr` で判断) |

> step 4→6 は同じ「コード→設計書」でも fidelity が違う: 4 = 素材、5 = 設計の堅牢化(内部品質)、6 = レビュー/デリバリー化(対外品質)。
> スキル表記: `→` は順序固定(前段の出力が次段の入力)、`+` は順不同/併用。
> Code-A′ は **delivery 本体**(単一実装・組み直さない)。step 6 はそれを依存順 PR に**切り出す**だけ。Code-A を捨てて clean に組み直す重い variant は、blast radius が大きい時だけの選択肢。
> step 2(まず動かす)と step 3(次に整える)を**混ぜない** — 機能を 100% 通してから構造を整える(机上設計で間違った骨格を作らせない)。
> step 5 の `/define-acceptance-criteria`・`/mece-plan-review` は本来「実装前 gate」だが、ここでは目的が変わり **post-code で仕様の正本化 + カバレッジ漏れ検出**に使う。
> step 5 を Doc-1 (プランファイル) に対して実行すると、両 skill は自らの契約どおり `<plan>.analysis.md` に `## 受け入れ条件` `## MECE分析結果` を書き出す。これは finalize-plan Step 1.5 の入力要件そのものなので、この場合 step 6 は ledger 追記に頼らず **`/finalize-plan` を通常どおり起動する** — QA-ID 台帳・正本カバレッジゲート・PR 割当ゲートは design-first 経由と同一に機能する (finalize-plan の即中断ゲートは弱めず、入力側を要件に合わせて整える方式を採る)。
> step 4-5 (doc 逆生成 + AC/MECE) 自体を省略した **ledger 駆動セッション**では分析ファイルが無いため step 6 の `/finalize-plan` は起動できない。この場合のみ ledger への追記で代替し、最低限 **ブランチ戦略と QA 手順の 2 点**を書く (/finalize-plan の主要出力と同じ。PR 分割は行わない — 梱包は出荷時に /create-pr で判断)。
> 周回の途中で「戻しにくい決定」が必要になった (可逆・小 blast radius の前提が崩れた) 場合は、loop を中断し `When to use` のガードレールに従って design-first (`/mece-plan-review` 等の実装前ゲート) に切り替える。

## 効かせる規律

> drift / ledger / 100%-then-design の正本は他所に 1 つずつある(順に Overview・Start here step 3・The loop)。ここはそれらの再掲ではなく、loop 表に組み込めなかった掟だけを置く。

**1. 磨く(内部)と仕上げる(対外)を分ける。** step 5 = 設計の堅牢化(grill/AC/MECE/SSOT)、step 6 = レビュー/デリバリー化(QA 手順/語彙浄化)。混ぜると「対外向けに整える」圧力で設計の堅牢化が甘くなる。

**2. 効く決定は ADR(Why + 却下案)。** 後で蒸し返される決定は ADR に結晶化する(step 5 の `/grill-with-docs` が ADR を更新)。

**3. ledger は観測と status の唯一の SSOT に保つ。** 決定と Why は ADR 側に置き、ADR は観測値を ledger に委ねる(同じ事実を両方に書かない)。ledger に free-form の「決定ログ」を溜めると、step 4-6 で逆生成する doc/ADR と重複し、後追いの集約が要る。spike-N / 案ラベルは ledger 内部限定で、コードコメントや対外 doc に持ち出すなら ADR#/PR# など grep 可能な参照に置換する(step 5/6 で `/purge-private-vocab` を待たず、書いた時点で漏らさない。番号ラベル規則と同根)。

## Common mistakes

- **設計/doc をコードより先に書く。** 紙の設計 → コードの順はこのスキルが**禁じる**反転違反で、doc が先だと必ず乖離する。spike → 動くコード → リファクタ → doc(step 4 以降は working code から起こす)の順を守る。
- **緑チェックを product-green と取り違える。** 動くコードは実装可能性を示すだけ。ユーザーの完了率向上は示さない。UX 仮説は post-ship で計測する。
- **variant 同士の相対比較で合否(kill/grounded)を決める。** A vs B は、どちらも**機能の目的(その機能が生む価値)を定義する ground-truth** で測っていなければ「差が無い → 無価値」と誤断する(両方ゴールを外していても気づけない)。relative 比較は候補の絞り込みにのみ使い、合否はこの ground-truth(網羅性が価値なら既知完全集合 = oracle を構築)に対する**絶対値**(recall/precision 等)で出す。

## 実例 (worked example)

- [references/worked-example-spike-to-rebuild.md](references/worked-example-spike-to-rebuild.md) — 実現性不明 → 捨て spike (既定 OFF で本番非接触) → 規約準拠で**作り直し** → 決定を ADR に保全、の 1 周を匿名化した実例。step 2 を Code-A′ のリファクタでなく作り直しで起こした変種で、「捨てるのはコード・残すのは決定」「技術実現性は ADR / UX 仮説は DD」の分離を具体で示す。

## 併用推奨 skill

> **install 前提**: `/prototype` (superpowers) と `/grill-with-docs` は本 repo の plugin ではなく別途 install が必要。未 install の場合 step 1 (spike) / step 5 (ドメインレビュー) が起動できないため、先に導入するか、手動の throwaway spike / ドメイン用語レビューで代替する。本 repo 内の plugin は `/review-design` `/define-acceptance-criteria` `/mece-plan-review` `/dry-ssot-text` `/finalize-plan` `/purge-private-vocab`。

- `/prototype` — step 1 の throwaway スパイク
- `/review-design` — step 3 のリファクタ/配置判断
- `/grill-with-docs` `/define-acceptance-criteria` `/mece-plan-review` `/dry-ssot-text` — step 5 の設計書磨き
- `/finalize-plan` `/dry-ssot-text` `/purge-private-vocab` — step 6 のレビュー/デリバリー仕上げ
