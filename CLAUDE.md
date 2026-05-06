# omokawa-skills 開発ガイド

## バケット構成

スキルは `skills/` 配下に**バケット**で分類する：

- `engineering/` — 日常の開発作業で使う汎用スキル（プロジェクト非依存）
- `personal/` — 環境依存・組織依存のスキル（公開はするが README/plugin.json から除外しない方針 = 利用者が自社設定で使う前提）

`skills/engineering/` のスキルは **設定不要で動く**ことを目標に作る。設定が必要なものは `docs/agents/*.md` から読み込み、なければエラーで止めるのではなく**フォールバック**を提示する（例: `core_features` が空なら CLAUDE.md / README.md から推定）。

## ファイル種別と配置

| 種別 | 配置 | 配布対象 |
|---|---|---|
| Skill | `skills/<bucket>/<name>/SKILL.md` (+ `references/`, `agents/`) | `plugin.json` の `skills` |
| Slash command | `commands/<name>/<name>.md` | `plugin.json` の `commands` |
| Agent | `agents/<name>.md` | `plugin.json` の `agents` |

## 命名規約

- **動詞ベース**で命名する：`define-acceptance-criteria`, `review-design`, `finalize-plan`, `qa-ui` など
- `self-*` プレフィックスは使わない（誰が使うかではなく**何をするか**を名前で示す）
- バケットは「engineering = 動詞 / personal = 動詞 + 目的語」を緩く守る
- 1スキル1ディレクトリ。SKILL.md 必須、`references/`/`agents/` は必要に応じて

## パス参照

エージェント定義（`agents/*.md`）からスキル内ファイルを参照する場合：

```markdown
${CLAUDE_PLUGIN_ROOT}/skills/<bucket>/<name>/<file>
```

絶対パス `~/.claude/skills/...` を**直接書かない**。プラグイン化されたとき動かなくなる。

## 設定値の保管

機密ではない**プロジェクト共有値**は `docs/agents/*.md` に書く。各スキルは「このファイルを Read で取得」と SKILL.md に書く。`.env` はほぼ使わない（SKILL.md は AI が読む文書なのでシェル変数展開は機能しない）。

## スキル間相互参照

スキル間に依存関係がある場合（例: `define-acceptance-criteria` → `mece-plan-review` → `finalize-plan`）、SKILL.md の description と本文に `/<相手スキル名>` で言及する。改名したら全箇所同期更新。

## 改名時のチェックリスト

1. `skills/<bucket>/<name>/` のディレクトリ名
2. `SKILL.md` の `name:` フィールド
3. 他スキル/エージェント/コマンドからの `/<旧名>` 参照
4. `agents/*.md` 内の `${CLAUDE_PLUGIN_ROOT}/skills/.../<旧名>/` パス
5. `.claude-plugin/plugin.json` のリスト
6. `README.md` のリンク

## 公開前チェック

- 機密情報（Cloud ID, API キー等）が含まれていないか `grep` でスキャン
- 組織固有のラベル名・環境名・リポジトリ名がプレースホルダー化されているか
- `${CLAUDE_PLUGIN_ROOT}` が一貫して使われているか
- 改名時に旧名残存がないか
