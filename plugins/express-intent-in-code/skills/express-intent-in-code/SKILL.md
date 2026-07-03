---
name: express-intent-in-code
description: Use on a confirmed working-code target (method/value/type in this change's blast radius) whose name stops at mechanism (`bbox_xhtml`) or shape (`word_coordinate_data` / `useFieldSaveState`) and whose purpose survives only in why-comments, when /review-code-quality hands off a naming / cohesion finding as needs-judgment, or when the user says 「意図が伝わる名前にして」「この関数の目的を名前で表現して」「コメントなしで読めるコードにして」. Lifts one target up a naming ladder (機構名 → what名 → 目的名 → ドメイン抽象); 段4 ドメイン抽象 (`signing_positions`) is the best-effort target, reached by sourcing the real domain word (codebase/spec/UI) or extracting the missing type — never inventing jargon. Promotes why a name can't carry into types/tests, leaving true why as comments. Do NOT drive-by rename outside the target nor scan a whole diff (that is /review-code-quality; this is the deep one-point transformer) — the only self-run whole-diff pass is a mechanical grep screening for homonym collisions (e.g. auth `token` vs placeholder `token`) and 段0 noise-word identifiers.
---

# Express Intent In Code

## Overview

読み手が最も知りたいのは「どう動くか (how/what)」ではなく「**なぜこの名前・行・構造がここに在るのか (why = ドメイン上の目的)**」。why コメントが増殖するのは、名前が機構 (`bbox_xhtml`) や形状 (`word_coordinate_data` / `useFieldSaveState`) 止まりで目的を表明できていない、もしくはドメイン概念が primitive・分岐・暗黙の不変条件に隠れている (概念欠落) サインである。正しい修正は**コメント追加ではなく「目的名への昇格 + 概念の構造化」**。

**到達目標は段4 ドメイン抽象** (`bbox_xhtml` → `signing_positions`) — 本体を 1 行も読まず**名前だけで意図・達成したいゴール・目的が掴める**水準。段4 へは 2 経路で到達する: codebase/仕様/UI 文言から実在のドメイン語を探して**それへ snap** (経路A)、または primitive が群れて欠落型を示しているなら**型 (Whole Value) を抽出** (経路B)。段4 は辞書引きの改名ではなく、しばしば型抽出という構造変更。共有語が無いのに造語して段4 に上げてはならない (確信ありげな誤誘導名は正直な what 名より有害)。詳細は [references/domain-abstraction.md](references/domain-abstraction.md)。

このスキルは working code を 1 点受け取り、名前/型/構造/テストを why 表明形へ**深く変換する規律**: caller を平叙文化 → 機構/目的を分離 → 目的名へ昇格 → ドメイン語を探索し段4 へ昇格 (or 探索ログを残して据え置き) → 名前で担えない why を型/sum type/テストへ昇格 → コードから絶対に読めない真の why のみコメント残置。`/review-code-quality` の「広く浅い診断」とは別物 (狭く深い一点突破の変換)。境界の詳細は [references/boundary-and-scope.md](references/boundary-and-scope.md)。

**ゴールは why コメントの撲滅ではなく純化** — 昇格できる why は名前/型/テストへ移して消し、外部仕様・トレードオフ根拠・危険・将来予定の 4 類型だけは残す。

## When to use / not

**使う**: 対象が確定した working code 1 点 (メソッド/値/型) で、名前が機構や形状止まり・目的が why コメントだけに宿っている。`/review-code-quality` が naming/凝集 finding を needs-judgment として申し送ってきた。

**使わない**:
- diff 全体を広く浅くスキャンして「何を直すか」診断したい → `/review-code-quality`
- 規約テキスト依存の機械的コメント整形 → `/polish-before-commit`
- 今回の変更対象でない隣接コードの drive-by 改名 (Surgical Changes 違反)
- 共有語が無いのに造語して段4 に上げること (段4 は実在証拠への接地が前提。探索が空振りなら段3 据え置き + 探索ログ)
- 段4 へ到達した型を全 call site へ波及させる広域改名 (対象 1 点のみ変換)

**バッチ / パイプライン起動 (単一対象が未指定のとき)**: `/simplify` 等の品質パイプライン後段で、単一対象も `/review-code-quality` からの naming/凝集 handoff も無いまま起動された場合 — diff 全体を改名候補スキャンしない (それは `/review-code-quality` の役割で、本スキルが肩代わりしない)。handoff があればそれを変換対象に取り、handoff も明示対象も無ければ diff 名を列挙せず「handoff 無しのため変換対象なし」と即 no-op 宣言する (無人パイプラインを確認待ちで止めない)。**例外 — grep で拾える 2 兆候は handoff の有無によらず対象に加える**: (a) 多義衝突 (blast radius 内で同じ語が 2 つのドメイン概念を指す。例: URL 認証の `token` と焼き込みプレースホルダーの `token`) と (b) 新規識別子の段0 ノイズ語 (`doc`/`data`/`info`/`target`/`tmp` 等)。診断器の handoff は表層 finding に偏りこの 2 種を落とす実績があるため、機械的な grep 1 パスに限り本スキルが直接スクリーニングする (診断的な網羅レビューには広げない)。スクリーニングや変換中に見つけた**副次候補** (対象外の別衝突・別ノイズ語) は対象化せず、出力の据え置きログに 1 行で残して次の `/review-code-quality` パスの入力にする。

スコープ内/外の全リストは [references/boundary-and-scope.md](references/boundary-and-scope.md)。

## 命名梯子 (このスキルの背骨)

名前を 1 段ずつ上げる。**飛び級 (段0 → 目的名直行) は禁止** — 機構違いの別案で発散する。

| 段 | 名前の型 | 見分け方 | 例 (bbox_xhtml ケース) |
|---|---|---|---|
| **段0** | 機構/Nonsense | 取得元・内部表現・ノイズ語が核 (`bbox` `xhtml` `data` `info` `tmp` `retval` `manager` `util` `handle` `dto` `impl`) | `bbox_xhtml` |
| **段1** | what/Honest | やること・戻り値の形は読めるが目的は読めない | `word_coordinate_data` |
| 段1.5 | 構造の発見 | 長い正直名の `and`/`with`/`from` 複数 = 責務複数、消せない機構語 = ドメイン型欠落 | (分割/型化のサイン) |
| **段2** | 嘘の除去 | 名前に出ない副作用/前提/除外がある (空行除外・座標系反転・キャッシュ) | (`…_excluding_empty` 等へ) |
| **段3** | Intent/目的名 | caller のドメイン役割 (why) を表明 | `signature_anchor_boxes` |
| **段4** | ドメイン抽象 | ユビキタス言語 (専門家・仕様・UI 文言の実在共有語)。**既定の到達目標**。実在語へ snap か欠落型の抽出で到達 | `signing_positions` |

各段の上げ方と bbox_xhtml の全段ウォークスルーは [references/naming-ladder.md](references/naming-ladder.md)。段4 への到達手続き (探索 Step A–H・造語ゲート・据え置き記録) は [references/domain-abstraction.md](references/domain-abstraction.md)。

## Workflow

> 各ステップの詳細・アンチパターン・コミット境界の切り方は [references/decision-procedure.md](references/decision-procedure.md) が SSOT。本文は操作チェックリスト。

- **Step 0 適用判定**: 対象が (a) working code で (b) 今回の変更対象 (blast radius 内) か確認。drive-by 改名は中止。着手前に回帰テスト/characterization test の有無を確認し、無ければ先に用意して振る舞いを固定する (改名は意味を変えうる)。対象が 1 点に確定していなければユーザーに確認。
- **Step 1 現在段の診断**: 対象名を梯子のどこか判定 (機構語リストで段0、用途が読めるかで段1/段3 を切り分け)。1 段ずつ上げる。同時に**多義衝突を grep で検査**: 対象名の核となる語が blast radius 内で別のドメイン概念にも使われていないか全出現を分類する。衝突していれば段の高低より優先して片方を実在ドメイン語へ逃す (T11) — 読者は文脈の近い方の意味で誤読するため、正直な what 名でも衝突したままでは有害。
- **Step 2 caller 観測 (平叙文化)**: 全 caller を grep し「戻り値を次に何に使うか」を 1 動詞句で言語化。caller を読まず目的名をでっち上げない (押印用途を `signature` と決め打つ退行を防ぐ)。複数 caller が別目的なら 1 メソッド 2 役 → 改名でなく分離 (T2) を先に (**caller が 1 つなら 2 役判定は省略**)。**「同一概念 (中立な目的名 1 本) か 2 役 (分割) か」は戻り値の形が同じかでなく、両 call site で真に読める単一目的名を選べるかで判定する** — 選べなければ (どの名前を選んでも片方の call site で嘘になる) 2 役 → 分割し、共有する射影は private 機構メソッドへ。
- **Step 3 Honest 化と構造の発見**: 目的名へ直行せず、いったん「何を・何から・何を経由して」を全部出した長い正直名へ。`and`/`with` 複数 = 責務複数 (T2)、消せない機構語 = ドメイン型欠落 (T5/T6)。長さは構造を直して縮める (語を削らない)。
- **Step 4 嘘の除去 (段2)**: 名前に出ない副作用・前提・除外を列挙し、名前へ昇格するか別メソッドへ追い出して名前 = 契約を成立させる。飛ばすと why コメント依存が温存される。
- **Step 5 目的名への昇格 (段3) + why の構造化**: caller 用途を核にドメイン役割名へ。名前 1 つで担えない不変条件・状態・全称的約束は T5(型)/T6(sum type)/T7(戻り型)/T9(テスト) へ昇格。判定軸は「コメントで補っている不変条件を 1 つでも型/構造/テストへ移せたか」。
- **Step 5.5 段4 ドメイン抽象への到達 (既定目標)**: 段3 に達したら必ず段4 を試みる。**ドメイン語を探索** (概念を 1 文化 → codebase grep → user-facing 文言 → 仕様/ADR/テスト記述/PR タイトル)。実在語が見つかれば新造せず snap (経路A。**複数の実在語があれば repo 頻度でなく「対象の概念を指す語」= use site に近い語を選ぶ**)。段3 でも明確な語が書けない/機構語が消せない/primitive が群れているなら設計のサイン → 分割/型抽出 (T2/T5/T6) で欠落型を出してから命名 (経路B)。**genuine-vs-invented ゲート**で合否判定 (≥2 独立ソース or 1 権威ソース・sentence test・型は複数使用箇所 → PASS / どこにも無い・CS 語彙偽装・新 synonym → FAIL)。ゲートが通る語が無ければ段3 据え置き + **探索ログを記録** (探索せず安住しない)。詳細 [references/domain-abstraction.md](references/domain-abstraction.md)。
- **Step 6 コメントの蒸留と純化**: 各 why コメントを keep-vs-promote 決定表で振り分け、畳めたものを削除。**順序厳守: 名前/構造変換 → 表明できた why を削除 → 真の why のみ残置** (先にコメントを消さない)。詳細 [references/comment-keep-vs-promote.md](references/comment-keep-vs-promote.md)。
- **Step 7 過剰昇格の歯止め (T10)**: 意図を足さないラッパ・1 ケース多態・造語目的名・過長名を Inline/据え置きで畳む。rule of three を待つ。
- **Step 8 fresh-eyes 検証**: after の名前/シグネチャ**だけ** (コメント・plan 無し) を見て目的を言い当てられるか検証する。非自明な対象は [agents/intent-reader.md](agents/intent-reader.md) を Task で起動 (bias-free)、自明な単一改名は cold self-read で代替。**非自明の線引き**: 構造変換 (T2/T5/T6/T8) を伴い変換後の識別子が複数になる場合は非自明とみなし intent-reader を既定とする (Task 起動不能な環境では cold self-read に落とし、その旨を出力に明記)。推論された目的が caller 観測の目的と食い違えば名前を再調整。
- **Step 9 検証と粒度・出力**: 各変換後に lint/test を通す (Ruby: rubocop+rspec / TS: eslint+prettier / 他言語はプロジェクトのテストランナー、無ければ手動検証を明記)。grep で全 caller/spec/コメント参照の改名漏れを洗う。**広域 gsub/sed は使わず対象限定 Edit**。改名→分割→型化→コメント削除を 1 コミットに混ぜない。出力は下記フォーマット。

## 技法選択 (trigger → T)

症状から技法を引く。high から順に適用を検討。各 T の move 詳細と before/after は [references/technique-catalog.md](references/technique-catalog.md)。

| T | 技法 | trigger (この症状なら) | lev |
|---|---|---|---|
| T1 | 目的語昇格 rename | 名前が取得元/内部表現/ノイズ語で、用途を知るのに本体か why コメントが要る | high |
| T2 | 意図名で関数抽出 | 1 メソッドが取得+変換+選別など複数段を抱え、段落コメントが各段を代弁 | high |
| T3 | コメント→名前/型/定数 蒸留 | 式/数値/条件の横に what 説明、同 why が 2+ 箇所に散る | high |
| T4 | 説明変数・要約変数 | 巨大式/複合条件を実行シミュレートしないと読めない | high |
| T5 | primitive→値オブジェクト/型 (**段4 経路B**) | Hash/string/数値タプルに同 why (検証済み・座標系・用途) が散る/primitive が群れ欠落型を示す | high |
| T6 | sum type + 網羅強制 (**段4 経路B**) | 状態タグ+null 同居で不正状態が作れる/switch が複数箇所に散在 | high |
| T7 | parse, don't validate | `T→bool`/`T→void` が検査結果を捨て、下流で再検証/nil 分岐が散る | med |
| T8 | 制御フローを目的の流れへ | 深いネスト/再代入で概念がブレる/計算と副作用が同居/中間対応表 (`x_to_y` hash) を作って後段で逆引きする | med |
| T9 | テスト/property を why の第二の声に | 改名で why が乗りきらない (用途複数・全称的約束) | med |
| T10 | Inline/据え置きの歯止め | 意図を足さないラッパ/1 ケース多態/造語目的名/過長名 | med |
| T11 | 境界・一貫命名の固定 | `min`/`max` が包含か排他か不明/同一概念に名前揺れ/1 語が blast radius 内で 2 概念を指す (多義衝突。これのみ high 扱い) | low |

## コメント keep-vs-promote (要約)

判定軸は Ousterhout「**その情報はコードの抽象 (名前・型・構造・テスト) から自明か**」の一点。

- **昇格して削除**: 値の正体/存在理由/分岐理由/マジック値の意味/変換手順/自明な what/シグネチャの言い換え → 名前・型・定数・述語メソッドへ移す。
- **残す (真の why 4 類型)**: (a) 外部仕様・他システム前提 (b) トレードオフ/最適化見送りの根拠数値 (c) 危険・順序依存・実行時不変条件 (d) 将来予定 FIXME (理想+妥協理由)。昇格を試みず、文面のゴール志向化と数値付与だけ改善。

振り分け先の対応表・純化ルール (構造的 Goal→制約→手段は ADR 集約 + コメント 1 行参照) は [references/comment-keep-vs-promote.md](references/comment-keep-vs-promote.md)。

## アンチパターン (頻出のみ・全文は decision-procedure.md)

- **why コメント撲滅の誤読**: 外部制約・根拠数値・危険警告まで消す。ゴールは撲滅でなく純化。
- **what 止まりで満足**: `bbox_xhtml → word_coordinate_data` で止め目的に届かない (= ユーザー退行の正体)。caller 用途を動詞句にして役割名まで上げる。
- **段3 で安住 (探索せず据え置き)**: 段3 に達したのにドメイン語を探さず据え置く。本体を読まないと目的が掴めない名前を残す退行。段4 を必ず試み、据え置くなら探索ログを残す。
- **段4 を造語で偽装**: 実在証拠の無い「それっぽい」語や CS 語彙 (`Manager`/`Handler`) を段4 名にする。確信ありげな誤誘導名は正直な what 名より comprehension が悪い。grep/仕様/UI 文言に接地できなければ却下。
- **名前が見つからないのに改名で押し切る**: 段3 でも明確な語が書けないのは設計のサイン (対象が 2 概念を抱える)。辞書を引くのでなく分割/型抽出で構造を直してから命名する。
- **caller を読まない目的名のでっち上げ**: 用途を観測せず「それっぽい why 名」を付け、`word_coordinate_data` より悪い誤誘導を生む。
- **機構語の全消去で grep 不能化**: `bbox`/`xhtml` を public 名から外しても private 構築経路に残しトレーサビリティを確保。
- **過剰昇格**: 意図を足さない 1-2 行ラッパ・1 ケース空 subclass・造語目的名・過長名で間接層だけ増やす。
- **広域 gsub/sed での改名**: コードを黙って壊す。対象限定 Edit + 適用直後の lint/build 検証を厳守。

## 出力フォーマット

指摘リストではなく**変換成果物**を出す:

```markdown
## express-intent-in-code: <対象>

### 診断
- 現在段: 段N (<理由>) / caller 用途: 「<1動詞句>」

### 改名候補 (3 案 + 各案が表明する why)
1. `<案A>` — <表明する why の差分>
2. `<案B>` — <差分>
3. `<案C>` — <差分>  → 推奨: <案> (<根拠: caller 用途/ユビキタス言語>)

### 段4 到達の根拠 (grounding) — または 据え置きの根拠 (探索ログ)
- 到達した場合: 採用したドメイン語 `<語>` の出所 (`file:line`、行が不明なら file 名 / spec section でも可)。経路A (実在語へ snap) か経路B (型抽出) かを明記。
- 据え置く場合: 概念の 1 文 / 試した候補語 / 探索したソースと結果 (codebase grep・UI 文言・仕様) / 失敗したゲート基準。

### before / after
\`\`\`diff
- <before>
+ <after>
\`\`\`

### 昇格して削除したコメント
- `file:line` 「<コメント>」→ <昇格先 (名前/型/定数/テスト)>

### 残す真の why (4 類型ラベル付き)
- `file:line` 「<コメント>」(類型a 外部仕様) — <純化後の文面>
```

`/review-code-quality` から申し送られた場合は、元 finding にひも付けて返す。

## 併用推奨 skill

- `/review-code-quality` — 診断器。naming/凝集 finding を needs-judgment として本スキルへ渡す前段 (直列関係)。
- `/polish-before-commit` — 規約テキスト依存の機械的コメント整形・最終仕上げ。本スキルの後段。
- `/purge-private-vocab` — 段4 で造語しない原則と同じ思想 (plan 造語の除染)。目的名にローカル造語を混ぜないための照合に使える。
