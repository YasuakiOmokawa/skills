---
name: define-acceptance-criteria
description: Fills a matrix of 3 required categories (normal, error, edge) by controlled-vocabulary perspectives to enumerate acceptance criteria into the analysis file. Use when in plan mode before /mece-plan-review, when the user asks to write AC for a plan, or when an AC matrix is needed as MECE input.
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
- AC 行頭は controlled label ([references/perspectives.md](references/perspectives.md)) — 自由形式禁止。**ただし非影響確認カテゴリは例外**で、隣接する既存機能名で記述し controlled label 接頭辞は不要 (label 必須は正常系 / 異常系 / エッジケースの 3 必須カテゴリのみ)
- プラン本文に欠落する仕様を AC で仮置きする場合は末尾に `(仕様確定要)`

## Task complexity tier

実行前に変更規模を判定 → tier を選択 → 該当する scope で AC を作成する:

| Tier | 判定 (OR で 1 つ該当) | 観点軸数 | 必須セル数 | 技術リスク |
|---|---|---|---|---|
| **lite** | 1 ファイル <50 LoC / pure UI・copy・typo・comment / lint-only / config 値変更のみ | 1 軸 | 3 セル | 0-1 件 (省略可) |
| **standard** (default) | 2-5 ファイル / 中規模 feature / 単一 domain | 3 軸 | 9 セル | 3 件 |
| **deep** | 6+ ファイル / multi-domain / auth・billing・payment・DB migration・security config | 5 軸 | 15 セル | 3-5 件 |

**リスク領域** (auth / billing / payment / DB migration / security config) は LoC によらず強制的に **deep**。判定不能なら **standard**。`<plan>.analysis.md` 冒頭の `### Tier` に判定結果と理由を 1 行記録 (例: `Tier: standard (3 files, single domain)`)。

## Quantitative scaffolding (SSOT)

| 項目 | lite | standard | deep |
|---|---|---|---|
| 観点軸数 | 1 軸 | 3 軸 (+ observability 1 軸まで例外) | 5 軸 |
| 必須セル数 | 3 セル | 9 セル | 15 セル |
| 技術リスク件数 | 0-1 件 | 3 件固定 | 3-5 件 |
| 全 tier 共通 | controlled label (`permission` / `observability` / `data_compat` / `req_form` 等) を使用。完全新規 label は 12 文字以内・名詞のみ。`(仕様確定要)` も項目としてカウント可 |

この表は他 references の数量定義に対する canonical。**deep = 5 主軸 + observability 1 軸まで (計 6 軸まで)**、**必須セル数 = 主軸数 × 3** (deep は 15、observability セルは加算・任意)。observability 軸は standard/deep の主軸上限にカウントしない。

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

[references/perspectives.md](references/perspectives.md) の「変更種別 → デフォルト観点軸」表から **3-5 個**選ぶ (下限 3 / 上限 5)。よく使う種別は以下を inline で採用でき、references を開かず median path を完結できる (下表に無い種別・副作用軸・Step B は perspectives.md 参照):

| 変更種別 | 既定 controlled label (上から優先) |
|---|---|
| api_change | `req_form` / `permission` / `compat` |
| db_change / db_or_model_change | `data_compat` / `migration` / `data_volume` |
| auth_change | `permission` / `auth_state` / `user_type` |
| ui_change | `device` / `a11y` / `browser` |
| batch_change | `idempotency` / `data_volume` / `runtime` |
| 全種別 追加候補 | `observability` (主軸数にカウントしない) |

複数主種別での主軸採用 / 副作用軸 1 つ追加 (併用可) / observability 特例 / 表に無い場合の汎用候補軸 (Step B) などの運用詳細は [references/selection-rules.md](references/selection-rules.md) を参照。選定理由を分析ファイル `### 検討観点` に 1 文ずつ明記。

**主軸 / 副作用軸の deterministic classifier**: 変更種別 → デフォルト観点軸表の該当 type 行に現れた controlled label は **主軸**、Step B 汎用候補軸 (`flag_removal` / `non_invasive` / `dep_loc` / `layer` / `contract` 等) と `observability` は **副作用軸**。複数主種別共存時は各 type の最も中心的な 1 label を 1 主軸として採用 (= 副軸格上げ禁止)。

**主軸候補が tier 軸数を超える場合の deterministic ドロップ**: (1) plan の不変条件からセルが空 / 自明になる軸を先にドロップ (例: 「auth 不変・誰でも閲覧可」と明示 → `permission` をドロップ)、(2) plan 本文で明示された関心 (後方互換 / データ量等) に対応する軸は優先的に残す、(3) なお超過するなら表の行順 (上位種別優先) で決める。table-listed label は概念的に cross-cutting に見えても主軸 (例: `compat`) であり副軸格上げ禁止。

