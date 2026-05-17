# 初期化処理 (define-acceptance-criteria / mece-plan-review 共通)

このファイルは両 skill で共通する初期化手順をまとめたもの。**両 plugin の `references/init-common.md` に同内容で重複配置している** (plugin self-containment の制約上、cross-plugin file sharing ができないため)。**内容を変更する場合は両方を同時に更新すること** (sync 義務)。

## プランファイル特定

引数からプランファイルパスを取得する:

- `$ARGUMENTS` が指定されていればそれを使用
- 省略時はシステムプロンプトの `Plan File Info:` セクションからパスを取得

ファイル全文を Read で読み込む。

## 分析ファイルパス導出

プランファイルの拡張子前に `.analysis` を挿入したパスを使用する:

- 例: `~/.claude/plans/feature-xxx.md` → `~/.claude/plans/feature-xxx.analysis.md` (プランファイルは `~/.claude/plans/` 配下を推奨)

両 skill で同じ規約を使うことで、`/define-acceptance-criteria` で書き出した分析ファイルが `/mece-plan-review` でそのまま参照可能になる。

## リポジトリ名取得

```bash
git remote get-url origin | sed 's/.*github.com[:/]\(.*\)\.git/\1/'
```

- 成功時: `<org>/<repo>` 形式で `${REPO_NAME}` として保持
- 失敗時 (non-git リポジトリ): `${REPO_NAME}` を `"unknown-repo"` として継続。Devin wiki 依存処理は `[non-git: Devin 未使用]` でスキップ

## 各 skill 固有の追加処理

### define-acceptance-criteria
- 分析ファイルが存在しなければ新規作成
- 既存の場合は末尾に追記 (重複セクションには注意)

### mece-plan-review
- 分析ファイルから `## 受け入れ条件` セクションを抽出 (なければ即座に中断)
- AC 項目を `- [ ]` 単位で enumerate して `AC-1, AC-2, ...` の序数を付与
- 関連リポジトリ取得 (`gh repo list <ORG>` で Wiki Researcher 用)
