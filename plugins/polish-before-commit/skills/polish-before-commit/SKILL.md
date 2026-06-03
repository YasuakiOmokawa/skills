---
name: polish-before-commit
description: Auto-fixes convention and pattern-consistency issues, runs lint, and aggregates remaining judgment calls before stopping for the user. Use when finalizing a branch, just before `git commit` or `/create-pr`, or whenever the user says "仕上げて" / "polish" / "コミット前チェック".
---

# polish-before-commit

**提案だけでなく、自動修正まで行う。** プロジェクト規約・パターン一貫性・impl/spec 整合 (現状 Ruby/RSpec の delegate/def 撤去後 dead-mock 削除のみ、TS/JS/Python は範囲外で skip) を点検し、Step 4 → 5 → 6 → 7 は順序固定で再評価ループ禁止。

**フロー最終段の役割**: この skill は `/simplify` → `/vercel-react-best-practices` → `/review-code-quality` → 本 skill というフローの最後に置かれる。Step 9 で `/review-code-quality` からの申し送り (`.git/quality-review-handoff.md`) と本 skill の Manual Review Items を集約し、**末尾でユーザー判断が必要な項目を一覧提示してから止まる** (連続スキル実行で個別レポートが transcript に埋もれ握りつぶされるのを防ぐため)。

## Task complexity tier

| Tier | 判定 | 実行 Step |
|---|---|---|
| **lite** | 1 ファイル <30 LoC, 規約 hit 0, Ruby delegate/def 撤去なし | Step 5 (lint) + Step 8 (final review) + Step 9 (集約) |
| **standard** (default) | 2-5 ファイル, 規約 hit 1-3 | Step 1-5 + Step 8 + Step 9 (Step 6/7 は条件 hit 時のみ) |
| **deep** | 6+ ファイル / 規約 hit 4+ / Ruby delegate or def 撤去あり / multi-language | 全 Step (1-9) |

**Step 6 (dead-mock 削除)** は Ruby PR で `delegate :X` / `def X` 撤去を含む場合のみ実行 (tier 問わず)。**Step 9 (判断申し送りの集約)** は tier 問わず必ず実行 (フロー最終出力のため lite でも省略不可)。リスク領域 (auth / billing / payment / migration) は LoC によらず **deep**。

## Quick start

1. 引数 `$ARGUMENTS` あり → そのファイルを対象。なし → `git diff --name-only origin/${BASE_BRANCH:-develop}...HEAD` で取得 (0 件なら終了)。
2. 上記 tier 表で実行範囲を確定 → 規約を収集 (下記 Workflow Step 1) → tier 対応 Step を順に実行。
3. 各 Step の結果を**文言バリアント表に厳密一致**させた最終レポートを返す (silent skip 禁止、tier による省略は `[<Step>: tier-{lite,standard,deep} により省略]` を 1 行明示)。最後に Step 9 で `### ⚠️ ユーザー判断が必要な項目` を集約提示し、commit へ進まず判断を仰ぐ。

## Workflow

### 1. 規約の収集

```bash
find . -maxdepth 4 -name "CLAUDE.md" -type f 2>/dev/null
find . -maxdepth 5 -path "*/.claude/rules/*.md" -type f 2>/dev/null
```

加えて `~/.claude/CLAUDE.md` と `~/.claude/rules/*.md` も Read。抽出対象: コーディング規約 / 命名 / 禁止事項 / 推奨パターン / コメント原則。0 件なら以降の各ステップのフォールバック (スキップ + 文言明示) に従う。

**規約 0 件時の分岐**: Step 4 → 既存パターン多数決のみ (規約根拠なしの逸脱検出は行わない、文言 `[パターン一貫性: 違反なし]` を流用) / Step 7 → 即 `[コメント改善: スキップ（規約に原則なし）]` を出力。

### 2. 対象ファイル確定 / 3. 処理方式

Step 2 は Quick start の通り。Step 3: ファイル ≤ 5 は main thread で直接処理、> 5 かつ複数言語混在は `subagent_type: "general-purpose"` で並列 (規約・対象ファイル・[references/pattern-consistency.md](references/pattern-consistency.md) を渡す)。

### 4. パターン一貫性

[references/pattern-consistency.md](references/pattern-consistency.md) の手法に従い、対象ファイルの既存パターン分析 → 同一ファイル内混在検出 → 類似ファイル間不整合検出 → 規約整合性確認 → 既存パターンへ統一。

**4.6 同種違反の網羅確認 (必須)**: 1 ファイルでパターン違反を修正したら、変更ファイル群の他箇所に同じ違反が残っていないか `grep` で網羅確認し、見つけた違反は同時修正する。

- 検査コマンド汎用形: `grep -l '<違反パターン>' $(git diff --name-only origin/${BASE_BRANCH:-develop}...HEAD)`
- Step 5 (lint) が Step 2 で確定した変更ファイル群全体をカバーするため、4.6 で広げた範囲も自動再検証される。

**Step 4 レポート文言** (3 バリアント、いずれかを必ず出力):

| 条件 | 文言 |
|---|---|
| 違反 0 件 | `[パターン一貫性: 違反なし]` |
| 1 ファイル修正 + 他箇所 0 件 | `[パターン一貫性: N 件修正、網羅確認 OK]` |
| 複数ファイル同時修正 | `[パターン一貫性: N 件修正 (うち網羅確認発火 M 件)]` |

### 5. lint 自動修正 (言語別分岐)

