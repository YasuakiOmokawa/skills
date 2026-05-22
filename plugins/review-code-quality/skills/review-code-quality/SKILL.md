---
name: review-code-quality
description: Detects two tiers of issues. Tier 1 (always-on, 3 観点): design-level cohesion / coupling / readability issues that RuboCop/ESLint miss. Tier 2 (conditional, business-impact 観点 — runs only when the diff updates a domain model attribute such as plan_code / role / status, otherwise reports `skip`): 2-stage business side-effect chains like feature-flag revival or auth bypass. Use when finishing self-review of an implementation, before requesting PR review, or when a diff updates a domain model attribute.
---

# Review Code Quality

**提案のみ行い、自動修正は行わない。**

4 観点 (凝集度 / 結合度 / 可読性 / 業務副作用 chain) を専用 agent で分析し、統合レポートを出力する。

## Quick start

1. `$ARGUMENTS` 指定があればそのファイル、なければ `git diff --name-only origin/develop...HEAD` で対象を確定。0 件なら終了
2. 処理方式を選ぶ (詳細: [references/execution.md](references/execution.md)):
   - ファイル ≤ 2 → **main thread で 4 観点を順次分析**
   - ファイル > 2 かつ Task 使用可 → **4 agent 並列** (同一メッセージ内に Task 4 つ)
   - ファイル > 2 かつ Task 使用不可 (nested 実行) → **main thread fallback** + 冒頭で fallback 理由を明示
3. 4 agent **すべての結果を受信してから**統合分析を開始 (部分結果先行禁止)
4. 統合レポートを出力 (詳細: [references/integration-output.md](references/integration-output.md))

## Workflows

### Step 1: 対象ファイルの特定

引数指定時は `$ARGUMENTS` を使用。なければ `git diff --name-only origin/develop...HEAD` で取得。0 件なら終了。

### Step 2: Quality Analysis

[references/execution.md](references/execution.md) の「処理方式の選択」表に従って分岐する。

- **Task 使用可否の自己判定**: 本 skill が他 subagent から呼ばれている (nested 実行) 場合、Task ツールは使用不可とみなす。Task を試行して失敗を確認する必要はない。判定基準は references/execution.md を参照
- **4 agent**: cohesion / coupling / readability / business-impact (`agents/*.md`)
- **business-impact-analyzer の skip 条件**: 対象 diff に domain model attribute (plan_code / role / status 等) の更新が含まれない場合、最低件数を満たさず skip 報告で終了してよい
- 並列実行の agent 起動プロンプトテンプレ・観点と reference の対応表・指摘件数ルール (最低 3 件 / 50 行未満の escape hatch 等) は [references/execution.md](references/execution.md) を参照

### Step 3: 統合分析

**前提**: Step 2 で起動した 4 agent (並列実行モード) の**すべての結果を受信してから** Step 3 を開始する (部分結果での先行実行は禁止、root cause 集約の前提が崩れるため)。main thread 代替実行の場合は 4 観点を順次完了してから本ステップへ進む。

business-impact-analyzer の **skip 報告も統合レポートに残す**。

手順 (根本原因の特定 → 優先度判定 → レポート出力)、重大度表、出力ルール (アイコンは該当時のみ / サマリーは 0 件含めて全表示 / 指摘は `/abs/path:line_number` 形式) とレポートテンプレは [references/integration-output.md](references/integration-output.md) を参照。

## Advanced features

- 実行モード (並列 / main thread fallback) と Task 自己判定、指摘件数ルール: [references/execution.md](references/execution.md)
- 重大度・統合手順・レポート出力ルール: [references/integration-output.md](references/integration-output.md)
- 各観点の検出基準: [references/cohesion.md](references/cohesion.md) / [references/coupling.md](references/coupling.md) / [references/readability.md](references/readability.md) / [references/business-impact.md](references/business-impact.md)

## 併用推奨 skill

- `/polish-before-commit` — 検出された問題を踏まえてコミット前の最終仕上げを行う
- `/qa-ui` — コード品質と並行して実装後 UI を検証する
