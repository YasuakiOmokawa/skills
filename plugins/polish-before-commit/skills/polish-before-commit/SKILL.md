---
name: polish-before-commit
description: Polishes changed files before commit/PR by enforcing project conventions, pattern consistency, and impl/spec alignment (incl. Ruby dead-mock removal after delegate/def deletion). Use when finalizing a branch, just before `git commit` or `/create-pr`, or whenever the user says "仕上げて" / "polish" / "コミット前チェック".
---

# polish-before-commit

**提案だけでなく、自動修正まで行う。** Step 4 → 5 → 6 → 7 は順序固定、再評価ループ禁止。

## Quick start

1. 引数 `$ARGUMENTS` あり → そのファイルを対象。なし → `git diff --name-only origin/${BASE_BRANCH:-develop}...HEAD` で取得 (0 件なら終了)。
2. 規約を収集 (下記 Workflow Step 1) → Step 2-8 を順に実行。
3. 各 Step の結果を**文言バリアント表に厳密一致**させた最終レポートを返す (silent skip 禁止)。

## Workflow

### 1. 規約の収集

```bash
find . -maxdepth 4 -name "CLAUDE.md" -type f 2>/dev/null
find . -maxdepth 5 -path "*/.claude/rules/*.md" -type f 2>/dev/null
```

加えて `~/.claude/CLAUDE.md` と `~/.claude/rules/*.md` も Read。抽出対象: コーディング規約 / 命名 / 禁止事項 / 推奨パターン / コメント原則。0 件なら以降の各ステップのフォールバック (スキップ + 文言明示) に従う。

### 2. 対象ファイル確定 / 3. 処理方式

Step 2 は Quick start の通り。Step 3: ファイル ≤ 5 は main thread で直接処理、> 5 かつ複数言語混在は `subagent_type: "general-purpose"` で並列 (規約・対象ファイル・`references/pattern-consistency.md` を渡す)。

### 4. パターン一貫性

`references/pattern-consistency.md` の手法に従い、対象ファイルの既存パターン分析 → 同一ファイル内混在検出 → 類似ファイル間不整合検出 → 規約整合性確認 → 既存パターンへ統一。

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

詳細手順・スキップ条件・文言 4 バリアントは **`references/dead-mock-removal.md`** に従う。要旨:

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

## Manual Review Items (自動修正せず提案のみ)

1. 設計判断: サービス切り出し / モジュール化 / 責務分離
2. 影響範囲調査: メソッド名・引数・戻り値の変更
3. ビジネスロジック: バリデーション追加 / 認可変更
4. Dead mock の**部分削除** (`receive_messages(a:, b:)` のうち一部 identifier だけ削除): 書換え候補を併記してユーザー承認後に編集

## 併用推奨 skill

- `/review-code-quality` — 設計レベルの品質課題をコミット前に検出
- `/create-pr` — 仕上げ完了後にカレントブランチから PR を作成
