# omokawa-skills 開発ガイド

スキル本文を読む場合、前提知識として CONTEXT.md を参照。

## 構成とファイル配置

`plugins/<name>/skills/<name>/` の 2 階層構造を厳守する。

| 種別 | 配置 | discovery |
|---|---|---|
| Skill | `plugins/<name>/skills/<name>/SKILL.md` | 自動 |
| Slash command | `plugins/<name>/commands/<name>.md` | 自動 |
| Sub-agent | `plugins/<name>/skills/<name>/agents/*.md` | skill 本文から `Task` で呼出 |

- `plugin.json` に `skills/commands/agents` 配列を書かない (ファイル構造から自動 discovery)
- agent 定義から skill 内ファイルは `${CLAUDE_PLUGIN_ROOT}/skills/<name>/<file>` で参照する (絶対パスを書かない)

## バケット分類 (説明上のみ)

plugin は README の一覧で engineering / personal / career の 3 バケットに分類する (物理ディレクトリでは分けない。定義は README)。engineering 系は**設定不要で動く**ことを目標にし、設定が必要なら `~/.claude/skills-config/*.md` から読み、なければエラーで止めず**フォールバック**を提示する。career 系はユーザー個人設定が必須。

## 設定値の保管 (グローバル)

機密でないマシンごとのグローバル設定は `~/.claude/skills-config/*.md` (定義は CONTEXT.md)。各 plugin は「このファイルを Read で取得」と SKILL.md に書く。`.env` は使わない (SKILL.md は AI が読む文書なのでシェル変数展開は機能しない)。サンプルは `examples/skills-config/`。

## バージョン bump ルール

plugin の中身 (SKILL.md / `commands/` / sub-agents / `references/`) を変更した PR では、同 PR 内で 3 箇所を揃えて bump する:

1. `plugins/<name>/.claude-plugin/plugin.json` の `version` (minor bump)
2. `marketplace.json` の該当 entry の `version` (1 と同値)
3. `marketplace.json` のトップレベル `version` (minor bump)

patch bump は使わない (typo 修正等は次の minor まで貯める)。破壊的変更時のみ major。commit メッセージは `chore: <変更概要> (vX.Y.Z)`。

tag / GitHub Release は release-on-version-bump.yml が marketplace.json の push から自動生成する。手動 `git tag` / `gh release create` は auto-tag とレースして失敗するので実行しない。「tag が抜けている」症状は常に marketplace.json bump 漏れのサイン。

## 検証

- skill 変更後は `python3 scripts/validate_skills.py` をローカル実行 (CI でも PR ごとに実行)
- 新規 plugin 追加・改名時、機械検証外の 2 点を grep で確認: 他 plugin / README 本文の `/<旧名>` 言及、README のバケット行とリンク
- 公開前に機密情報 (Cloud ID, API キー等) と組織固有名 (ラベル・環境・リポジトリ名) の残存を grep でスキャン
