---
name: express-intent-in-code
description: Use when the redundancy-guard hook reports added comments / lint suppressions / a new file next to siblings, before writing a new helper / util / file (reuse ladder), when /review-code-quality hands off a naming / cohesion finding, when a name stops at mechanism (`bbox_xhtml`) or shape (`word_coordinate_data`) and its purpose survives only in why-comments, or when the user says 「意図が伝わる名前にして」「コメントなしで読めるコードにして」.
---

# Express Intent In Code

意図はコメントでなく名前・型・構造で表明する。ゴールは why コメントの撲滅ではなく**純化** — 昇格できる why はコードへ移し、コードから読めない真の why だけを残す。

## 書く前の再利用梯子 (最初に該当した段で止める)

新しい関数・ヘルパー・ファイルを書き始める前に順に問う:
⓪そもそも要るか → ①このコードベースに既にあるか (隣接ファイル・同種 dir を grep してから書く — 数ファイル先の再実装が最頻の無駄) → ②言語標準 → ③プラットフォーム標準機能 → ④導入済み依存 → ⑤どれも無ければ最小コード。
suppression (rubocop:disable 等) を書きたくなったら①へ戻る — 既存イディオムなら不要なことが多い。

## 命名梯子 (飛び級禁止、1 段ずつ)

段0 機構/ノイズ語 (`bbox_xhtml`, `data`, `tmp`) → 段1 正直な what (`word_coordinate_data`) → 段2 嘘の除去 (名前に出ない副作用・前提を名前へ) → 段3 目的名 (`signature_anchor_boxes`) → 段4 ドメイン語 (`signing_positions`)。

- 段3 へ上げる前に**全 caller を観測**し、用途を 1 動詞句で言語化する (読まずにでっち上げない)。caller ごとに用途が割れるなら改名でなく分離する。
- 段4 は実在するドメイン語 (codebase / 仕様 / UI 文言) への接地が条件。**造語禁止** — 見つからなければ段3 で止め、探索した旨を一言残す。

## コメントの判定

書く前に (または hook に指摘されたら) 昇格を試みる:

| コメントが説明しているもの | 昇格先 |
|---|---|
| 値の正体・データ形状 | 型 / 値オブジェクト |
| 用途・存在理由 | 名前 (目的名) |
| 分岐理由・複合条件 | 述語メソッド / 説明変数 |
| マジック値の意味 | 定数 |
| 手順の段落・機構・外部制約への弁明 | 意図名の private へ抽出 |
| boolean 引数の意味 | enum / シンボル |
| null / undefined の意味差 | 判別可能 union |

**残す = 真の why 4 類型のみ**: 外部仕様・他システム前提 / 実測根拠・トレードオフ数値 / 危険・順序依存・セキュリティ判断 / FIXME (理想 + 妥協理由)。置き場所はそれを担う名前付き定義の直上 1 箇所で、公開メソッド本体には書かない。文面は code-comments 7 原則に従う。**既存の 4 類型コメントは削らない。why の記録が 0 箇所になったら削りすぎ。**

## 歯止め

- 対象は今回の変更 1 点のみ。隣接コードの drive-by 改名はしない。
- **既存の実装・ヘルパー・イディオムの再利用は n=1 で行う。新しい共有抽象の抽出は rule of three を待つ。**
- 意図を足さないラッパ・1 ケースの多態・過長名を作らない。
- 広域 sed/gsub 禁止。変換後は lint / test を通し、caller・spec・コメント内参照の改名漏れを grep で確認する。

## 検証

変換後の名前とシグネチャ**だけ**を見て (本体・コメントなしで) 目的を言い当てられるか。言えなければ段が足りない。
