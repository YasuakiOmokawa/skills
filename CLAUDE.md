# omokawa-skills 開発ガイド

## 文脈把握

スキル本文を読む場合、前提知識として CONTEXT.md を参照。

## ディレクトリ構成

このリポジトリは **monorepo + N plugins** 構造。各 skill / command は独立 plugin として `plugins/<name>/` 配下に配置される。Claude Code の auto-discovery は plugin 内の `skills/<name>/SKILL.md` を 1 階層直下で探すため、以下のレイアウトを厳守する:

```
plugins/<name>/
├── .claude-plugin/plugin.json          # plugin metadata
├── skills/<name>/SKILL.md               # skill 本体 (必須、ある場合)
├── agents/<name>.md                     # top-level agent (該当 plugin のみ)
├── commands/<name>.md                   # slash command (create-pr plugin のみ)
└── skills/<name>/agents/, references/   # sub agent / 参考資料 (skill 内部)
```

`plugins/<name>/skills/<name>/` の 2 階層構造は Claude Code の plugin loader が `${CLAUDE_PLUGIN_ROOT}/skills/` を見るため必要。

## バケット分類 (説明上のみ)

skill を「engineering 系」「personal 系」「career 系」のバケットで**説明上**分類する。物理ディレクトリでは分けない:

- **engineering 系** — 日常の開発作業で使う汎用 plugin (プロジェクト非依存)
- **personal 系** — 環境依存・組織依存の plugin (利用者が自社設定で使う前提、Jira 系など)
- **career 系** — キャリア戦略・ビジョン整合・branding に関わる plugin

`engineering 系` の plugin は **設定不要で動く**ことを目標に作る。設定が必要なものは `~/.claude/skills-config/*.md` から読み込み、なければエラーで止めるのではなく**フォールバック**を提示する。

`career 系` の plugin は **ユーザー個人設定が必須**である点が engineering 系と異なる。

README の plugin 一覧でこの分類を明示し、利用者の理解を助ける。

## ファイル種別と配置

| 種別 | 配置 | discovery |
|---|---|---|
| Skill | `plugins/<name>/skills/<name>/SKILL.md` | 自動 (plugin.json への列挙不要) |
| Slash command | `plugins/<name>/commands/<name>.md` | 自動 |
| Top-level agent | `plugins/<name>/agents/<name>.md` | 自動 (Claude Code plugin install 経由のみ) |
| Sub-agent (skill 内) | `plugins/<name>/skills/<name>/agents/*.md` | skill 本文から `Task` ツールで呼出 |

`plugin.json` には `skills/commands/agents` 配列を**書かない**。Claude Code はファイル構造から自動 discovery する。

### ⚠️ agents は skill 内サブ配置で維持する (npx skills add 互換性)

agent ファイルは **`plugins/<name>/skills/<name>/agents/*.md`** に置く。plugin top-level (`plugins/<name>/agents/`) には**置かない**。

理由は本リポの主 install 経路である `npx skills add YasuakiOmokawa/skills` (vercel-labs/skills CLI) が **plugin top-level の `agents/` を install 対象に含まない**ため。npx skills add は `~/.claude/skills/<name>/` 配下に skill 本体と references を展開するが、plugin top-level の agents/ には触らない。仮に plugin top-level に置くと:

- ❌ npx skills add ユーザー: agent ファイルが install されず、SKILL.md の `Task(subagent_type="<plugin>:<agent>")` が `Agent not found` で失敗
- ✅ Claude Code `/plugin install` ユーザー: 公式 plugin agent system で auto-discovery が機能

本リポは npx skills add を主経路として README に記載しているため、後者を選ぶと前者ユーザーに壊れた skill を配布することになる。PR #30 / #32 で「plugin top-level に移動 + 型付け `subagent_type` 呼び出し」を試したが、npx skills add 互換性が壊れ PR #33 で revert した経緯がある。

`subagent_type="general-purpose"` + agent ファイルを `Read` で inline 読込みパターンが本リポの標準。tools frontmatter による情報源の構造的強制は失われる (= behavioral self-control に依存) が、両 install 経路で動く trade-off を選んだ。将来 vercel-labs/skills が plugin top-level agents をサポートするか、Claude Code plugin install を主経路に切り替えると判断するまで、この配置を維持すること。

## marketplace.json

リポジトリ root の `.claude-plugin/marketplace.json` に全 plugins (現在 22) を列挙。各 entry の `source` は `./plugins/<name>` (相対パス)。配列とディレクトリの一致は CI (validate-skills.yml) が検証する。

新規 plugin を追加する場合は:
1. `plugins/<name>/` ディレクトリと `plugin.json` を作る
2. `marketplace.json` の `plugins` 配列に entry を追加
3. README の該当バケットに行を追加

## バージョン bump ルール

plugin の中身 (SKILL.md / `commands/` / `agents/` / sub-agents / `references/`) を変更した PR では、次の 3 箇所を**同 PR 内で**揃えて bump する:

