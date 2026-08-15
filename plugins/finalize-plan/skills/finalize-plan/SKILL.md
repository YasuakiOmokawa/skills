---
name: finalize-plan
description: Use after a plan's acceptance criteria and MECE analysis are complete, immediately before implementation.
---

`$ARGUMENTS` はプランファイルパス。`<plan>.analysis.md` の AC・MECE からプラン、`<plan>.qa-ledger.md`、`<plan>.preflight.md` を生成する。

## Tier

優先順は auth/billing/payment/migration → deep、分析ファイルの `### Tier`、未記載時は `[MECE追加]` を含む AC 件数。件数でも決まらなければ standard。

| Tier | AC | Manual planner | Auto planner |
|---|---:|---|---|
| lite | ≤5 | main agent が inline | skip |
| standard | 6–15 | dispatch | dispatch |
| deep | >15 / risk | dispatch | dispatch |

PR 分割・ブランチ設計は行わない。

## Workflow

### 1. 入力

プランパスは `$ARGUMENTS` → `Plan File Info:` → user confirmation の順で得る。分析ファイルは拡張子前へ `.analysis` を挿入する。

分析ファイルに本文を持つ `## 受け入れ条件` と `## MECE分析結果` の両方が必要。不在・空・片方欠落なら停止する。

```text
⛔ 分析ファイル（{パス}）にACまたはMECE分析結果が見つかりません。
先に /define-acceptance-criteria → /mece-plan-review を実行してください。
```

PoC 例外はない。`## 正本抽出結果` は任意。プランが参照するローカル Markdown を1 hop読み、Figma URLがあるのに同節がなければ `/extract-figma-spec` を提案する。単独実行では採否を待ち、委譲実行では要人間確認へ加えて続行する。

### 2. QA-ID

[references/qa-id-enumeration.md](references/qa-id-enumeration.md) に従い AC を一度だけ enumerate し、`mktemp -d` で作る `RUN_DIR/enumerated_qa_ids.txt` に全 QA-ID を1行1件で保存する。Step 6 後に削除する。

### 3. QA planning

tier 表を実行する。lite は main agent が `agents/manual-qa-planner.md` を読み inline 適用する。standard / deep の prompt と fallback は [references/agent-orchestration.md](references/agent-orchestration.md)。

### 4. プラン追記

planner 出力を統合し、プランの `## 実装準備` を upsert する。既存節は最初の完全一致見出しから次の `## ` 見出し直前または EOF までを置換し、直前に空行だけを挟んだ `---` があればそれも置換範囲へ含める。同名の重複節と付随 separator は削除し、1節・separator 1本だけ保持する。書式は [references/output-template.md](references/output-template.md)。

manual の各 `出典:` は enumerate 元 AC 原文を保持する。対応しない QA-ID は統合せず要人間確認へ加える。

### 5. 正本カバレッジ

Step 4 の Write 後、分析ファイルに `## 正本抽出結果` がなければ [references/output-template.md](references/output-template.md) の skip 行をプランへ記録する。見出しがあれば空でも、[references/coverage-gate-bash.md](references/coverage-gate-bash.md) の `ANALYSIS_FILE` に分析ファイル、`PLAN_FILE` にプランを指定して実行する。終了値は `0=pass/skip`、`1=未カバー`、`2=構造エラー`。`2` は `RUN_DIR` を削除し、補完・Step 6-7・成功報告を行わず未完了として停止する。

未カバー atom を既存 manual の確認本文が完全に検証していれば、元の `出典: <AC原文>` を保ち、その QA ブロックへ atom ごとに `**正本出典: <atom ID>**` を追加する。それ以外は enumerate 済み ID とプラン内 ID の最大 QA-M 連番を継続し、期待値原文と atom 出典を持つ QA-M を追加する。補完はこの1回だけ行い、gate を1回だけ再実行する。なお未カバーなら追加補完・再試行をせず、atom ID を coverage 行と完了報告に残して未完了とする。Step 6-7 は続行する。

記録位置・書式は output template に従い既存行を置換する。補完 QA-M は ledger に加えるが、Step 2 の `対象AC` 件数には加えず coverage 行だけに計上する。

### 6. QA ledger

Step 2 の全 QA-ID と Step 5 の補完 ID の和集合から [references/qa-ledger.md](references/qa-ledger.md) を作る。ordered `(QA-ID, 手段, exact source)` の fingerprint を `## 実装準備` marker と ledger generation に記録する。fingerprint が変われば全 current assignments を pending にした新 generation を追記し、同じなら新規 `(QA-ID, 手段)` だけ追記する。その後 `RUN_DIR` を削除する。

### 7. Preflight

プランから [references/preflight.md](references/preflight.md) を生成する。現在の6候補値の fingerprint が既存 marker と同じなら user 更新を含む artifact を保持する。異なるか marker が無ければ6行を現在値 (`未定` 含む) で置換し marker を更新する。

## 委譲実行

同期的な質問と独立 executor dispatch の可否で判定する。

- パスは `$ARGUMENTS` → 起動 prompt。`Plan File Info:` は単独実行だけで使い、未解決なら探索・推測・Write なしで `不足入力: プランファイルパス` と終了する。
- 同期質問不可なら分類不能・preflight 未定・要人間確認を最終報告へ列挙する。
- dispatch 不可なら [references/agent-orchestration.md](references/agent-orchestration.md) の in-context fallback を使う。実行主体名は判定材料にしない。
- nested prompt / Read の skill root は、この SKILL.md の所在から絶対パスへ解決する。

## 完了報告

- Write したプラン、ledger、preflight の絶対パス
- coverage gate 結果
- ledger 割当結果の auto / manual / orphan 件数
- preflight の `未定`、QA-X、orphan、AC不一致、Figma未抽出を含む要人間確認項目
