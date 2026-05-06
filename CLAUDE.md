# omokawa-skills 開発ガイド

## 文脈把握

スキル本文を読む場合、前提知識としてCONTEXT.mdを参照。

## ディレクトリ構成

Claude Code の自動 discovery が **`skills/<name>/SKILL.md` の 1 階層**しか見ないため、フラット構造を採用する：

```
skills/<name>/SKILL.md      # SKILL.md は必ず 1 階層直下
agents/<name>.md             # エージェント定義は agents/ 直下
commands/<name>.md            # スラッシュコマンドは commands/ 直下にフラット配置
```

サブディレクトリ（`skills/engineering/<name>/` 等）にすると Claude Code が**未認識**になる。これは superpowers / anthropic-agent-skills など Anthropic 公式プラグインで実証されている標準パターン。

## バケット分類（説明上のみ）

スキルを「engineering 系」「personal 系」のバケットで**説明上**分類する。物理ディレクトリでは分けない：

- **engineering 系** — 日常の開発作業で使う汎用スキル（プロジェクト非依存）
- **personal 系** — 環境依存・組織依存のスキル（利用者が自社設定で使う前提）

`engineering 系` のスキルは **設定不要で動く**ことを目標に作る。設定が必要なものは `~/.claude/skills-config/*.md` から読み込み、なければエラーで止めるのではなく**フォールバック**を提示する（例: `core_features` が空なら CLAUDE.md / README.md から推定）。

README のスキル一覧でこの分類を明示し、利用者の理解を助ける。

## ファイル種別と配置

| 種別 | 配置 | discovery |
|---|---|---|
| Skill | `skills/<name>/SKILL.md` (+ `references/`, `agents/`) | 自動（plugin.json への列挙不要） |
| Slash command | `commands/<name>.md` | 自動 |
| Agent | `agents/<name>.md` | 自動 |

`plugin.json` には `skills/commands/agents` 配列を**書かない**。Claude Code はファイル構造から自動 discovery する。

## 命名規約

- **動詞ベース**で命名する：`define-acceptance-criteria`, `review-design`, `finalize-plan`, `qa-ui` など
- `self-*` プレフィックスは使わない（誰が使うかではなく**何をするか**を名前で示す）
- 1スキル1ディレクトリ。SKILL.md 必須、`references/`/`agents/` は必要に応じて

## パス参照

エージェント定義（`agents/*.md`）からスキル内ファイルを参照する場合：

```markdown
${CLAUDE_PLUGIN_ROOT}/skills/<name>/<file>
```

絶対パス `~/.claude/skills/...` を**直接書かない**。プラグイン化されたとき動かなくなる。

## 設定値の保管（グローバル）

機密ではない**ユーザーマシンごとのグローバル設定値**は `~/.claude/skills-config/*.md` に書く。全プロジェクト横断で参照される（プロジェクトを切り替えても同じ設定が効く）。各スキルは「このファイルを Read で取得」と SKILL.md に書く。`.env` はほぼ使わない（SKILL.md は AI が読む文書なのでシェル変数展開は機能しない）。

サンプルは `examples/skills-config/` 配下に置く。利用者は `bash scripts/setup.sh` で対話生成、または手動でコピーして `~/.claude/skills-config/` に配置する。

## スキル間相互参照

スキル間に依存関係がある場合（例: `define-acceptance-criteria` → `mece-plan-review` → `finalize-plan`）、SKILL.md の description と本文に `/<相手スキル名>` で言及する。改名したら全箇所同期更新。

## 改名時のチェックリスト

1. `skills/<name>/` のディレクトリ名
2. `SKILL.md` の `name:` フィールド
3. 他スキル/エージェント/コマンドからの `/<旧名>` 参照
4. `agents/*.md` 内の `${CLAUDE_PLUGIN_ROOT}/skills/<旧名>/` パス
5. `README.md` のリンク

## 公開前チェック

- 機密情報（Cloud ID, API キー等）が含まれていないか `grep` でスキャン
- 組織固有のラベル名・環境名・リポジトリ名がプレースホルダー化されているか
- `${CLAUDE_PLUGIN_ROOT}` が一貫して使われているか
- 改名時に旧名残存がないか