| 言語 | コマンド |
|---|---|
| Ruby | `bundle exec rubocop ${files} --autocorrect-all` |
| TypeScript/JavaScript | `yarn eslint ${files} --fix` |
| Python | `ruff check --fix ${files}` または `black ${files}` |
| その他 (Go/Rust/Shell 等) | `Makefile` / `package.json` / `pyproject.toml` から lint タスク探索。なければ `[lint: 未定義言語のためスキップ（手動確認要）]` |

成功するまで最大 3 回繰り返す。3 回試行で解決しなければ手動対応として報告。

**順序保証**: Step 5 の auto-fix 差分は Step 6 / 7 の評価対象に含める (lint 結果を信頼)。Step 4 の再評価はしない。Step 4 → 5 → 6 → 7 で確定、逆順・再評価ループは禁止。

### 6. Dead mock 削除 (Ruby/RSpec)

詳細手順・スキップ条件・文言 4 バリアントは [references/dead-mock-removal.md](references/dead-mock-removal.md) に従う。要旨:

- 対象: impl 側で `delegate :X` / `def X` を撤去した PR の spec 残存 mock (`receive(:X)` / `receive_messages(X:)` / `instance_double(..., X:)` / `double(..., X:)`)。
- スキップ判定の優先順: ① `*.rb` なし / `spec/` なし → 対象外、② 削除 identifier 0 件 → 撤去なし。
- 削除単位: 単独 stub と「全 identifier が削除済の `receive_messages`」は auto、部分削除は Manual Review。
- 削除後は編集 spec 全件を `bundle exec rspec` で 0 failures 確認。失敗時は revert + 報告。

### 7. コメント改善

Step 1 で収集した規約テキストに「コメント」「comment」キーワードを含む節が**ある場合のみ**実施。なければ独自判断で追加・削除しない。

**Step 7 レポート文言** (3 バリアント、いずれかを必ず出力):

| 条件 | 文言 |
|---|---|
| 規約に原則なし | `[コメント改善: スキップ（規約に原則なし）]` |
| 規約あり + 違反なし | `[コメント改善: 違反なし（規約適用済み）]` |
| 規約あり + 修正実施 | `[コメント改善: N 件修正（<規約根拠>準拠）]` (根拠は適用規約のファイル名) |

### 8. 最終レビュー

```
Task(subagent_type="general-purpose", prompt="feature-dev:code-reviewer agent として変更ファイルの git diff をレビューし、バグ・規約違反を報告せよ")
```

Task ツールが使えない (nested 実行) / `feature-dev` plugin 未導入の場合は、main thread で同等のレビュー (変更 diff のバグ・規約違反確認) を直接行い、`[最終レビュー: ... (fallback)]` と明示する (silent skip 禁止)。

**Step 8 レポート文言** (2 バリアント、いずれかを必ず出力):

| 条件 | 文言 |
|---|---|
| 指摘なし | `[最終レビュー: 指摘なし]` |
| 指摘あり | `[最終レビュー: 指摘 N 件 (内訳: バグ X / 規約違反 Y / その他 Z)]` |

### 9. 判断申し送りの集約 (フロー最終 / 全 tier 必須)

このフローの**最終出力**として、ユーザー判断が必要な項目を 1 箇所に集約・提示してから止まる。連続スキル実行で個別レポートが transcript に埋もれ握りつぶされるのを防ぐ。

1. 申し送りファイルを読む:
   ```bash
   HANDOFF="$(git rev-parse --git-dir)/quality-review-handoff.md"
   [ -f "$HANDOFF" ] && cat "$HANDOFF"
   ```
2. ファイル先頭の `branch:` が現在のブランチ (`git branch --show-current`) と一致するもののみ採用。不一致なら stale として除外し `[申し送り: stale (別ブランチ) のため除外]` を 1 行明示。
3. 採用した申し送り項目 + 本 skill の Manual Review Items (下記) を統合し、同一箇所の重複は 1 件にまとめる。
4. 末尾に **`### ⚠️ ユーザー判断が必要な項目`** セクションを出力。各項目は `/abs/path:line` + 要約 + 出所 (review-code-quality 申し送り / polish 検出) + 推奨対応を併記。
5. **ここで自動的に commit / `/create-pr` へ進まない。** 一覧を提示し、どれを今対応するかユーザーの判断を仰ぐ。
6. 提示後、申し送りファイルをクリアする (次フローに stale を持ち越さない): `[ -f "$HANDOFF" ] && rm "$HANDOFF"`

**Step 9 レポート文言** (2 バリアント、いずれかを必ず出力):

| 条件 | 文言 |
|---|---|
| 判断項目 0 件 | `[ユーザー判断項目: なし]` |
| 判断項目あり | `[ユーザー判断項目: N 件 (申し送り X / polish 検出 Y)]` |

## Manual Review Items (自動修正せず提案のみ → Step 9 で集約)

以下は本 skill が検出しても自動修正せず、Step 9 の「ユーザー判断が必要な項目」に集約する:

1. 設計判断: サービス切り出し / モジュール化 / 責務分離
2. 影響範囲調査: メソッド名・引数・戻り値の変更
3. ビジネスロジック: バリデーション追加 / 認可変更
4. Dead mock の**部分削除** (`receive_messages(a:, b:)` のうち一部 identifier だけ削除): 書換え候補を併記してユーザー承認後に編集

## 併用推奨 skill

- `/review-code-quality` — 設計レベルの品質課題を検出し、自動適用しない needs-judgment を本 skill へ申し送る (Step 9 で集約)
- `/create-pr` — Step 9 のユーザー判断が片付いた後にカレントブランチから PR を作成
