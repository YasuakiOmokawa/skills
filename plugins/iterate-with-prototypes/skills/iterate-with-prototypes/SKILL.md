---
name: iterate-with-prototypes
description: Use when starting a complex feature where a PRD or spec exists but load-bearing assumptions (technical feasibility, UX effect, reuse of an existing API or data structure) are still unverified, most implementation is done by an AI agent, the work spans several design docs and a PR chain (potentially across multiple sessions or delegated subagent runs that resume from the assumption ledger), AND the change is reversible with a small blast radius. Do NOT use when the core risk is a hard-to-reverse decision (DB schema / migration, public API contract, cross-team boundary) — use design-first there. Symptom — about to design a complex feature on paper before any of it is proven to run, or confident-but-wrong design propagating across documents.
---

# Iterate With Prototypes

## Overview

不確実な機能で危ないのは、**机上の設計から始める**こと。AI は紙の上で自信満々に間違った骨格を作り、設計書はやがて実コードから乖離する。このスキルは順序を反転する: **コードを先に 100% 動かし、設計は後でリファクタ、設計書は最後にコードから起こす**。doc を working code から導出するので机上設計とコードの初期ギャップは導出時点で消えるが、継続的な drift には doc の再導出 or code-as-SSOT 運用が要る。

spike や throwaway、独立 QA 自体は有能なエージェントが放っておいてもやる。このスキルの効き目は、この反転の順序とそれを崩さない規律にある。

## When to use

- PRD/仕様はあるが、実現可能性 / UX効果 /「既存API・データ構造を流用できる」が未検証
- 機能が複数のプラン文書に跨る規模
- 実装の大半を AI エージェントに任せる

使わない場合: 未検証の仮定が無い既知機能(`/define-acceptance-criteria` → 実装に直行) / 1 つの問いに答える単発 throwaway(`/prototype` を直接)。

**ガードレール(誤適用防止)**: code-first が正しいのは、危険な未知が **feasibility / UX / 流用可否** で、**かつ blast radius が小さく Code-A を捨てやすい**とき(例: view 層・BE 凍結)。危険な未知が**戻しにくい決定**(DB スキーマ / migration / 公開 API 契約 / チーム間境界)なら code-first は**不可** — 「まず 100% 動かす」と間違った土台を Code-A に焼き込み、リファクタで剥がせない。その場合は **design-first か「狭い spike + ADR を先に固める」**に切り替える(決め手の観測が本番非接触の spike で取れるなら後者、決定が組織合意や他チームの回答に依るなら前者)。ここでの spike は **本番非接触の throwaway**(本番リソース/migration/データ・公開エンドポイントを作らない)に限り、結論は ADR に固める(Code-A にしない)。ADR がまだ 1 本も無い周回では、**戻しにくい決定が必要と判明した時点で(周回のどの位置でも)**案件ディレクトリに `ADR-0001-<主題>.md` を自分で起こす(戻しにくい決定 1 件につき 1 本 — 別々にロールバックしうる決定なら別 ADR、迷ったら 1 本にまとめる。step 5 の `/grill-with-docs` を待たない)。起票は呼び出し側の依頼範囲の cap に関係なく行う — 決定を失わないため。決め手となる観測がまだ無い段階なら `Status: Proposed` として、決定に必要な観測を ledger の該当行へのポインタで書く。reversible な部分(UI 等)を code-first で切り出すのは、それが依存する irreversible 決定の ADR が固まった後。

## Start here

起動直後の第一手(`The loop` step 1 は「最も危険な仮定」を知っている前提なので、その前に):

