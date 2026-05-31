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
- 機能が複数のプラン文書 + PR チェーンに跨る規模
- 実装の大半を AI エージェントに任せる

使わない場合: 未検証の仮定が無い既知機能(`/define-acceptance-criteria` → 実装に直行) / 1 つの問いに答える単発 throwaway(`/prototype` を直接)。

**ガードレール(最重要・誤適用防止)**: code-first が正しいのは、危険な未知が **feasibility / UX / 流用可否** で、**かつ blast radius が小さく Code-A を捨てやすい**とき(例: view 層・BE 凍結)。危険な未知が**戻しにくい決定**(DB スキーマ / migration / 公開 API 契約 / チーム間境界)なら code-first は**不可** — 「まず 100% 動かす」と間違った土台を Code-A に焼き込み、リファクタで剥がせない。その場合は **design-first か「狭い spike + ADR を先に固める」**に切り替える。ここでの spike は **本番非接触の throwaway**(本番リソース/migration/データ・公開エンドポイントを作らない)に限り、結論は ADR に固める(Code-A にしない)。reversible な部分(UI 等)を code-first で切り出すのは、それが依存する irreversible 決定の ADR が固まった後。

## Start here

起動直後の第一手(`The loop` step 1 は「最も危険な仮定」を知っている前提なので、その前に必ず):

1. **対象を特定** — PRD/仕様/プランを探す。取れなければ 1 度だけ聞く(**branch 名から決めつけない**)。`When to use` で使用可否を判定し、不適なら `/prototype` か `/define-acceptance-criteria` へ誘導して抜ける。
2. **仮定を自分で抽出してランク** — load-bearing な未検証仮定を**自分で**列挙し、**不確実性 × 外れた時の手戻り**で順位付け(ユーザーに丸投げせず、順位案を出して訂正してもらう)。
3. **単一正本(ledger)を作る = 最初の成果物** — `主張 / 検証方法 / kill 条件 / status` の表で 1 ファイル。**検証方法と kill 条件は実行可能に書く**: ①何を正本(source-of-truth)として数値照合するか名指す ②scalar な予算(レイテンシ/精度等)は percentile + 計測窓に固定(例: p95 ≤ 1s)③代表入力を列挙(正常/エッジ)④境界は推測せず観測で確定(put→get・実測)。以後の TODO・決定・AC はすべてここに集約する。
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
| 6 | レビュー + デリバリー可能に仕上げる(PR 分割/QA・対外語彙浄化・最終 SSOT) | `/finalize-plan` + `/purge-private-vocab` + `/dry-ssot-text` | Doc-3 + 依存順 PR チェーン |

> step 4→6 は同じ「コード→設計書」でも fidelity が違う: 4 = 素材、5 = 設計の堅牢化(内部品質)、6 = レビュー/デリバリー化(対外品質)。
> スキル表記: `→` は順序固定(前段の出力が次段の入力)、`+` は順不同/併用。
> Code-A′ は **delivery 本体**(単一実装・組み直さない)。step 6 はそれを依存順 PR に**切り出す**だけ。Code-A を捨てて clean に組み直す重い variant は、blast radius が大きい時だけの選択肢。
> step 5 の `/define-acceptance-criteria`・`/mece-plan-review` は本来「実装前 gate」だが、ここでは目的が変わり **post-code で仕様の正本化 + カバレッジ漏れ検出**に使う。

## 効かせる規律

**1. 設計書はコードから起こす(初期 drift を消す)。** 設計を先に書かない。動く working code を正本にし、doc は最後に code から導出する。これで机上設計とコードの**初期ギャップ**は構造的に消える。ただし「ドリフトしない」のは導出時点だけ — コードが以後も変われば doc は再 drift するので、**doc を再導出するか code を正本(code-as-SSOT)と割り切る**こと。

**2. 100% 動かしてから設計する。** features を 100% 通してから構造を整える(設計 = リファクタ)。机上設計で AI に間違った骨格を作らせない。step 2(まず動かす)と step 3(次に整える)を混ぜない。

**3. 単一正本(ledger)。** 仮定・TODO・決定・AC を 1 ファイルに集約する。複数 doc に散らさない。

**4. 磨く(内部)と仕上げる(対外)を分ける。** step 5 = 設計の堅牢化(grill/AC/MECE/SSOT)、step 6 = レビュー/デリバリー化(PR 分割/語彙浄化)。混ぜると「対外向けに整える」圧力で設計の堅牢化が甘くなる。

**5. 効く決定は ADR(Why + 却下案)。** 後で蒸し返される決定は ADR に結晶化する(step 5 の `/grill-with-docs` が ADR を更新)。

## Common mistakes

- **机上設計から始める。** 紙の設計 → コードの順は、このスキルが**禁じる**既定挙動。spike → 動くコード → リファクタ → doc の順を守る。
- **設計書をコードより先に書く。** doc が先だと必ず乖離する。doc は step 4 以降、working code から起こす。
- **緑チェックを product-green と取り違える。** 動くコードは実装可能性を示すだけ。ユーザーの完了率向上は示さない。UX 仮説は post-ship で計測する。

## 併用推奨 skill

- `/prototype` — step 1 の throwaway スパイク
- `/review-design` — step 3 のリファクタ/配置判断
- `/grill-with-docs` `/define-acceptance-criteria` `/mece-plan-review` `/dry-ssot-text` — step 5 の設計書磨き
- `/finalize-plan` `/purge-private-vocab` `/dry-ssot-text` — step 6 のレビュー/デリバリー仕上げ