1. `plugins/<name>/.claude-plugin/plugin.json` の `version` (該当 plugin を minor bump)
2. `.claude-plugin/marketplace.json` の該当 plugin entry の `version` (1 と同じ値に揃える)
3. `.claude-plugin/marketplace.json` のトップレベル `version` (marketplace 全体を minor bump)

patch bump は使わない (typo 修正等の差分は次の minor まで貯める)。破壊的変更時のみ major bump。

commit メッセージは `chore: <変更概要> (vX.Y.Z)` 形式。bump のみの後追い commit は `chore: bump <plugin名> to vX.Y.Z`。

**tag / GitHub Release は自動生成される** (理由: `.github/workflows/release-on-version-bump.yml` が main への marketplace.json push を検知して `v<marketplace 全体 version>` tag と release を作る)。手動で `git tag` / `gh release create` を実行しないこと (auto-tag とレースして "already exists" で失敗する)。"tag が抜けている" 症状は常に "marketplace.json bump が抜けている" のサインなので、bump 漏れを後追いするだけで tag/release も自動で揃う。

## 命名規約

- **動詞ベース**で命名する: `define-acceptance-criteria`, `review-design`, `finalize-plan`, `qa-ui` など
- `self-*` プレフィックスは使わない (誰が使うかではなく**何をするか**を名前で示す)
- 1 plugin 1 skill (または 1 command)。混在させない

## パス参照

agent 定義 (`plugins/<name>/agents/*.md`) から skill 内ファイルを参照する場合:

```markdown
${CLAUDE_PLUGIN_ROOT}/skills/<name>/<file>
```

`${CLAUDE_PLUGIN_ROOT}` は plugin install 先 (`plugins/<name>/`) に解決される。絶対パス `~/.claude/skills/...` を**直接書かない**。

## 設定値の保管 (グローバル)

機密ではない**ユーザーマシンごとのグローバル設定値**は `~/.claude/skills-config/*.md` に書く。全プロジェクト横断で参照される。各 plugin は「このファイルを Read で取得」と SKILL.md に書く。`.env` は使わない (SKILL.md は AI が読む文書なのでシェル変数展開は機能しない)。

サンプルは `examples/skills-config/` 配下。利用者は `bash scripts/setup.sh` で対話生成、または手動でコピー。

## Plugin 間相互参照

plugin 間に依存関係がある場合 (例: `define-acceptance-criteria` → `mece-plan-review` → `finalize-plan`)、SKILL.md の description と本文に `/<相手 plugin 名>` で言及する。`plugin.json` には dependency 定義を書かない (install は user 判断)。

各 SKILL.md には「**併用推奨 skill:**」セクションを設け、関連 plugin を明示する。

## 改名時のチェックリスト

1. `plugins/<name>/` のディレクトリ名
2. `plugins/<name>/.claude-plugin/plugin.json` の `name` フィールド
3. `plugins/<name>/skills/<name>/SKILL.md` の `name:` フィールド
4. 他 plugin / SKILL.md / agent / README からの `/<旧名>` 参照
5. `plugins/<name>/agents/*.md` 内の `${CLAUDE_PLUGIN_ROOT}/skills/<旧名>/` パス
6. `.claude-plugin/marketplace.json` の対応 entry (`name` と `source`)
7. `README.md` のリンク

## 失敗知見の還流と regression 検証

- **Gotchas 還流**: empirical 検証・実利用で executor の失敗を観測したら、該当 skill の SKILL.md (または agent 定義) に `## Gotchas` 節を設けて **1 件 1 行**で追記する (例: qa-ui の ui-evaluator.md)。既に point-of-use の inline 規則として書かれている知見は重複転記しない (DRY 維持 — Gotchas は「決定表や手順に組み込めなかった罠」の置き場)
- **evals/ regression suite**: empirical 検証が収束したら、検証シナリオ + requirements checklist を `plugins/<name>/evals/` に markdown で保存する。skill を変更する PR では、該当 skill の保存済みシナリオを fresh executor で再実行し全 [critical] PASS を確認してから merge する。100% pass に飽和したシナリオは capability 改善の信号としては無価値だが、劣化検出器としては最適 (capability 用途と regression 用途を混同しない)
- **構造検証 CI**: `python3 scripts/validate_skills.py` が PR ごとに CI (validate-skills.yml) で実行され、frontmatter 仕様・references/agents 参照実在・絶対パス混入・marketplace 整合を機械検証する (「改名時のチェックリスト」「公開前チェック」の機械化)。ローカルでも skill 変更後に実行すること

## 公開前チェック

- 機密情報 (Cloud ID, API キー等) が含まれていないか `grep` でスキャン
- 組織固有のラベル名・環境名・リポジトリ名がプレースホルダー化されているか
- `${CLAUDE_PLUGIN_ROOT}` が一貫して使われているか
- 改名時に旧名残存がないか
- marketplace.json の `plugins` 配列と `plugins/` 配下のディレクトリが一致しているか