1. **対象を特定** — PRD/仕様/プランを探す。取れなければ 1 度だけ聞く(**branch 名から決めつけない**)。`When to use` で使用可否を判定し、不適なら `/prototype` か `/define-acceptance-criteria` へ誘導して抜ける。
2. **仮定を自分で抽出してランク** — load-bearing な未検証仮定を**自分で**列挙し、**不確実性 × 外れた時の手戻り**で順位付け(ユーザーに丸投げせず、順位案を出して訂正してもらう)。このセッションでは検証手段が無い仮定(実機・外部環境でしか観測できない等)が混じる場合、その執行可否も順位判断の入力に含める(`#N` は spike の着手順なので、実行不能な仮定を最上位に置くと進められない)。執行不能なため下位に回した高手戻り仮定は、人間側で解く宿題として現在地に残す — 順位を下げたまま忘れない。「検証手段が無い」と判定する前に、実行可能な範囲を 1 回試す(対象ツール・環境の有無を確認する等) — 試さずに推測で不能と決めない。人間・第三者の回答しか観測手段が無い仮定は、誰に何を聞く必要があるかを書けば「試した」と見なす(問い合わせ自体は宿題に回す)。
3. **単一正本(ledger)を作る = 最初の成果物** — `主張 / 検証方法 / kill 条件 / status` の表で 1 ファイル。**検証方法と kill 条件は実行可能に書く**: ①何を ground-truth(source-of-truth)として数値照合するか名指す ②scalar な予算(レイテンシ/精度等)は percentile + 計測窓に固定(例: p95 ≤ 1s)。正本に数値が無ければ自分で暫定値を置き、`(暫定)` と誰が確定するかを併記する(空欄にせず、確定値に見せかけもしない)③代表入力を列挙(正常/エッジ)④境界は推測せず観測で確定(put→get・実測)⑤判定が人間の主観に依る仮定(体感・納得感)は数値を kill 条件の主節にしない — 誰にどう見せて何と答えたら kill かを書く(数値を併記するなら表の別の行に補助指標として立てる。gate を支配するのは主観の行 — 補助指標が予算内でも主観の行が kill なら killed)。以後の TODO・AC・観測はここに集約する(効く決定と Why は ADR 側 — 「効かせる規律」3)。方法論用語 (ledger / spike / kill 条件 / grounded 等) を使うなら、**冒頭に用語定義 (glossary) を 1 ブロック置く** — 後から読む人・別エージェントが decode できない造語を残さないため。

   例(1 行):

   | 主張 | 検証方法 | kill 条件 | status |
   |---|---|---|---|
   | #1 既存 SearchIndex API を流用して全文検索を賄える | 本番 SearchIndex に代表クエリ 20 件(正常 15 / エッジ 5)を投げ、返却 ID 集合を本番 DB の期待集合(=ground-truth)と照合。レイテンシは p95 計測 | recall < 0.9 もしくは p95 > 1s が再現 | unverified |

   列はこの 4 列で固定し、step 2 の順位は**主張欄の先頭に `#N`** で書く(順位列を足さない)。`#N` は unverified の行にだけ存在する — grounded / killed に決着した行からは外す。再開する読み手が行の並び順から最上位仮定を推測しなくて済むようにするため(表の物理順は問わない)。番号は周回ごとに振り直すので、**行から行を参照するときは `#N` だけで指さず主張の要約を添える** — 振り直しで参照先が黙って別の行に移る。

   **行の粒度**: 1 行 = 1 つの判定対象(同じ処理経路・同じ kill 条件)。同一経路の複数の代表入力(境界値・エッジ)や、1 回通せば同時に測れる複数の観測基準(上の例の recall と latency)は行を分けず検証方法欄に列挙する。判定対象の処理経路や観測次元が別で kill 条件も別なら行を分ける。**複合主張は最初から狭く切る** — 例「HEIC も安定処理」(= 拡張子受理 + EXIF 補正 + 内容抽出精度)は次元の一部だけが kill 条件に触れうるので、全体 recall だけ見て grounded にすると触れた次元が握りつぶされる。次元ごとに行を分け、grounded 側と unverified 側を別行にする。

   観測値と spike 成果物のパスは**検証方法欄の末尾に追記する**(列を足さない)。grounded / killed の根拠を後から監査できるようにするため。セルに収まらない長さになったら表の下の `## 観測` 節、保留中の作業は `## TODO` 節に置き、セルからは 1 行で参照する(この 2 節は溢れたときだけ作る)。表の下には `## 現在地` 節も置く — いまどの step にいるか・何が裏付け済みかを、次に再開する読み手が読む場所。節名を実行者ごとに発明すると探せなくなる。証拠が書かれていない grounded(他者が残した行など)は **Code-A 着手 gate を通す根拠にしない** — status は勝手に書き換えず、未監査であることを `## 現在地` に注記して再観測を次の spike に積む。

   status は **unverified / grounded / killed** の 3 値のみ(本文の「接地」= grounded、表の「kill 条件」成立 = killed。この 3 トークン以外を status 列に書かない)。**grounded の立証責任は証拠側にある** — ground-truth 照合が取れない、または観測が kill / grounded どちらの条件にも届かない場合は grounded にせず unverified のまま step 1 へ戻る(楽観 grounded は「最上位仮定が grounded になってから Code-A 着手」の gate をすり抜けさせる)。
4. 最上位仮定の spike へ → `The loop` step 1。**step 3 を出た時点の ledger は全行 unverified・観測欄は空**(verdict と観測値は spike の実測を待って書く。予測で先に埋めると、実測と食い違っても最初の判定が残る)。

