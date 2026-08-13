---
name: finalize-plan
description: Use when acceptance criteria and MECE review are complete and a plan needs implementation-ready QA preparation immediately before coding, or when asked to add implementation preparation or QA steps to a plan.
---

# finalize-plan

`$ARGUMENTS` はプランファイルパス。`<plan>.analysis.md` の AC・MECE からプラン、`<plan>.qa-ledger.md`、`<plan>.preflight.md` を生成する。

## Tier

分析ファイルの `### Tier` を継承する。未記載は standard。件数は `[MECE追加]` を含む enumerate 対象 AC の総数。auth / billing / payment / migration は件数によらず deep。

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

経路や PoC 文脈による例外はない。分析ファイルの `## 正本抽出結果` は任意入力。プランまたは Read 済み参照先に Figma URL があるのに分析ファイルへ同節がなければ `/extract-figma-spec` を提案し、単独実行では採否を待つ。委譲実行では要人間確認へ加えて続行する。

### 2. QA-ID

main agent が [references/qa-id-enumeration.md](references/qa-id-enumeration.md) に従い AC を一度だけ enumerate する。

### 3. QA planning

tier 表を実行する。lite は main agent が `agents/manual-qa-planner.md` を読み inline 適用する。standard / deep の prompt と fallback は [references/agent-orchestration.md](references/agent-orchestration.md)。

### 4. プラン追記

planner 出力を統合し、プラン末尾へ `## 実装準備` を追記する。書式は [references/output-template.md](references/output-template.md)。

manual の各 `出典:` は enumerate 元 AC 原文を保持する。対応しない QA-ID は統合せず要人間確認へ加える。

### 5. 正本カバレッジ

Step 4 の Write 後、分析ファイルに `## 正本抽出結果` 見出しがなければ [references/output-template.md](references/output-template.md) の skip 行を記録する。見出しがあれば内容が空でも [references/coverage-gate-bash.md](references/coverage-gate-bash.md) をプラン自体へ実行する。

未カバー atom の期待値を既存 manual 項目の確認本文が完全に検証していれば、AC原文を残したまま `出典: <atom ID>` を追加する (`出典: <AC原文> / 出典: <atom ID>`。atom ごとにラベルを繰り返す)。それ以外は enumerate 済み ID とプラン内 ID の最大 QA-M 連番を継続し、期待値原文と `出典: <atom ID>` を持つ新規 QA-M を manual へ追加する。補完後は再実行して差分ゼロを確認する。

記録書式と位置は output template に従う。既存行は置換する。補完 QA-M は ledger 対象へ加えるが、Step 2 由来の `対象AC` 件数には加えず coverage 行だけに計上する。

### 6. QA ledger

Step 2 の全 QA-ID と Step 5 の補完 ID の和集合から [references/qa-ledger.md](references/qa-ledger.md) を初期化する。

### 7. Preflight

プランから [references/preflight.md](references/preflight.md) を生成する。不在なら6行を新規作成し、既存なら欠損行だけ追加する。解決不能値は artifact に `未定` として残す。

## 委譲実行

AskUserQuestion の有無と Task の有無で判定し、実行主体名では推測しない。

- プランパス: `$ARGUMENTS` → 起動 prompt の明示パス。`Plan File Info:` は単独実行だけで使う。解決不能なら探索・推測・Write をせず `不足入力: プランファイルパス` で即終了。
- AskUserQuestion 不可: 分類不能、preflight 未定、要人間確認を質問せず最終報告へ列挙。
- Task 不可: [references/agent-orchestration.md](references/agent-orchestration.md) の in-context fallback。subagent であること自体は fallback 条件ではない。
- `${CLAUDE_PLUGIN_ROOT}`: この SKILL.md の所在から skill root の絶対パスへ解決してから nested prompt / Read に渡す。

## 完了報告

次を列挙する。

- Write したプラン、ledger、preflight の絶対パス
- coverage gate 結果
- ledger 割当結果の auto / manual / orphan 件数
- preflight の `未定`、QA-X、orphan、AC不一致、Figma未抽出を含む要人間確認項目
