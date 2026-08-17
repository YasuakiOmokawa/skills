# Repository context

## Layout

- Skill: `plugins/<name>/skills/<name>/SKILL.md`
- Outcome evaluation: `plugins/<name>/evals/outcomes.md`
- Plugin manifest: `plugins/<name>/.claude-plugin/plugin.json`
- Marketplace manifest: `.claude-plugin/marketplace.json`

Skill、command、agentはファイル配置からdiscoveryされる。plugin manifestへdiscovery配列は書かない。

## Global configuration

非機密のマシン設定は `~/.claude/skills-config/` に置く。

- `jira.md`: personal Jira plugins
- `create-design-doc/dd_template.md` と `dd_reference.md`: 任意。存在しなければ取得済み根拠へ縮退する
- `vision.md`: career pluginに必須

API key、access token、passwordはこの領域へ保存しない。

## Contracts

- Skill入力は自然文と利用可能なtask contextであり、skill固有argument schemaを持たない。
- `apply-findings` の明示的review-only以外にnamed modeを持たない。
- Skillは別skillを暗黙起動せず、必要な後続作業を結果として返す。
- 固定見出し、ID、列、状態値は、skill外のconsumerが実際に読む場合だけmachine contractとする。
- 外部状態の変更と破壊的操作は、正確な対象と変更内容が依頼で承認された場合だけ行う。

## Evaluation

`outcomes.md` は `Trigger`、`Outcome`、`Authorization`、`Hold-out` の4節を持つ。構造は `scripts/validate_skills.py`、振る舞いはfresh executorとblind judgeで検証する。
