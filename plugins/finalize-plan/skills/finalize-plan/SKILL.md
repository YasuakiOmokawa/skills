---
name: finalize-plan
description: Turns AC and MECE results from the analysis file into a branch strategy, PR split, and manual/auto QA steps appended to the plan file. Use when the user has completed `/define-acceptance-criteria` + `/mece-plan-review` and is about to move from plan mode into implementation.
---

# finalize-plan

分析ファイル (`<plan>.analysis.md`) から AC・MECE 結果を読み込み、プランファイル末尾に `## 実装準備` (ブランチ・PR 分割・QA 手順) を追記する。入力欠落時は即中断。

## Arguments

- `$ARGUMENTS`: プランファイルパス (省略時は会話コンテキストの `Plan File Info:` から取得、見つからなければ確認)

## Task complexity tier

`<plan>.analysis.md` 冒頭の `### Tier` を継承し、agent の起動範囲を変える:

| Tier | AC 件数 | 想定 PR 数 | branch-planner | pr-splitter | manual-qa-planner | auto-qa-planner |
|---|---|---|---|---|---|---|
| **lite** | ≤5 | 1 | ✓ (簡略) | skip | inline (1 セクション統合) | skip |
| **standard** (default) | 6-15 | 2-3 | ✓ | ✓ | ✓ | ✓ |
| **deep** | >15 / auth / billing / payment / migration | 4+ | ✓ (詳細) | ✓ (詳細) | ✓ | ✓ |

リスク領域は AC 件数によらず **deep**。lite では Step 1.7 の QA-ID enumerate を簡略形 (`QA-N-01`, `QA-N-02`... の通し番号) に縮約してよい。

## Quick start

1. **Step 1**: プランファイルパスを特定
2. **Step 1.5**: 分析ファイルから `## 受け入れ条件` と `## MECE分析結果` を抽出 (両方必須、片方欠落で中断)
3. **Step 1.7**: main agent が AC を QA-ID 形式で 1 回だけ enumerate (`${ENUMERATED_QA_AC}`)
4. **Step 2A** (直列): branch-planner → pr-splitter
5. **Step 2B** (並列、同一メッセージ): manual-qa-planner + auto-qa-planner
6. **Step 3**: 結果を統合してプランファイルに `## 実装準備` を追記

## Workflows

### Step 1.5: 分析ファイル抽出 (片方欠落で即中断)

分析ファイルパス = プランファイルの拡張子前に `.analysis` を挿入 (例: `feature-xxx.md` → `feature-xxx.analysis.md`)。`## 受け入れ条件` と `## MECE分析結果` の**両方**が必要。片方でも欠落なら次のメッセージを表示して中断:

```
⛔ 分析ファイル（{パス}）にACまたはMECE分析結果が見つかりません。
先に /define-acceptance-criteria → /mece-plan-review を実行してください。
```

### Step 1.7: QA-ID enumerate (main agent が 1 回だけ実行)

`${AC_CONTENT}` の各 `- [ ]` 項目を以下の prefix で連番付与し `${ENUMERATED_QA_AC}` として両 planner に渡す:

```
正常系       → QA-H-01, QA-H-02, ...  (Happy)
異常系       → QA-E-01, QA-E-02, ...  (Error)
エッジケース → QA-D-01, QA-D-02, ...  (eDge)
非影響確認   → QA-R-01, QA-R-02, ...  (Regression)
[MECE追加]   → QA-M-01, QA-M-02, ...  (Mece)
```

**0 件カテゴリは ID を発行しない** が Step 3 の対象 AC 行では `0/0` 件数表記を必ず残す (詳細・生成例・fallback は [references/qa-id-enumeration.md](references/qa-id-enumeration.md))。

**[MECE追加] のカウント**: `[MECE追加]` / `[MECE追加 変更]` タグ付き AC は base 4 カテゴリ (正常系 / 異常系 / エッジケース / 非影響確認) **とは別に** QA-M-NN を採番し、`対象AC` 件数の総数に**加算**して扱う。**タグ優先**: AC 本文が `### 正常系` 等のセクション内にインライン配置されていても、`[MECE追加]` タグが section 見出しより優先し QA-M を採番する。例: base 8 件 (3/2/2/1) + MECE追加 1 件 → 対象AC `9項目 (正常系3 / 異常系2 / エッジケース2 / 非影響1 / MECE追加1)`。