> **iterate の実体**: spike は 1 回で終わらないことが多い。spike を配信して触らせる → ledger の仮定/status を更新 → 未解決なら step 1 へ戻る、という**周回**を回す。step 2(Code-A)に進むのは、最上位仮定が grounded になり(下位の仮定が unverified のままでもこの gate には影響しない)**かつ呼び出し側が PRD 網羅実装を明示的に依頼している**とき。依頼が「ledger 化と spike の検証」までなら(PoC・使い捨て検証など速度優先の文脈で典型)、最上位仮定が grounded/killed で確定した時点でこの回の作業を終える。
> **最上位仮定が killed になった場合**: その仮定に乗っていた方針は捨て、代替経路を新しい仮定として立て直す(順位付けのみ step 2 をやり直す)。残る経路がすべて戻しにくい決定に触れるなら、`When to use` のガードレールに従って design-first へ抜ける。立て直した後にもう 1 周するかは**呼び出し側の依頼範囲が先に効く** — 依頼が「spike の検証まで」なら、立て直した仮定と順位を ledger に書いてこの回を終える。

## The loop (code-first・全 6 ステップ)

| # | やること | スキル | 成果物 |
|---|---|---|---|
| 1 | 最リスキー箇所を使い捨て検証(構成/テスト不問・**本番正本と数値照合**)。同一データ経路で連鎖する高手戻り仮定は 1 spike に同居させ verdict を仮定ごとに分ける(経路が独立なら別 spike) | `/prototype` | 接地 verdict(ledger 更新) |
| 2 | PRD 100% 網羅の動くコード(ファイル分割 + テスト) | (code gen / TDD) | **Code-A**(動く・設計は粗くてよい) |
| 3 | 設計 = delivery 品質までリファクタ(機能固定・構造を整える) | `/review-design` | Code-A′(動く・delivery 品質) |
| 4 | コードから設計書を逆生成(磨く前の素材) | — | Doc-1(step 5 に通すならプランファイルとして起こす) |
| 5 | 設計書を磨く(ドメイン/用語で叩く → AC → MECE → SSOT) | `/grill-with-docs` → `/define-acceptance-criteria` → `/mece-plan-review` → `/dry-ssot-text` | Doc-2(AC + ADR 込み) |
| 6 | レビュー + デリバリー可能に仕上げる(QA 手順・対外語彙浄化・最終 SSOT) | `/finalize-plan` + `/dry-ssot-text` + `/purge-private-vocab` | Doc-3 + QA 台帳 (PR 梱包は出荷時に `/create-pr` で判断) |

> step 4→6 は同じ「コード→設計書」でも fidelity が違う: 4 = 素材、5 = 設計の堅牢化(内部品質)、6 = レビュー/デリバリー化(対外品質)。
> スキル表記: `→` は順序固定(前段の出力が次段の入力)、`+` は順不同/併用。
> Code-A′ は **delivery 本体**(単一実装・組み直さない)。step 6 はそれを依存順 PR に**切り出す**だけ。Code-A を捨てて clean に組み直す重い variant は、blast radius が大きい時だけの選択肢。
> step 2(まず動かす)と step 3(次に整える)を**混ぜない** — 機能を 100% 通してから構造を整える。
> step 5 の `/define-acceptance-criteria`・`/mece-plan-review` は本来「実装前 gate」だが、ここでは目的が変わり **post-code で仕様の正本化 + カバレッジ漏れ検出**に使う。
> step 5 を Doc-1 (プランファイル) に対して実行すると、両 skill は自らの契約どおり `<plan>.analysis.md` に `## 受け入れ条件` `## MECE分析結果` を書き出す。これは finalize-plan Step 1.5 の入力要件そのものなので、この場合 step 6 は ledger 追記に頼らず **`/finalize-plan` を通常どおり起動する** — QA-ID 台帳・正本カバレッジゲート・PR 割当ゲートは design-first 経由と同一に機能する (finalize-plan の即中断ゲートは弱めず、入力側を要件に合わせて整える方式を採る)。
> step 4-5 (doc 逆生成 + AC/MECE) 自体を省略した **ledger 駆動セッション**では分析ファイルが無いため step 6 の `/finalize-plan` は起動できない。この場合のみ ledger への追記で代替し、最低限 **ブランチ戦略と QA 手順の 2 点**を書く (/finalize-plan の主要出力と同じ。PR 分割は行わない — 梱包は出荷時に /create-pr で判断)。step 6 の残り 2 skill は磨く対象の doc が無いので走らせない (ledger 内の語彙は「効かせる規律」3 で担保する)。QA の実行は QA-ID 台帳が無いので `/qa-ui` の台帳なしフォールバックに渡す。
> 周回の途中で「戻しにくい決定」が必要になった (可逆・小 blast radius の前提が崩れた) 場合は、loop を中断し `When to use` のガードレールに従って design-first (`/mece-plan-review` 等の実装前ゲート) に切り替える。中断するのはその決定に依存する範囲だけで、依存しない可逆な仮定の spike は続けてよい。離脱時に残す成果物はガードレールが言う ADR。

## 効かせる規律

