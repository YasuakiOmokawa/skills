---
name: define-acceptance-criteria
description: Defines acceptance criteria and technical risks for a plan file. Use when in plan mode before /mece-plan-review, when the user asks to write AC for a plan, or when an AC matrix is needed as MECE input. Writes detail to `<plan>.analysis.md` and a one-line summary to the plan file tail.
---

# define-acceptance-criteria

3 必須カテゴリ × controlled vocabulary 観点 (3-5 個) のマトリクスを埋めて AC を書き出す。詳細は `<plan>.analysis.md` に、サマリーのみプランファイル末尾に追記する。

```
              │ 観点A    │ 観点B    │ 観点C
──────────────┼──────────┼──────────┼──────────
正常系        │ 具体I/O  │ 具体I/O  │ 具体I/O    ← 必須 (全セル ≥1 項目)
異常系        │ Err+HTTP │ Err+HTTP │ Err+HTTP   ← 必須 (全セル ≥1 項目)
エッジケース  │ 境界値   │ 境界値   │ 境界値     ← 必須 (全セル ≥1 項目)
非影響確認    │ 既存A    │ 既存B    │ 既存C      ← 推奨 (a/b/c から選択)
```

- 必須 3 カテゴリの全セル ≥1 項目 (空セル = 検討不足)
- AC 行頭は controlled label ([references/perspectives.md](references/perspectives.md)) — 自由形式禁止
- プラン本文に欠落する仕様を AC で仮置きする場合は末尾に `(仕様確定要)`

## Quick start

シナリオ: 「users API に role 更新を追加」

1. プランファイル読込 → 変更ファイル抽出 ([references/perspectives.md](references/perspectives.md) Step A で `api_change` + `db_change` 判定、テスト/docs/メタは除外)
2. 観点 4 軸選定: `permission` (主軸、auth 文脈) / `req_form` / `data_compat` / `observability`
3. 必須 3 カテゴリ × 4 軸 = 12 セル充填:
   ```markdown
   - [ ] permission: 本人が PATCH /api/users/123 (自分の ID) → 200 OK
   - [ ] req_form: PATCH /api/users/:id without body → 400 Bad Request
   - [ ] permission [境界値: 未ログイン]: PATCH /api/users/:id → 401 Unauthorized
   ```
4. 技術リスク 3 件を 3 点セットで記述
5. 分析ファイル (`<plan>.analysis.md`) に詳細出力 → プランファイル末尾に 1 行サマリー

## Workflow

### Step 1: 初期化 + プランファイル読込

[references/init-common.md](references/init-common.md) に従って初期化 (プランファイル特定 / 分析ファイルパス導出 / リポジトリ名取得)。加えて変更概要・変更ファイル一覧・既存設計内容を抽出。変更ファイル抽出のフォールバック順: プラン本文記述 → `git diff --name-only $(git merge-base HEAD main)..HEAD` → 自然言語類推 → AskUserQuestion。

### Step 1.5: 変更種別の機械判定

[references/perspectives.md](references/perspectives.md) Step A のパスパターン表で機械抽出する。**除外パスパターン**: `spec/`, `test/`, `__tests__/`, `*_test.go`, `*.spec.ts`, `*.md`, `docs/`, `README*`, `CHANGELOG`, `LICENSE`。テスト単独修正は `test_only_change` 扱いか Step B 汎用候補軸に流す。LLM は機械抽出候補を出発点とし、ズレる場合のみ手動補正して分析ファイル `### 検討観点` に「機械抽出: A, B / 追加: C (理由)」と明記。

### Step 2: 観点の選択 (3-5 個)

[references/perspectives.md](references/perspectives.md) の「変更種別 → デフォルト観点軸」表から **3-5 個**選ぶ (下限 3 / 上限 5)。複数主種別での主軸採用 / 副作用軸 1 つ追加 (併用可) / observability 特例 / 表に無い場合の汎用候補軸 (Step B) などの運用詳細は [references/selection-rules.md](references/selection-rules.md) を参照。選定理由を分析ファイル `### 検討観点` に 1 文ずつ明記。

### Step 3: 受け入れ条件の生成

必須 3 カテゴリ × 選択観点で全セル充填:

- **正常系**: `- [ ] <label>: <入力> → <期待出力>` (「正しく動作する」禁止)
- **異常系**: `- [ ] <label>: <条件> → <HTTP status or エラー文言>`
- **エッジケース**: `- [ ] <label> [境界値: <カテゴリ>]: <条件>` (境界値カテゴリは [references/edge-case-checklist.md](references/edge-case-checklist.md))
- **非影響確認 (推奨)**: `git status --short` 出力で機械判定 — `M` 含む → (a) 手動列挙 or (b) `git diff` 隣接列挙 / `A` のみ → (c) 省略可 / `D` 含む → (a) 必須。詳細は [references/non-impact-rules.md](references/non-impact-rules.md)

### Step 4: 技術リスクの生成

リスク 3 件を 3 点セットで記述 (各項目 1 文 = 句点 1 つ厳守):
- **何がわからないか**: 主語+述語の 1 文
- **最悪何が起きるか**: 誰に+何が
- **どうやって検証するか**: 実行可能コマンド (`code block`) または手順

### Step 5: 分析ファイルへの書き出し

分析ファイルパス: プランファイルの拡張子前に `.analysis` 挿入 (例: `feature-xxx.md` → `feature-xxx.analysis.md`)。既存なら末尾追記。フォーマット (`/mece-plan-review` との contract、変更禁止) は [references/output-template.md](references/output-template.md) を参照。

### Step 6: プランファイル末尾サマリー

プランファイル末尾の `## 品質検証` セクションに 1 行サマリーを追記 (既存内容は変更しない):

```markdown
---

## 品質検証

- AC: <N>観点×必須3カテゴリ + 非影響確認 <K>件 = <M>項目定義済み → <分析ファイル名>
- 技術リスク: <N>件特定済み → <分析ファイル名>
```

**M 算出**: 簡略式 (各セル 1 項目固定) は `M = N × 3 + K`。各セルに複数項目を含む場合は実数表記に分岐 (`AC: M項目定義済み (内訳: 必須X件 + 非影響確認K件)`)。判定: `M == N × 3 + K` なら簡略式、不一致なら実数表記。

## 上流/下流 contract (変更禁止)

| 項目 | 値 |
|---|---|
| 分析ファイルパス | プランファイル拡張子前に `.analysis` 挿入 |
| 必須セクション | `## 受け入れ条件` / `### 正常系` / `### 異常系` / `### エッジケース` / `### 非影響確認` |
| AC 行頭 | `- [ ] <controlled label>: ...` ([references/perspectives.md](references/perspectives.md)) |
| プラン末尾 | `## 品質検証` 1 行サマリー |

`/mece-plan-review` が AC を `- [ ]` 単位で enumerate するため必須。

## 併用推奨 skill

- `/mece-plan-review` — 本 skill 出力の AC を 3 視点で MECE 検証
- `/finalize-plan` — AC + MECE 結果からブランチ・PR 分割・QA 手順を起こす
