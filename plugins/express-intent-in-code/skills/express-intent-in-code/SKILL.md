---
name: express-intent-in-code
description: Use when you have a confirmed working-code target (a method / value / type inside this change's blast radius) whose name stops at mechanism (`bbox_xhtml`) or shape (`word_coordinate_data`) and whose purpose survives only in why-comments, when /review-code-quality hands off a naming / cohesion finding as needs-judgment, or when the user says 「意図が伝わる名前にして」「why コメントを名前/型に昇格して」「この関数の目的を名前で表現して」「コメントなしで読めるコードにして」. Lifts one target up a naming ladder (機構名 → what名 → 目的名) and promotes the why a name cannot carry into types / sum types / tests, leaving only the true why that code can never reveal as comments. Outputs before/after diffs, 3 rename candidates with the why each expresses, a promote-and-delete comment list, and the residual true-why — not a diagnosis list. Do NOT drive-by rename working code outside the named target, and do NOT scan a whole diff for what to fix (that is /review-code-quality, the diagnoser; this is the deep one-point transformer).
---

# Express Intent In Code

## Overview

読み手が最も知りたいのは「どう動くか (how/what)」ではなく「**なぜこの名前・行・構造がここに在るのか (why = ドメイン上の目的)**」。why コメントが増殖するのは、名前が機構 (`bbox_xhtml`) や形状 (`word_coordinate_data`) 止まりで目的を表明できていない、もしくはドメイン概念が primitive・分岐・暗黙の不変条件に隠れている (概念欠落) サインである。正しい修正は**コメント追加ではなく「目的名への昇格 + 概念の構造化」**。

このスキルは working code を 1 点受け取り、名前/型/構造/テストを why 表明形へ**深く変換する規律**: caller を平叙文化 → 機構/目的を分離 → 目的名へ昇格 → 名前で担えない why を型/sum type/テストへ昇格 → コードから絶対に読めない真の why のみコメント残置。`/review-code-quality` の「広く浅い診断」とは別物 (狭く深い一点突破の変換)。境界の詳細は [references/boundary-and-scope.md](references/boundary-and-scope.md)。

**ゴールは why コメントの撲滅ではなく純化** — 昇格できる why は名前/型/テストへ移して消し、外部仕様・トレードオフ根拠・危険・将来予定の 4 類型だけは残す。

## When to use / not

**使う**: 対象が確定した working code 1 点 (メソッド/値/型) で、名前が機構や形状止まり・目的が why コメントだけに宿っている。`/review-code-quality` が naming/凝集 finding を needs-judgment として申し送ってきた。

**使わない**:
- diff 全体を広く浅くスキャンして「何を直すか」診断したい → `/review-code-quality`
- 規約テキスト依存の機械的コメント整形 → `/polish-before-commit`
- 今回の変更対象でない隣接コードの drive-by 改名 (Surgical Changes 違反)
- 段4 ドメイン抽象への到達を必須化すること (段4 は上限、段3 で意図が十分なら据え置く)

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
| **段4** | ドメイン抽象 | ユビキタス言語 (専門家の共有語)。**上限・必須でない** | `signing_positions` |

各段の上げ方と bbox_xhtml の全段ウォークスルーは [references/naming-ladder.md](references/naming-ladder.md)。

## Workflow

> 各ステップの詳細・アンチパターン・コミット境界の切り方は [references/decision-procedure.md](references/decision-procedure.md) が SSOT。本文は操作チェックリスト。

- **Step 0 適用判定**: 対象が (a) working code で (b) 今回の変更対象 (blast radius 内) か確認。drive-by 改名は中止。着手前に回帰テスト/characterization test の有無を確認し、無ければ先に用意して振る舞いを固定する (改名は意味を変えうる)。対象が 1 点に確定していなければユーザーに確認。
- **Step 1 現在段の診断**: 対象名を梯子のどこか判定 (機構語リストで段0、用途が読めるかで段1/段3 を切り分け)。1 段ずつ上げる。
- **Step 2 caller 観測 (平叙文化)**: 全 caller を grep し「戻り値を次に何に使うか」を 1 動詞句で言語化。caller を読まず目的名をでっち上げない (押印用途を `signature` と決め打つ退行を防ぐ)。複数 caller が別目的なら 1 メソッド 2 役 → 改名でなく分離 (T2) を先に。**「同一概念 (中立な目的名 1 本) か 2 役 (分割) か」は戻り値の形が同じかでなく、両 call site で真に読める単一目的名を選べるかで判定する** — 選べなければ (どの名前を選んでも片方の call site で嘘になる) 2 役 → 分割し、共有する射影は private 機構メソッドへ。
- **Step 3 Honest 化と構造の発見**: 目的名へ直行せず、いったん「何を・何から・何を経由して」を全部出した長い正直名へ。`and`/`with` 複数 = 責務複数 (T2)、消せない機構語 = ドメイン型欠落 (T5/T6)。長さは構造を直して縮める (語を削らない)。
- **Step 4 嘘の除去 (段2)**: 名前に出ない副作用・前提・除外を列挙し、名前へ昇格するか別メソッドへ追い出して名前 = 契約を成立させる。飛ばすと why コメント依存が温存される。
- **Step 5 目的名への昇格 (段3) + why の構造化**: caller 用途を核にドメイン役割名へ。名前 1 つで担えない不変条件・状態・全称的約束は T5(型)/T6(sum type)/T7(戻り型)/T9(テスト) へ昇格。判定軸は「コメントで補っている不変条件を 1 つでも型/構造/テストへ移せたか」。
- **Step 6 コメントの蒸留と純化**: 各 why コメントを keep-vs-promote 決定表で振り分け、畳めたものを削除。**順序厳守: 名前/構造変換 → 表明できた why を削除 → 真の why のみ残置** (先にコメントを消さない)。詳細 [references/comment-keep-vs-promote.md](references/comment-keep-vs-promote.md)。
- **Step 7 過剰昇格の歯止め (T10)**: 意図を足さないラッパ・1 ケース多態・造語目的名・過長名を Inline/据え置きで畳む。rule of three を待つ。
- **Step 8 fresh-eyes 検証**: after の名前/シグネチャ**だけ** (コメント・plan 無し) を見て目的を言い当てられるか検証する。非自明な対象は [agents/intent-reader.md](agents/intent-reader.md) を Task で起動 (bias-free)、自明な単一改名は cold self-read で代替。推論された目的が caller 観測の目的と食い違えば名前を再調整。
- **Step 9 検証と粒度・出力**: 各変換後に lint/test を通す (Ruby: rubocop+rspec / TS: eslint+prettier / 他言語はプロジェクトのテストランナー、無ければ手動検証を明記)。grep で全 caller/spec/コメント参照の改名漏れを洗う。**広域 gsub/sed は使わず対象限定 Edit**。改名→分割→型化→コメント削除を 1 コミットに混ぜない。出力は下記フォーマット。

## 技法選択 (trigger → T)

症状から技法を引く。high から順に適用を検討。各 T の move 詳細と before/after は [references/technique-catalog.md](references/technique-catalog.md)。

| T | 技法 | trigger (この症状なら) | lev |
|---|---|---|---|
| T1 | 目的語昇格 rename | 名前が取得元/内部表現/ノイズ語で、用途を知るのに本体か why コメントが要る | high |
| T2 | 意図名で関数抽出 | 1 メソッドが取得+変換+選別など複数段を抱え、段落コメントが各段を代弁 | high |
| T3 | コメント→名前/型/定数 蒸留 | 式/数値/条件の横に what 説明、同 why が 2+ 箇所に散る | high |
| T4 | 説明変数・要約変数 | 巨大式/複合条件を実行シミュレートしないと読めない | high |
| T5 | primitive→値オブジェクト/型 | Hash/string/数値タプルに同 why (検証済み・座標系・用途) が散る | high |
| T6 | sum type + 網羅強制 | 状態タグ+null 同居で不正状態が作れる/switch が複数箇所に散在 | high |
| T7 | parse, don't validate | `T→bool`/`T→void` が検査結果を捨て、下流で再検証/nil 分岐が散る | med |
| T8 | 制御フローを目的の流れへ | 深いネスト/再代入で概念がブレる/計算と副作用が同居 | med |
| T9 | テスト/property を why の第二の声に | 改名で why が乗りきらない (用途複数・全称的約束) | med |
| T10 | Inline/据え置きの歯止め | 意図を足さないラッパ/1 ケース多態/造語目的名/過長名 | med |
| T11 | 境界・一貫命名の固定 | `min`/`max` が包含か排他か不明/同一概念に名前揺れ | low |

## コメント keep-vs-promote (要約)

判定軸は Ousterhout「**その情報はコードの抽象 (名前・型・構造・テスト) から自明か**」の一点。

- **昇格して削除**: 値の正体/存在理由/分岐理由/マジック値の意味/変換手順/自明な what/シグネチャの言い換え → 名前・型・定数・述語メソッドへ移す。
- **残す (真の why 4 類型)**: (a) 外部仕様・他システム前提 (b) トレードオフ/最適化見送りの根拠数値 (c) 危険・順序依存・実行時不変条件 (d) 将来予定 FIXME (理想+妥協理由)。昇格を試みず、文面のゴール志向化と数値付与だけ改善。

振り分け先の対応表・純化ルール (構造的 Goal→制約→手段は ADR 集約 + コメント 1 行参照) は [references/comment-keep-vs-promote.md](references/comment-keep-vs-promote.md)。

## アンチパターン (頻出のみ・全文は decision-procedure.md)

- **why コメント撲滅の誤読**: 外部制約・根拠数値・危険警告まで消す。ゴールは撲滅でなく純化。
- **what 止まりで満足**: `bbox_xhtml → word_coordinate_data` で止め目的に届かない (= ユーザー退行の正体)。caller 用途を動詞句にして役割名まで上げる。
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
