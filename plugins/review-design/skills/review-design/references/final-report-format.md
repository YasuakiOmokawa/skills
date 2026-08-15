# Final report format (Step 6)

Choose the first matching route: (0) stopped with unresolved reviewer ❌ / fatal, (1) no plan, (2) plan edited at any point, (3) unedited with ⚠️ / Unknown / acceptable residual, (4) unedited and all green. Treat Unknown as a residual, never as green. Repeated non-fatal items remain route 2 or 3; they never select route 0.

## Unresolved route

Condition: route 0. Use `保存先: <plan>.design-review.md` when a plan exists; otherwise use `保存: プランファイル不在のため skip`.

```
設計レビュー未完了。未解決:
- <reviewer ❌ or fatal and why no grounded edit remains>
<保存先または保存行>
```

## Problem-free route

Condition: route 4.

```
設計レビュー完了。問題なし。
保存先: <plan>.design-review.md
```

## Problem-found route

Condition: route 2. This route wins even when the final re-review is all green.

```
設計レビュー完了。以下を修正しました:
- <what → how it was fixed (1 issue = 1 line)>
- <...>
残存リスク:
- <acceptable risk and rationale, or Unknown with missing evidence>
保存先: <plan>.design-review.md
```

残存リスクが無い場合はそのブロックを省略する。

The plan file body must contain the corrected design itself, never an analysis summary or report dump.

## Residual-risk route

Condition: route 3.

```
設計レビュー完了。修正なし・残存リスクあり:
- <acceptable risk and rationale, or Unknown with missing evidence>
保存先: <plan>.design-review.md
```

## プラン不在の場合 (Step 0 で feature description のみが得られ、プランファイルパスが解決できない invocation)

Step 4 の Edit と Step 6 の Write はどちらも保存先パスが無いため実行しない (存在しないパスへの書き込みを試みない)。指摘はプランへの反映でなく、チャット応答内に直接提示する。

```
設計レビュー完了 (プランファイル不在のためレビュー結果を直接提示)。
- <reviewer / Devil's Advocate の指摘 (1 issue = 1 line)。指摘が無ければ「問題なし」>
- <...>
保存: プランファイル不在のため skip
```

### "1 issue = 1 line" granularity

- Same logical issue rippling across multiple files / spots → **one line** (collapse to the root issue).
- Independent issues (e.g. transaction boundary violation **and** God Class avoidance) → **separate lines**.

## In-context fallback notation

Add the tag only when the environment forced reviewer or DA fallback, never for normal `inline default`.

Tail format (append exactly one line at the end of the chat report and therefore at the end of the saved prefix; the saved-only audit sections follow it):

```
(in-context fallback mode: <agent names slash-separated>)
```

Do not include per-reviewer dumps, intermediate DA critiques, or feedback-loop state.

## Step 6 の保存ファイル (`<plan>.design-review.md`)

チャット表示 (上記の該当 route) はこのまま変更しない。加えて、Step 6 完了時に必ず `Write` で保存する。

**パス規則**: Step 0 で解決したプランファイルパスの拡張子直前に `.design-review` を挿入する (例: `feature-x.md` → `feature-x.design-review.md`)。

**保存内容**: チャット route 本文を一字一句変えず先頭へ置き、後続のオーケストレータ監査パックが機械参照するための 3 節を追記する (チャットには出さない情報だが、保存ファイルには必須)。要約・補足・言い換えで prefix を変えない。

```
<チャット表示と同じ本文 (選択した route)>

## Fatal 残存

fatal 残存件数: <N>
reviewer ❌ 残存件数: <R>
- <unresolved item, or 該当なし>

## Acceptable 残存リスク

| 指摘元 | 内容 | 判断根拠 |
|---|---|---|
| DA | <Step 5 最終ラウンドで acceptable と判定された critique> | <grounding / 判定理由> |
| <reviewer name> | <Step 3 で ⚠️ のまま Edit されなかった指摘> | <理由> |
| <reviewer name> | <Step 3 の Unknown> | Unknown: <不足証拠と解消条件> |

## Hidden assumption

- <Step 5.4 で洗い出した hidden assumption (1-2 件)>
```

- 通常の完了 route は `N=0, R=0`。Unresolved route は実数と各指摘を記録する
- 「Acceptable 残存リスク」は Step 5 最終ラウンドの DA acceptable、Step 3 の ⚠️、Unknown を 1 行 1 件で列挙する。Unknown は acceptable と断定せず、不足証拠と解消条件を書く。該当が 1 件もない場合も見出しを残し「該当なし」と書く。
- 「Hidden assumption」は Step 5.4 で洗い出した前提を 1 行 1 件で列挙する。該当なしの場合も見出し行は残し「該当なし」と書く