### Step 2A → 2B: Agent 実行 (1 直列 + 2 並列)

- **Step 2A 直列**: `branch-planner` → `pr-splitter` (pr-splitter は branch-planner の base ブランチ名を派生に使う)
- **Step 2B 並列**: `manual-qa-planner` + `auto-qa-planner` を**同一メッセージ内**で並列起動。両 planner は再分類せず `${ENUMERATED_QA_AC}` の QA-ID を信頼する

4 agent はいずれも `Task(subagent_type="general-purpose")` で起動し、prompt 冒頭で agent 定義ファイルを Read させる (repo 制約上 typed subagent_type は使わない)。最小レシピ:

```
Task(subagent_type="general-purpose", prompt="""
${CLAUDE_PLUGIN_ROOT}/skills/finalize-plan/agents/<agent>.md を読み込み、以下を基に <成果物> を策定:
## プラン:
${PLAN_CONTENT}
## Enumerated AC:
${ENUMERATED_QA_AC}      # qa planner のみ
## MECE 分析結果:
${MECE_CONTENT}          # qa planner のみ
""")
```

2A は branch-planner → pr-splitter の順 (pr-splitter は `${BRANCH_RESULT}` の base 名を派生に使う)。2B は manual-qa-planner + auto-qa-planner を同一メッセージで並列起動。各 agent 固有 prompt の全文・Task ツール利用不可時の in-context fallback は [references/agent-orchestration.md](references/agent-orchestration.md) 参照。

### Step 3: プランファイルに `## 実装準備` 追記

```markdown
---

## 実装準備

### ブランチ戦略
git checkout -b feature/xxx
命名理由: [理由] / 既存ブランチ確認: [重複なし | 連番付与]

### PR分割計画
| PR | スコープ | ファイル数目安 | 依存 |
|----|----------|----------------|------|
| PR1 | ... | 3-5 | - |
| PR2 | ... | 3-5 | PR1 |

### 手動QA手順
**環境**: {BASE_URL}（QA 実行時にユーザーから取得）
**対象AC**: N項目（正常系X / 異常系Y / エッジケースZ / 非影響W / MECE追加V）（カテゴリ名 canonical は output-template.md SSOT を参照、`エッジ` 単独や `eDge` 不可）
[Chrome DevTools MCP で実行可能な手順]

### 自動QA（テストコード仕様）
[RSpec / Vitest 仕様]
```

完全なテンプレ・PR チェーン図・0 件カテゴリ表記ルール・in-context fallback 時の備考挿入位置は [references/output-template.md](references/output-template.md) 参照。

## Quality standards

- **PR ガイドライン準拠**: ≤2 commits, ≤5 files。この上限は tier 表の「想定 PR 数」より優先する (tier の PR 数は目安であり下限ではない。総ファイル数が少なければ standard でも 1 PR でよい)
- **実行可能性**: Chrome DevTools MCP で実行可能な手動 QA 手順
- **AC トレーサビリティ**: QA-H/E/D/R/M 全項目が手動 QA または自動 QA のいずれかでカバーされている
- **0 件カテゴリ可視化**: 対象 AC 行に `非影響0` のように件数明示 (省略禁止 — 省略すると読み手が「採番漏れ」か「該当ゼロ」かを区別できないため)

## Advanced

- [references/qa-id-enumeration.md](references/qa-id-enumeration.md) — QA-ID 採番ルール詳細・生成例・Step 1.7 失敗時の `QA-X-NN` fallback
- [references/agent-orchestration.md](references/agent-orchestration.md) — 各 agent への Task prompt / 並列メッセージ構成 / Task ツール不可時の in-context 代替モード
- [references/output-template.md](references/output-template.md) — Step 3 出力テンプレ全文 / PR チェーン図 / 0 件カテゴリ表記 / fallback 時の備考行

## 併用推奨 skill

- `/define-acceptance-criteria` — 入力となる AC を定義する (前段)
- `/mece-plan-review` — AC の網羅性を検証してから本スキルに引き継ぐ (前段)
- `/qa-ui` — 実装完了後、本スキルで定めた QA 手順で UI 検証する (後段)
- `/create-pr` — finalize で固めた PR 分割をもとに PR を作成する (後段)
