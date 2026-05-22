---
name: finalize-plan
description: Finalizes a confirmed plan by reading AC/MECE results from the analysis file, enumerating per-category QA-IDs (QA-H/E/D/R/M), and appending branch, PR-split, and QA procedures to the plan file. Use when the user has completed `/define-acceptance-criteria` + `/mece-plan-review` and is about to move from plan mode into implementation.
---

# finalize-plan

分析ファイル (`<plan>.analysis.md`) から AC・MECE 結果を読み込み、プランファイル末尾に `## 実装準備` を追記する。入力欠落時は即中断。

## Arguments

- `$ARGUMENTS`: プランファイルパス (省略時は会話コンテキストの `Plan File Info:` から取得、見つからなければ確認)

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

**0 件カテゴリは ID を発行しない** が Step 3 の対象 AC 行では `0/0` 件数表記を必ず残す (詳細・生成例・fallback は `references/qa-id-enumeration.md`)。

### Step 2A → 2B: Agent 実行 (1 直列 + 2 並列)

- **Step 2A 直列**: `branch-planner` → `pr-splitter` (pr-splitter は branch-planner の base ブランチ名を派生に使う)
- **Step 2B 並列**: `manual-qa-planner` + `auto-qa-planner` を**同一メッセージ内**で並列起動。両 planner は再分類せず `${ENUMERATED_QA_AC}` の QA-ID を信頼する

各 agent への Task prompt テンプレ、Task ツール利用不可時の in-context fallback は `references/agent-orchestration.md` 参照。

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

完全なテンプレ・PR チェーン図・0 件カテゴリ表記ルール・in-context fallback 時の備考挿入位置は `references/output-template.md` 参照。

## Quality standards

- **PR ガイドライン準拠**: ≤2 commits, ≤5 files
- **実行可能性**: Chrome DevTools MCP で実行可能な手動 QA 手順
- **AC トレーサビリティ**: QA-H/E/D/R/M 全項目が手動 QA または自動 QA のいずれかでカバーされている
- **0 件カテゴリ可視化**: 対象 AC 行に `非影響0` のように件数明示 (省略禁止)

## Advanced features

- 分析ファイル契約と中断メッセージの正確な文面: 上記 Step 1.5 と中断ブロックを参照
- QA-ID 採番ルール詳細・生成例・Step 1.7 失敗時の `QA-X-NN` fallback: `references/qa-id-enumeration.md`
- 各 agent への Task prompt / 並列メッセージ構成 / Task ツール不可時の in-context 代替モード: `references/agent-orchestration.md`
- Step 3 出力テンプレ全文 / PR チェーン図 / 0 件カテゴリ表記 / fallback 時の備考行: `references/output-template.md`

## 併用推奨 skill

- `/define-acceptance-criteria` — 入力となる AC を定義する (前段)
- `/mece-plan-review` — AC の網羅性を検証してから本スキルに引き継ぐ (前段)
- `/qa-ui` — 実装完了後、本スキルで定めた QA 手順で UI 検証する (後段)
- `/create-pr` — finalize で固めた PR 分割をもとに PR を作成する (後段)
