---
name: polish-before-commit
description: コミット前やPR作成前に、プロジェクト規約への準拠とパターン一貫性を確認・修正したい時に使用。
---

# My Code Polish

**提案だけでなく、自動修正まで行う。**

## Arguments

- `$ARGUMENTS`: リファクタ対象のファイルパス（省略可）
  - 指定あり: 指定されたファイルのみをリファクタ
  - 指定なし: `git diff --name-only origin/develop...HEAD` で取得。0件なら終了

## Workflow

### 1. プロジェクト規約の収集

以下のコマンドでプロジェクト内の規約ファイルを列挙し、Read で全件読み込む:

```bash
find . -maxdepth 4 -name "CLAUDE.md" -type f 2>/dev/null
find . -maxdepth 5 -path "*/.claude/rules/*.md" -type f 2>/dev/null
```

ユーザーのグローバル規約 (`~/.claude/CLAUDE.md`) も読み込む。

抽出対象:
- コーディング規約、命名規則、禁止事項、推奨パターン、コメント記載原則

規約ファイルが 0 件、または対象テーマ（命名・エラーハンドリング・コメント等）の記載が無い場合は、該当ステップでのフォールバック挙動を各ステップの指示に従う（下記ステップ 6 参照）。

### 2. 変更ファイルの特定と分類

引数指定時は `$ARGUMENTS` を使用。なければ git diff で取得。

### 3. 処理方式の選択

| 条件 | 処理方式 |
|-----|---------|
| ファイル ≤ 5 | 直接処理（main thread で 1M context を活用） |
| ファイル > 5 かつ 複数言語が混在 | サブエージェント並列（`subagent_type: "general-purpose"`） |

サブエージェントには収集した規約・対象ファイル・`references/pattern-consistency.md` を渡す。

### 4. パターン一貫性チェック

**`references/pattern-consistency.md`** の手法に従い実行:

1. 対象ファイルの既存パターンを分析
2. **同一ファイル内のパターン混在**を検出
3. **類似ファイル間の不整合**を検出（同じコンテキストのファイルと比較）
4. プロジェクト規約との整合性を確認
5. パターンを統一（既存パターンに合わせる）

### 5. 自動修正と検証ループ

修正後は必ず lint を実行し、成功するまで繰り返す（最大3回）。

| 言語 | 検証コマンド |
|-----|-------------|
| Ruby | `bundle exec rubocop ${files} --autocorrect-all` |
| TypeScript/JavaScript | `yarn eslint ${files} --fix` |
| Python | プロジェクトに応じて `ruff check --fix ${files}` または `black ${files}` |
| その他（Go / Rust / Shell 等） | プロジェクト内の `Makefile` / `package.json` / `pyproject.toml` 等から lint タスクを探索。見つからなければ **lint スキップし `[lint: 未定義言語のためスキップ（手動確認要）]` と最終レポートに明記** |

3回試行しても解決しない場合は手動対応として報告。

### 6. コメント改善

ステップ 1 で収集した規約テキストに「コメント」「comment」キーワードを含む節がある場合のみ、その原則に従ってコメントを改善する。

**規約にコメント原則の記載がない場合はこのステップをスキップする**（独自判断でコメントを追加・削除しない）。スキップした旨は最終レポートに `[コメント改善: スキップ（規約に原則なし）]` と明記する。

### 7. 最終レビュー

全ての改善が完了したら、`feature-dev:code-reviewer` で見落としをキャッチ:

```
Task(subagent_type="feature-dev:code-reviewer", prompt="変更ファイルの git diff をレビューし、バグ・規約違反を報告せよ")
```

## Manual Review Items

以下は自動修正せず、提案として報告:

1. **設計判断が必要**: サービス切り出し、モジュール化、責務分離
2. **影響範囲調査が必要**: メソッド名/引数/戻り値の変更
3. **ビジネスロジックのチェックが必要**: バリデーション追加、認可変更

## Quality Standards

- **Accuracy**: 明確に問題であるものだけを修正
- **Safety**: 既存の機能を壊さない
- **Completeness**: 変更されたファイルをすべてチェック
- **Respect**: プロジェクトの規約に従う