**1. 磨く(内部)と仕上げる(対外)を分ける。** step 5 = 設計の堅牢化(grill/AC/MECE/SSOT)、step 6 = レビュー/デリバリー化(QA 手順/語彙浄化)。混ぜると「対外向けに整える」圧力で設計の堅牢化が甘くなる。

**2. 効く決定は ADR(Why + 却下案)。** 後で蒸し返される決定は ADR に結晶化する(step 5 の `/grill-with-docs` が ADR を更新)。

**3. ledger は観測と status の唯一の SSOT に保つ。** 決定と Why は ADR 側に置き、ADR は観測値を ledger に委ねる(同じ事実を両方に書かない)。ledger に free-form の「決定ログ」を溜めると、step 4-6 で逆生成する doc/ADR と重複し、後追いの集約が要る。spike-N / 案ラベルは ledger 内部限定で、コードコメントや対外 doc に持ち出すなら ADR#/PR# など grep 可能な参照に置換する(`/purge-private-vocab` を待たず、書いた時点で漏らさない)。

## Common mistakes

- **設計/doc をコードより先に書く。** このスキルが反転させた順序の違反で、doc が先だと乖離する。spike → 動くコード → リファクタ → doc(step 4 以降は working code から起こす)の順を守る。
- **緑チェックを product-green と取り違える。** 動くコードは実装可能性を示すだけ。ユーザーの完了率向上は示さない。UX 仮説は post-ship で計測する。
- **variant 同士の相対比較で合否(kill/grounded)を決める。** A vs B は、どちらも**機能の目的(その機能が生む価値)を定義する ground-truth** で測っていなければ「差が無い → 無価値」と誤断する(両方ゴールを外していても気づけない)。relative 比較は候補の絞り込みにのみ使い、合否はこの ground-truth(網羅性が価値なら既知完全集合 = oracle を構築)に対する**絶対値**(recall/precision 等)で出す。

## 委譲実行 (subagent として起動された場合)

AskUserQuestion が利用可能ツールに無い実行文脈 (= subagent として Task 経由で起動された場合) では、**Start here に入る前に [references/delegated-execution.md](references/delegated-execution.md) を読む** — 対象特定・仮定ランキング確定・既存 ledger 再開・他 skill 呼び出し・Code-A standalone 化・完了報告の 6 点の読み替えを収録している。単独起動 (ユーザーがメイン会話で直接本 skill を起動した場合) の動作は変えない。

## 実例 (worked example)

- [references/worked-example-spike-to-rebuild.md](references/worked-example-spike-to-rebuild.md) — 実現性不明 → 捨て spike (既定 OFF で本番非接触) → 規約準拠で**作り直し** → 決定を ADR に保全、の 1 周を匿名化した実例。step 2 を Code-A′ のリファクタでなく作り直しで起こした変種で、「捨てるのはコード・残すのは決定」「技術実現性は ADR / UX 仮説は DD」の分離を具体で示す。

## Gotchas（観測済みの罠 — 実測で判明したものを 1 件 1 行で追記）

- 委譲プロンプトが「進められるところまで進めて」とだけ指示すると、fresh executor は ledger 更新に留まらず `The loop` step 1 (spike 実行) を経て step 2 (Code-A 実装・他リポジトリへの commit) まで自律的に進む場合がある。ledger 更新のみを期待する委譲では、到達してよい step の上限を委譲プロンプト側に明示すること (SKILL.md 側の読み替えでは制御しない — 単独起動の挙動と同じく、どこまで進めるかは呼び出し側の裁量に委ねる設計のため)。
- 対象コードベースが渡されない委譲実行で Code-A を standalone モジュールとして書く場合、既存エンドポイントの request/response 契約(multipart のフィールド名など)は推測で埋まる。契約が未確認であることをコード内コメントか ledger の仮定行に明示しないと、後続工程がその推測を確認済みの事実と誤認しうる。

## 併用推奨 skill

> **install 前提**: `/prototype` (superpowers) と `/grill-with-docs` は本 repo の plugin ではなく別途 install が必要。未 install の場合、または呼び先の形がその step の契約に合わない場合 (例: step 1 が要求する「本番正本との数値照合」に対し `/prototype` が対話型プロトタイプしか作らない) は、手動の throwaway spike / ドメイン用語レビューで代替する — 契約は親である本 skill 側が持つ。本 repo 内の plugin は `/review-design` `/define-acceptance-criteria` `/mece-plan-review` `/dry-ssot-text` `/finalize-plan` `/purge-private-vocab`。

- `/prototype` — step 1 の throwaway スパイク
- `/review-design` — step 3 のリファクタ/配置判断
- `/grill-with-docs` `/define-acceptance-criteria` `/mece-plan-review` `/dry-ssot-text` — step 5 の設計書磨き
- `/finalize-plan` `/dry-ssot-text` `/purge-private-vocab` — step 6 のレビュー/デリバリー仕上げ
