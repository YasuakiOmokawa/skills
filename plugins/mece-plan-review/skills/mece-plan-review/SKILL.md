---
name: mece-plan-review
description: Use after acceptance criteria exist to check specification and code coverage, update the analysis, and update one plan quality-summary line before implementation. Trigger on "MECE 検証して" or "AC の網羅性を検証して".
---

`## 受け入れ条件` を BB (仕様) / WB (コード) で検証し、tier または Critical 候補に応じて Fresh Red Team を加える。PoC では通常使わない。

## Inputs and tier

1. `$ARGUMENTS` のプラン、なければセッションの Plan File Info を読む。
2. `<plan>.analysis.md` の `## 受け入れ条件` がないか本文が空なら `不足入力: 受け入れ条件 (<絶対 analysis path>) — /define-acceptance-criteria を先に実行` と報告して終了する。
3. [references/init-common.md](references/init-common.md) と [references/ac-enumerate.md](references/ac-enumerate.md) に従い、AC を `AC-N` へ正規化する。列挙結果が0件でも同じ不足入力を報告し、Analyst起動・合成・書き込みをせず終了する。`${CODE_ROOT}` は plan の対象 repo、実装ファイルの共通 Git root、現在の Git root の順で解決する。辿れなければ `(対象コード不在)`。
4. tier は domain 名や「表示のみ」という自己申告ではなく、実際に変更する振る舞いで決める。auth / billing / payment / migration は **deep**、それ以外は **standard**。分析ファイルの `### Tier` が deep でも deep とし、lite は standard と読む。表示だけの変更は、値や認証状態を算出・生成しない場合に限り非リスクとする。

## Evidence boundary

[references/analyst-contract.md](references/analyst-contract.md) の閾値と JSONL 契約を適用する。

- BB は AC、プラン、仕様、公式資料、一般知識だけを使い、コードを読まない。
- WB の finding と判定根拠はコードだけから得る。AC とプランは照合対象と探索位置の特定だけに使い、仕様根拠にはしない。コード不在時は契約の既定に従う。
- Red Team には plan / AC 本文を渡さず、取得済み BB / WB の findings・AC 判定 JSONL と欠落ロール名だけを渡す。
- Critical は欠陥単独で害が成立する契約上の4類型だけ。件数を埋めない。Critical 0 なら MECE OK、1以上なら要修正。不十分 AC は別に改善する。
- 分析ファイルを書くのは main agent だけ。

## Execute

### Standard

main agent が BB と WB を情報源を混ぜず inline 実行する。

- Critical 候補 0: Red Team を省略し、`Critical: 0` と `Red Team skip のため未検出` を記録する。4分類は [references/red-team-checklist.md](references/red-team-checklist.md) を main agent が付与する。
- Critical 候補あり: 取得済み BB / WB の JSONL と欠落ロール名だけで Fresh Red Team を起動し再判定する。
- 分析中にリスク領域が判明したら standard の結果を破棄して deep でやり直す。

### Deep

独立 executor capability があれば BB / WB を同時に委譲し、その後 Fresh Red Team を起動する。委譲 prompt と抽出は [references/dispatch-prompts.md](references/dispatch-prompts.md)。委譲できなければ main agent が各役割を別々に実行し、Red Team 失敗時は [references/synthesis-and-errors.md](references/synthesis-and-errors.md) の fallback を使う。

AC 判定の ID 集合を期待する `AC-1..N` と比較する。不足・重複・未知 ID があれば1回だけ再取得する。期待 ID 行が1件以上残るロールだけ不足・重複行を `言及なし` へ正規化し、0件なら synthetic JSONL を作らず空ロールとする。片側だけ空なら `未取得` 合成、両側空なら合成・書き込み前に停止する (詳細は [references/dispatch-prompts.md](references/dispatch-prompts.md))。

## Output

[references/output-format.md](references/output-format.md) と [references/synthesis-and-errors.md](references/synthesis-and-errors.md) に従う。

1. 取得済み BB / WB JSONL と Red Team 出力を合成し、coverage、severity、4分類、重複、Unknown と理由を単一の `## MECE分析結果` へ upsert する。空ロールの JSONL は生成しない。
2. AC の追加・変更は分析ファイルだけに `[MECE追加]` / `[MECE追加 変更]` で記録する。finding ID をプラン本文へ持ち込まない。
3. プラン本文は変更せず、`## 品質検証` に次の1行だけ追加または更新する。

`- MECE判定: [OK (Critical: 0) or 要修正（Critical N件）] / Important [I]件 (うちAC反映 [R]件) → [分析ファイル名]`

委譲された実行では [references/delegated-execution.md](references/delegated-execution.md) の入力・報告契約も適用する。
