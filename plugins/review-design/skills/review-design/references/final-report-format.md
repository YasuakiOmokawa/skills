# Final report format (Step 6)

The final report has three routes: two depending on whether the plan was edited, plus one for when no plan file exists at all.

## Problem-free route

Conditions: Parallel Review all ✅ **AND** Devil's Advocate fatal count = 0.

```
設計レビュー完了。問題なし。
保存先: <plan>.design-review.md
```

## Problem-found route

Conditions: any reviewer returned ❌/⚠️, OR DA flagged ≥1 fatal finding and Edit was executed.

```
設計レビュー完了。以下を修正しました:
- <what → how it was fixed (1 issue = 1 line)>
- <...>
保存先: <plan>.design-review.md
```

The plan file body must contain the corrected design itself, never an analysis summary or report dump.

## プラン不在の場合 (Step 0 で feature description のみが得られ、プランファイルパスが解決できない invocation)

Step 4 の Edit と Step 6 の Write はどちらも保存先パスが無いため実行しない (存在しないパスへの書き込みを試みない)。指摘はプランへの反映でなく、チャット応答内に直接提示する。

```
設計レビュー完了 (プランファイル不在のためレビュー結果を直接提示)。
- <reviewer / Devil's Advocate の指摘 (1 issue = 1 line)。指摘が無ければ「問題なし」>
- <...>
保存: プランファイル不在のため skip
```

「1 issue = 1 line」の粒度規則 (下記) は本テンプレートにも適用する。

### "1 issue = 1 line" granularity

- Same logical issue rippling across multiple files / spots → **one line** (collapse to the root issue).
- Independent issues (e.g. transaction boundary violation **and** God Class avoidance) → **separate lines**.

## In-context fallback notation

This tag is added ONLY when the environment forced fallback for at least one of:

- Parallel Review reviewers (Step 3)
- Devil's Advocate (Step 5, subagent dispatch attempt failed due to env constraint)

It is **NOT** added when DA simply ran in `inline default` mode (the normal path) — that is not an environment-constraint fallback. Readers must not confuse "ran inline by design" with "ran inline because Task was unavailable".

Tail format (append exactly one line at the very end of the final report):

```
(in-context fallback mode: <agent names slash-separated>)
```

### Examples

DA only fell back:

```
(in-context fallback mode: devil's-advocate)
```

All reviewers + DA fell back:

```
(in-context fallback mode: anti-pattern-checker / ddd-reviewer / hexagonal-reviewer / clean-architecture-reviewer / devil's-advocate)
```

## What NOT to include

The final report must **not** include:

- Per-reviewer verdict dumps
- Devil's Advocate critique details
- Feedback-loop re-Review procedure or per-iteration state

These remain internal. The user-facing report stays in the two templates above plus the optional fallback tail.

## Step 6 の保存ファイル (`<plan>.design-review.md`)

チャット表示 (上記 2 テンプレート) はこのまま変更しない。加えて、Step 6 完了時に必ず `Write` で保存する。

**パス規則**: Step 0 で解決したプランファイルパスの拡張子直前に `.design-review` を挿入する (例: `feature-x.md` → `feature-x.design-review.md`)。

**保存内容**: チャット表示と同じ本文に加えて、後続のオーケストレータ監査パックが機械参照するための 2 節を追記する (チャットには出さない情報だが、保存ファイルには必須)。

```
<チャット表示と同じ本文 (問題なし route または修正済み route)>

## Fatal 残存

fatal 残存件数: 0

## Acceptable 残存リスク

| 指摘元 | 内容 | 判断根拠 |
|---|---|---|
| DA | <Step 5 最終ラウンドで acceptable と判定された critique> | <grounding / 判定理由> |
| <reviewer name> | <Step 3 で ⚠️ のまま Edit されなかった指摘> | <理由> |
```

- 「Fatal 残存」は Step 5 のフィードバックループが収束した時点の値であり、常に `0` (fatal が残っていればループが継続しているため到達しない)
- 「Acceptable 残存リスク」は Step 5 最終ラウンドの DA acceptable 判定と、Step 3 で ⚠️ のまま残った reviewer 指摘を 1 行 1 件で列挙する。該当が 1 件もない場合も見出し行は残し、本文に「該当なし」と書く (表の有無ではなく行の値で後続が判定できるようにするため)