**Cross-cutting behaviors の label**: retry / timeout / circuit-breaker などの cross-cutting 挙動が複数 change-type で出現する場合、変更種別表の特定行に閉じ込めず Step B 汎用候補軸として扱う (例: api_change の同期エンドポイントで「リトライ 3 回」なら `idempotency` を Step B 汎用候補軸として副作用軸採用)。

observability を含める場合の実効上限は **6 軸** (主軸 5 + observability 1)。主種別が 3 種類以上の場合は **副作用軸を 1 つに絞る** (合計が上限を超えるのを避けるため)。

### Step 3: 受け入れ条件の生成

必須 3 カテゴリ × 選択観点で全セル充填。**充填確認は (カテゴリ × 各軸) の N×3 セルを 1 つずつ列挙し、各セルが ≥1 項目かを書き出し前に確認する**。執筆は軸を内側ループ (セル起点) で回すと特定軸への偏りを防げる — カテゴリ単位で書くと一部セルが空のまま「総数」だけ満たす漏れが起きる:

- **正常系**: `- [ ] <label>: <入力> → <期待出力>` (「正しく動作する」禁止)
- **異常系**: `- [ ] <label>: <条件> → <HTTP status or エラー文言>`
- **エッジケース**: `- [ ] <label> [境界値: <カテゴリ>]: <条件>` (境界値カテゴリは [references/edge-case-checklist.md](references/edge-case-checklist.md))
- **非影響確認 (推奨)**: `git status --short` 出力で機械判定 — `M` 含む → (a) 手動列挙 or (b) `git diff` 隣接列挙 / `A` のみ → (c) 省略可 / `D` 含む → (a) 必須。詳細は [references/non-impact-rules.md](references/non-impact-rules.md)。**git 実行不能 (plan mode で未着手 / walk-through / dry-run)** の場合は plan 本文の「変更ファイル予定」リストから推測し、判定根拠に `(推定)` を付与する

### Step 4: 技術リスクの生成

リスク 3 件を 3 点セットで記述 (各項目 1 文 = 句点 1 つに収める。理由: 1 項目に複数文を詰めると検証単位が曖昧になり、後続でリスク単位の追跡ができなくなる):
- **何がわからないか**: 主語+述語の 1 文
- **最悪何が起きるか**: 誰に+何が
- **どうやって検証するか**: 実行可能コマンド (`code block`) または手順

### Step 5: 分析ファイルへの書き出し

分析ファイルパス: プランファイルの拡張子前に `.analysis` 挿入 (例: `feature-xxx.md` → `feature-xxx.analysis.md`)。既存なら末尾追記。フォーマット (`/mece-plan-review` との contract、変更禁止) は [references/output-template.md](references/output-template.md) を参照。

### Step 6: プランファイル末尾サマリー

プランファイル末尾の `## 品質検証` セクションに 1 行サマリーを追記 (既存内容は変更しない)。**セクションが存在しない場合**は `---` 区切り + `## 品質検証` ヘッダから新規作成:

```markdown
---

## 品質検証

- AC: <N>観点×必須3カテゴリ + 非影響確認 <K>件 = <M>項目定義済み → <分析ファイル名>
- 技術リスク: <N>件特定済み → <分析ファイル名>
```

**M 算出**: 簡略式 (各セル 1 項目固定) は `M = N × 3 + K`。各セルに複数項目を含む場合は実数表記に分岐 (`AC: M項目定義済み (内訳: 必須X件 + 非影響確認K件)`)。判定: `M == N × 3 + K` なら簡略式、不一致なら実数表記。

**N / X / K の定義**: N = 主軸数 (observability 等の追加軸は N に含めず `+ observability` のように別表記)。X = 正常系 + 異常系 + エッジケースの**実 AC 行数**、K = 非影響確認の**実 AC 行数** (いずれも理論値 N×3 ではなく実カウント)。

## 上流/下流 contract (変更禁止)

| 項目 | 値 |
|---|---|
| 分析ファイルパス | プランファイル拡張子前に `.analysis` 挿入 |
| 必須セクション | `## 受け入れ条件` / `### 正常系` / `### 異常系` / `### エッジケース` / `### 非影響確認` |
| AC 行頭 | 正常系 / 異常系 / エッジケースは `- [ ] <controlled label>: ...` ([references/perspectives.md](references/perspectives.md))。非影響確認は `- [ ] [既存機能名]が...` で label 不要 |
| プラン末尾 | `## 品質検証` 1 行サマリー |

`/mece-plan-review` が AC を `- [ ]` 単位で enumerate するため必須。

## 併用推奨 skill

- `/mece-plan-review` — 本 skill 出力の AC を 3 視点で MECE 検証
- `/finalize-plan` — AC + MECE 結果からブランチ・PR 分割・QA 手順を起こす
