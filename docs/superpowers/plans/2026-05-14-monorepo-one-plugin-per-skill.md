# omokawa-skills を 1 plugin 1 skill 構造へ再編 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `omokawa-skills` モノリス plugin を 14 個の独立 plugin (13 skills + 1 command) に分割し、ユーザーが選択的に install できるようにする。

**Architecture:** monorepo + marketplace.json で N plugins を列挙する方式。各 plugin は `plugins/<name>/` 配下に独立配置し、独自の `.claude-plugin/plugin.json` を持つ。`${CLAUDE_PLUGIN_ROOT}` の相対構造は不変なので既存 skill 本文・agent 参照は変更不要。旧 `omokawa-skills` plugin は即時廃止。

**Tech Stack:** Bash (git mv), JSON (plugin.json/marketplace.json), Markdown (SKILL.md/CLAUDE.md/README.md)

**Spec:** `docs/superpowers/specs/2026-05-14-monorepo-one-plugin-per-skill-design.md`

---

## File Structure (After Migration)

```
omokawa-skills/
├── .claude-plugin/marketplace.json       # 14 plugins 列挙
├── plugins/
│   ├── define-acceptance-criteria/
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/define-acceptance-criteria/SKILL.md
│   ├── mece-plan-review/                 # + references/
│   ├── finalize-plan/                    # + agents/ (top + sub), + sub-skill agents
│   ├── review-design/                    # + agents/ (top + sub), + references/
│   ├── review-code-quality/              # + agents/ (top + sub), + references/
│   ├── polish-before-commit/             # + agents/ (top), + references/
│   ├── model-data/                       # + sub agents/, + references/
│   ├── map-user-stories/                 # + references/
│   ├── qa-ui/                            # + sub agents/
│   ├── create-jira-issues/
│   ├── set-jira-story-points/
│   ├── translate-to-vision-story/        # + references/, + examples/
│   ├── dry-ssot-text/
│   └── create-pr/                        # command-only
│       ├── .claude-plugin/plugin.json
│       └── commands/create-pr.md
├── scripts/setup.sh                      # 変更不要
├── scripts/link-*.sh                     # 新レイアウト対応に更新
├── examples/skills-config/               # 変更不要
├── CLAUDE.md                             # 全面改訂
├── CONTEXT.md                            # 軽微更新
├── README.md                             # 全面改訂
├── CHANGELOG.md                          # 2.0.0 BREAKING 追記
└── docs/superpowers/                     # 既存 spec/plan
```

**ファイル責務:**

- `plugins/<name>/.claude-plugin/plugin.json` — 各 plugin のメタデータ (name/description/version/keywords)
- `plugins/<name>/skills/<name>/SKILL.md` — skill 本体 (既存をそのまま移動)
- `plugins/<name>/agents/<name>.md` — top-level agent (該当する 4 plugin のみ、既存をそのまま移動)
- `.claude-plugin/marketplace.json` — 14 plugins を `source: "./plugins/<name>"` で列挙

---

## Per-Plugin Metadata Reference

各 plugin の `plugin.json` 作成時に使用するメタデータ。description は既存 SKILL.md frontmatter からそのまま転記する。

| Plugin | Has top-level agent | category | keywords |
|---|---|---|---|
| define-acceptance-criteria | no | productivity | `["acceptance-criteria", "plan-driven", "qa"]` |
| mece-plan-review | no | productivity | `["mece", "plan-driven", "qa", "code-review"]` |
| finalize-plan | yes | productivity | `["plan-driven", "branch", "pr-split", "qa"]` |
| review-design | yes | productivity | `["code-review", "clean-architecture", "ddd", "hexagonal"]` |
| review-code-quality | yes | productivity | `["code-review", "cohesion", "coupling", "readability"]` |
| polish-before-commit | yes | productivity | `["code-review", "linting", "commit"]` |
| model-data | no | productivity | `["er-diagram", "dbml", "database-design", "sql"]` |
| map-user-stories | no | productivity | `["user-stories", "story-mapping", "plan-driven", "jira"]` |
| qa-ui | no | productivity | `["qa", "ui-testing", "chrome-devtools"]` |
| create-jira-issues | no | productivity | `["jira", "atlassian", "ticket"]` |
| set-jira-story-points | no | productivity | `["jira", "atlassian", "story-points"]` |
| translate-to-vision-story | no | personal | `["career", "branding", "writing", "zenn"]` |
| dry-ssot-text | no | productivity | `["writing", "refactoring", "documentation"]` |
| create-pr | no | productivity | `["pr", "github", "conventional-commits"]` |

---

## Phase 1: Pre-Migration Setup

### Task 1: Pre-flight check and scaffolding

**Files:**
- Create: `plugins/` (empty directory)

- [ ] **Step 1: Confirm clean working tree**

```bash
git status
```

Expected: `nothing to commit, working tree clean` (or only contains in-progress plan/spec docs)

- [ ] **Step 2: Confirm spec is committed**

```bash
git log --oneline -3 -- docs/superpowers/specs/
```

Expected: shows the spec commit `0419965` or equivalent.

- [ ] **Step 3: Create plugins/ directory**

```bash
mkdir -p plugins
```

- [ ] **Step 4: Create migration branch**

```bash
git switch -c feat/one-plugin-per-skill
```

- [ ] **Step 5: Verify directory exists**

```bash
ls -d plugins
```

Expected: `plugins`

---

## Phase 2: Migrate Skills to Individual Plugins

各タスクは以下のパターンに従う:
1. `mkdir -p plugins/<name>/.claude-plugin`
2. plugin.json を書く
3. `git mv skills/<name> plugins/<name>/skills/<name>`
4. (該当する場合) `git mv agents/<name>.md plugins/<name>/agents/<name>.md`
5. 構造を検証 (ls + jq)
6. commit

### Task 2: Migrate define-acceptance-criteria

**Files:**
- Create: `plugins/define-acceptance-criteria/.claude-plugin/plugin.json`
- Move: `skills/define-acceptance-criteria/` → `plugins/define-acceptance-criteria/skills/define-acceptance-criteria/`

- [ ] **Step 1: Create plugin directory**

```bash
mkdir -p plugins/define-acceptance-criteria/.claude-plugin
```

- [ ] **Step 2: Write plugin.json**

```json
{
  "name": "define-acceptance-criteria",
  "description": "プランモード中にプランファイルの受け入れ条件・技術リスクを定義する時に使用。詳細は分析ファイル（`<plan>.analysis.md`）に書き出し、プランファイル末尾には品質検証サマリーのみ追記する。/mece-plan-reviewの前に実行し、MECEの検証ターゲットを定義する。",
  "version": "0.1.0",
  "author": { "name": "Yasuaki Omokawa", "url": "https://github.com/YasuakiOmokawa" },
  "homepage": "https://github.com/YasuakiOmokawa/skills",
  "repository": "https://github.com/YasuakiOmokawa/skills",
  "license": "MIT",
  "keywords": ["acceptance-criteria", "plan-driven", "qa"]
}
```

- [ ] **Step 3: Move skill directory**

```bash
git mv skills/define-acceptance-criteria plugins/define-acceptance-criteria/skills/define-acceptance-criteria
```

- [ ] **Step 4: Verify structure**

```bash
ls plugins/define-acceptance-criteria/skills/define-acceptance-criteria/SKILL.md
jq . plugins/define-acceptance-criteria/.claude-plugin/plugin.json
```

Expected: SKILL.md path exists; jq prints valid JSON.

- [ ] **Step 5: Commit**

```bash
git add plugins/define-acceptance-criteria
git commit --no-verify -m "feat: migrate define-acceptance-criteria to standalone plugin"
```

---

### Task 3: Migrate mece-plan-review

**Files:**
- Create: `plugins/mece-plan-review/.claude-plugin/plugin.json`
- Move: `skills/mece-plan-review/` → `plugins/mece-plan-review/skills/mece-plan-review/`

- [ ] **Step 1: Create plugin directory**

```bash
mkdir -p plugins/mece-plan-review/.claude-plugin
```

- [ ] **Step 2: Write plugin.json**

```json
{
  "name": "mece-plan-review",
  "description": "プランファイルの受け入れ条件（AC）に対しMECE完全性検証を実施し、ユースケース漏れ・技術的対応漏れ・ACの改善点を検出して分析ファイルに記録する。プランにACが定義済みで実装前にMECE検証が必要な時に使用。事前に /define-acceptance-criteria でACを定義しておくこと。",
  "version": "0.1.0",
  "author": { "name": "Yasuaki Omokawa", "url": "https://github.com/YasuakiOmokawa" },
  "homepage": "https://github.com/YasuakiOmokawa/skills",
  "repository": "https://github.com/YasuakiOmokawa/skills",
  "license": "MIT",
  "keywords": ["mece", "plan-driven", "qa", "code-review"]
}
```

- [ ] **Step 3: Move skill directory**

```bash
git mv skills/mece-plan-review plugins/mece-plan-review/skills/mece-plan-review
```

- [ ] **Step 4: Verify and commit**

```bash
ls plugins/mece-plan-review/skills/mece-plan-review/SKILL.md
jq . plugins/mece-plan-review/.claude-plugin/plugin.json
git add plugins/mece-plan-review
git commit --no-verify -m "feat: migrate mece-plan-review to standalone plugin"
```

---

### Task 4: Migrate finalize-plan (with top-level agent)

**Files:**
- Create: `plugins/finalize-plan/.claude-plugin/plugin.json`
- Move: `skills/finalize-plan/` → `plugins/finalize-plan/skills/finalize-plan/`
- Move: `agents/finalize-plan.md` → `plugins/finalize-plan/agents/finalize-plan.md`

- [ ] **Step 1: Create plugin directory**

```bash
mkdir -p plugins/finalize-plan/.claude-plugin plugins/finalize-plan/agents
```

- [ ] **Step 2: Write plugin.json**

```json
{
  "name": "finalize-plan",
  "description": "プランモードで設計が確定した後、実装に移る直前に使用。分析ファイルからAC・MECE結果を読み込み、プランファイルにブランチ・PR分割・QA手順を追記する。",
  "version": "0.1.0",
  "author": { "name": "Yasuaki Omokawa", "url": "https://github.com/YasuakiOmokawa" },
  "homepage": "https://github.com/YasuakiOmokawa/skills",
  "repository": "https://github.com/YasuakiOmokawa/skills",
  "license": "MIT",
  "keywords": ["plan-driven", "branch", "pr-split", "qa"]
}
```

- [ ] **Step 3: Move skill + top-level agent**

```bash
git mv skills/finalize-plan plugins/finalize-plan/skills/finalize-plan
git mv agents/finalize-plan.md plugins/finalize-plan/agents/finalize-plan.md
```

- [ ] **Step 4: Verify and commit**

```bash
ls plugins/finalize-plan/skills/finalize-plan/SKILL.md plugins/finalize-plan/agents/finalize-plan.md
jq . plugins/finalize-plan/.claude-plugin/plugin.json
git add plugins/finalize-plan
git commit --no-verify -m "feat: migrate finalize-plan to standalone plugin"
```

---

### Task 5: Migrate review-design (with top-level agent)

**Files:**
- Create: `plugins/review-design/.claude-plugin/plugin.json`
- Move: `skills/review-design/` → `plugins/review-design/skills/review-design/`
- Move: `agents/review-design.md` → `plugins/review-design/agents/review-design.md`

- [ ] **Step 1: Create plugin directory**

```bash
mkdir -p plugins/review-design/.claude-plugin plugins/review-design/agents
```

- [ ] **Step 2: Write plugin.json**

```json
{
  "name": "review-design",
  "description": "新機能の実装開始前、ファイルやモジュールの追加時、「このコードはどこに置くべきか」と迷った時に使用。",
  "version": "0.1.0",
  "author": { "name": "Yasuaki Omokawa", "url": "https://github.com/YasuakiOmokawa" },
  "homepage": "https://github.com/YasuakiOmokawa/skills",
  "repository": "https://github.com/YasuakiOmokawa/skills",
  "license": "MIT",
  "keywords": ["code-review", "clean-architecture", "ddd", "hexagonal"]
}
```

- [ ] **Step 3: Move skill + top-level agent**

```bash
git mv skills/review-design plugins/review-design/skills/review-design
git mv agents/review-design.md plugins/review-design/agents/review-design.md
```

- [ ] **Step 4: Verify and commit**

```bash
ls plugins/review-design/skills/review-design/SKILL.md plugins/review-design/agents/review-design.md
jq . plugins/review-design/.claude-plugin/plugin.json
git add plugins/review-design
git commit --no-verify -m "feat: migrate review-design to standalone plugin"
```

---

### Task 6: Migrate review-code-quality (with top-level agent)

**Files:**
- Create: `plugins/review-code-quality/.claude-plugin/plugin.json`
- Move: `skills/review-code-quality/` → `plugins/review-code-quality/skills/review-code-quality/`
- Move: `agents/review-code-quality.md` → `plugins/review-code-quality/agents/review-code-quality.md`

- [ ] **Step 1: Create plugin directory**

```bash
mkdir -p plugins/review-code-quality/.claude-plugin plugins/review-code-quality/agents
```

- [ ] **Step 2: Write plugin.json**

```json
{
  "name": "review-code-quality",
  "description": "実装完了後のセルフチェック時、PRレビュー前の品質確認時に使用。RuboCop/ESLintでは検出できない設計レベルの問題を検出する。",
  "version": "0.1.0",
  "author": { "name": "Yasuaki Omokawa", "url": "https://github.com/YasuakiOmokawa" },
  "homepage": "https://github.com/YasuakiOmokawa/skills",
  "repository": "https://github.com/YasuakiOmokawa/skills",
  "license": "MIT",
  "keywords": ["code-review", "cohesion", "coupling", "readability"]
}
```

- [ ] **Step 3: Move skill + top-level agent**

```bash
git mv skills/review-code-quality plugins/review-code-quality/skills/review-code-quality
git mv agents/review-code-quality.md plugins/review-code-quality/agents/review-code-quality.md
```

- [ ] **Step 4: Verify and commit**

```bash
ls plugins/review-code-quality/skills/review-code-quality/SKILL.md plugins/review-code-quality/agents/review-code-quality.md
jq . plugins/review-code-quality/.claude-plugin/plugin.json
git add plugins/review-code-quality
git commit --no-verify -m "feat: migrate review-code-quality to standalone plugin"
```

---

### Task 7: Migrate polish-before-commit (with top-level agent)

**Files:**
- Create: `plugins/polish-before-commit/.claude-plugin/plugin.json`
- Move: `skills/polish-before-commit/` → `plugins/polish-before-commit/skills/polish-before-commit/`
- Move: `agents/polish-before-commit.md` → `plugins/polish-before-commit/agents/polish-before-commit.md`

- [ ] **Step 1: Create plugin directory**

```bash
mkdir -p plugins/polish-before-commit/.claude-plugin plugins/polish-before-commit/agents
```

- [ ] **Step 2: Write plugin.json**

```json
{
  "name": "polish-before-commit",
  "description": "コミット前やPR作成前に、プロジェクト規約への準拠・パターン一貫性・実装/spec 整合性 (Ruby の delegate / def 撤去後に残る dead mock の検出と削除を含む) を確認・修正したい時に使用。",
  "version": "0.1.0",
  "author": { "name": "Yasuaki Omokawa", "url": "https://github.com/YasuakiOmokawa" },
  "homepage": "https://github.com/YasuakiOmokawa/skills",
  "repository": "https://github.com/YasuakiOmokawa/skills",
  "license": "MIT",
  "keywords": ["code-review", "linting", "commit"]
}
```

- [ ] **Step 3: Move skill + top-level agent**

```bash
git mv skills/polish-before-commit plugins/polish-before-commit/skills/polish-before-commit
git mv agents/polish-before-commit.md plugins/polish-before-commit/agents/polish-before-commit.md
```

- [ ] **Step 4: Verify and commit**

```bash
ls plugins/polish-before-commit/skills/polish-before-commit/SKILL.md plugins/polish-before-commit/agents/polish-before-commit.md
jq . plugins/polish-before-commit/.claude-plugin/plugin.json
git add plugins/polish-before-commit
git commit --no-verify -m "feat: migrate polish-before-commit to standalone plugin"
```

---

### Task 8: Migrate model-data

**Files:**
- Create: `plugins/model-data/.claude-plugin/plugin.json`
- Move: `skills/model-data/` → `plugins/model-data/skills/model-data/`

- [ ] **Step 1: Create plugin directory**

```bash
mkdir -p plugins/model-data/.claude-plugin
```

- [ ] **Step 2: Write plugin.json**

```json
{
  "name": "model-data",
  "description": "要求文書からDBML形式のER図を生成し、SQLアンチパターンを検出。DB設計、ER図作成、スキーマ正規化、既存設計レビュー時に使用。",
  "version": "0.1.0",
  "author": { "name": "Yasuaki Omokawa", "url": "https://github.com/YasuakiOmokawa" },
  "homepage": "https://github.com/YasuakiOmokawa/skills",
  "repository": "https://github.com/YasuakiOmokawa/skills",
  "license": "MIT",
  "keywords": ["er-diagram", "dbml", "database-design", "sql"]
}
```

- [ ] **Step 3: Move skill**

```bash
git mv skills/model-data plugins/model-data/skills/model-data
```

- [ ] **Step 4: Verify and commit**

```bash
ls plugins/model-data/skills/model-data/SKILL.md
jq . plugins/model-data/.claude-plugin/plugin.json
git add plugins/model-data
git commit --no-verify -m "feat: migrate model-data to standalone plugin"
```

---

### Task 9: Migrate map-user-stories

**Files:**
- Create: `plugins/map-user-stories/.claude-plugin/plugin.json`
- Move: `skills/map-user-stories/` → `plugins/map-user-stories/skills/map-user-stories/`

- [ ] **Step 1: Create plugin directory**

```bash
mkdir -p plugins/map-user-stories/.claude-plugin
```

- [ ] **Step 2: Write plugin.json**

```json
{
  "name": "map-user-stories",
  "description": "設計書・プロジェクト仕様・Jira epic等からユーザーストーリーマップを作成し、タスク分解・スプリント計画まで行う場合に使用。新しいプロジェクトフェーズの計画、設計書の分析、大きな機能の実装単位への分解が必要な場合にトリガーされる。",
  "version": "0.1.0",
  "author": { "name": "Yasuaki Omokawa", "url": "https://github.com/YasuakiOmokawa" },
  "homepage": "https://github.com/YasuakiOmokawa/skills",
  "repository": "https://github.com/YasuakiOmokawa/skills",
  "license": "MIT",
  "keywords": ["user-stories", "story-mapping", "plan-driven", "jira"]
}
```

- [ ] **Step 3: Move skill**

```bash
git mv skills/map-user-stories plugins/map-user-stories/skills/map-user-stories
```

- [ ] **Step 4: Verify and commit**

```bash
ls plugins/map-user-stories/skills/map-user-stories/SKILL.md
jq . plugins/map-user-stories/.claude-plugin/plugin.json
git add plugins/map-user-stories
git commit --no-verify -m "feat: migrate map-user-stories to standalone plugin"
```

---

### Task 10: Migrate qa-ui

**Files:**
- Create: `plugins/qa-ui/.claude-plugin/plugin.json`
- Move: `skills/qa-ui/` → `plugins/qa-ui/skills/qa-ui/`

- [ ] **Step 1: Create plugin directory**

```bash
mkdir -p plugins/qa-ui/.claude-plugin
```

- [ ] **Step 2: Write plugin.json**

```json
{
  "name": "qa-ui",
  "description": "実装完了後にChromeDevTools MCPでUI検証を行う。ACがあればAC項目ごとに画面操作・スクリーンショット・pass/fail判定。FAILなら自動修正→再QAを最大3回ループ。",
  "version": "0.1.0",
  "author": { "name": "Yasuaki Omokawa", "url": "https://github.com/YasuakiOmokawa" },
  "homepage": "https://github.com/YasuakiOmokawa/skills",
  "repository": "https://github.com/YasuakiOmokawa/skills",
  "license": "MIT",
  "keywords": ["qa", "ui-testing", "chrome-devtools"]
}
```

- [ ] **Step 3: Move skill**

```bash
git mv skills/qa-ui plugins/qa-ui/skills/qa-ui
```

- [ ] **Step 4: Verify and commit**

```bash
ls plugins/qa-ui/skills/qa-ui/SKILL.md
jq . plugins/qa-ui/.claude-plugin/plugin.json
git add plugins/qa-ui
git commit --no-verify -m "feat: migrate qa-ui to standalone plugin"
```

---

### Task 11: Migrate create-jira-issues

**Files:**
- Create: `plugins/create-jira-issues/.claude-plugin/plugin.json`
- Move: `skills/create-jira-issues/` → `plugins/create-jira-issues/skills/create-jira-issues/`

- [ ] **Step 1: Create plugin directory**

```bash
mkdir -p plugins/create-jira-issues/.claude-plugin
```

- [ ] **Step 2: Write plugin.json**

```json
{
  "name": "create-jira-issues",
  "description": "ユーザーストーリーマップやタスク分解プランからJiraチケットを一括作成する場合に使用。ストーリーマップ完成後のチケット化、プランファイルからの一括作成、計画済みストーリー・タスクのJiraへの移行が必要な場合にトリガーされる。",
  "version": "0.1.0",
  "author": { "name": "Yasuaki Omokawa", "url": "https://github.com/YasuakiOmokawa" },
  "homepage": "https://github.com/YasuakiOmokawa/skills",
  "repository": "https://github.com/YasuakiOmokawa/skills",
  "license": "MIT",
  "keywords": ["jira", "atlassian", "ticket"]
}
```

- [ ] **Step 3: Move skill**

```bash
git mv skills/create-jira-issues plugins/create-jira-issues/skills/create-jira-issues
```

- [ ] **Step 4: Verify and commit**

```bash
ls plugins/create-jira-issues/skills/create-jira-issues/SKILL.md
jq . plugins/create-jira-issues/.claude-plugin/plugin.json
git add plugins/create-jira-issues
git commit --no-verify -m "feat: migrate create-jira-issues to standalone plugin"
```

---

### Task 12: Migrate set-jira-story-points

**Files:**
- Create: `plugins/set-jira-story-points/.claude-plugin/plugin.json`
- Move: `skills/set-jira-story-points/` → `plugins/set-jira-story-points/skills/set-jira-story-points/`

- [ ] **Step 1: Create plugin directory**

```bash
mkdir -p plugins/set-jira-story-points/.claude-plugin
```

- [ ] **Step 2: Write plugin.json**

```json
{
  "name": "set-jira-story-points",
  "description": "JiraキーとStory Pointsのマップデータを受け取り、Jiraチケットに一括でStory Pointsを設定する。「ストーリーポイント設定」「SP設定」「story points」などのキーワードでトリガーされる。",
  "version": "0.1.0",
  "author": { "name": "Yasuaki Omokawa", "url": "https://github.com/YasuakiOmokawa" },
  "homepage": "https://github.com/YasuakiOmokawa/skills",
  "repository": "https://github.com/YasuakiOmokawa/skills",
  "license": "MIT",
  "keywords": ["jira", "atlassian", "story-points"]
}
```

- [ ] **Step 3: Move skill**

```bash
git mv skills/set-jira-story-points plugins/set-jira-story-points/skills/set-jira-story-points
```

- [ ] **Step 4: Verify and commit**

```bash
ls plugins/set-jira-story-points/skills/set-jira-story-points/SKILL.md
jq . plugins/set-jira-story-points/.claude-plugin/plugin.json
git add plugins/set-jira-story-points
git commit --no-verify -m "feat: migrate set-jira-story-points to standalone plugin"
```

---

### Task 13: Migrate translate-to-vision-story

**Files:**
- Create: `plugins/translate-to-vision-story/.claude-plugin/plugin.json`
- Move: `skills/translate-to-vision-story/` → `plugins/translate-to-vision-story/skills/translate-to-vision-story/`

- [ ] **Step 1: Create plugin directory**

```bash
mkdir -p plugins/translate-to-vision-story/.claude-plugin
```

- [ ] **Step 2: Write plugin.json**

```json
{
  "name": "translate-to-vision-story",
  "description": "プロジェクト活動 (commits/PRs/README/ADR) を `~/.claude/skills-config/vision.md` のビジョン要素と照合し、対話型 draft → revise loop で Zenn 記事下書きを生成する。プロジェクト単位の物語化・キャリアブランディング・月次記事執筆時に使用。",
  "version": "0.1.0",
  "author": { "name": "Yasuaki Omokawa", "url": "https://github.com/YasuakiOmokawa" },
  "homepage": "https://github.com/YasuakiOmokawa/skills",
  "repository": "https://github.com/YasuakiOmokawa/skills",
  "license": "MIT",
  "keywords": ["career", "branding", "writing", "zenn"]
}
```

- [ ] **Step 3: Move skill**

```bash
git mv skills/translate-to-vision-story plugins/translate-to-vision-story/skills/translate-to-vision-story
```

- [ ] **Step 4: Verify and commit**

```bash
ls plugins/translate-to-vision-story/skills/translate-to-vision-story/SKILL.md
jq . plugins/translate-to-vision-story/.claude-plugin/plugin.json
git add plugins/translate-to-vision-story
git commit --no-verify -m "feat: migrate translate-to-vision-story to standalone plugin"
```

---

### Task 14: Migrate dry-ssot-text

**Files:**
- Create: `plugins/dry-ssot-text/.claude-plugin/plugin.json`
- Move: `skills/dry-ssot-text/` → `plugins/dry-ssot-text/skills/dry-ssot-text/`

- [ ] **Step 1: Create plugin directory**

```bash
mkdir -p plugins/dry-ssot-text/.claude-plugin
```

- [ ] **Step 2: Write plugin.json**

```json
{
  "name": "dry-ssot-text",
  "description": "Use when an AI-generated document (plan / design doc / RFC / PR description) has grown long with the same concept explained in multiple places and needs consolidation to a single source of truth while preserving navigation aids like TOC, progress tables, and checklists",
  "version": "0.1.0",
  "author": { "name": "Yasuaki Omokawa", "url": "https://github.com/YasuakiOmokawa" },
  "homepage": "https://github.com/YasuakiOmokawa/skills",
  "repository": "https://github.com/YasuakiOmokawa/skills",
  "license": "MIT",
  "keywords": ["writing", "refactoring", "documentation"]
}
```

- [ ] **Step 3: Move skill**

```bash
git mv skills/dry-ssot-text plugins/dry-ssot-text/skills/dry-ssot-text
```

- [ ] **Step 4: Verify and commit**

```bash
ls plugins/dry-ssot-text/skills/dry-ssot-text/SKILL.md
jq . plugins/dry-ssot-text/.claude-plugin/plugin.json
git add plugins/dry-ssot-text
git commit --no-verify -m "feat: migrate dry-ssot-text to standalone plugin"
```

---

### Task 15: Migrate create-pr (command-only plugin)

**Files:**
- Create: `plugins/create-pr/.claude-plugin/plugin.json`
- Move: `commands/create-pr.md` → `plugins/create-pr/commands/create-pr.md`

- [ ] **Step 1: Create plugin directory**

```bash
mkdir -p plugins/create-pr/.claude-plugin plugins/create-pr/commands
```

- [ ] **Step 2: Write plugin.json**

```json
{
  "name": "create-pr",
  "description": "カレントブランチをもとにConventional Commits形式のドラフトPRを作成する slash command。リリースラベル定義 (~/.claude/skills-config/release-labels.md) を参照。",
  "version": "0.1.0",
  "author": { "name": "Yasuaki Omokawa", "url": "https://github.com/YasuakiOmokawa" },
  "homepage": "https://github.com/YasuakiOmokawa/skills",
  "repository": "https://github.com/YasuakiOmokawa/skills",
  "license": "MIT",
  "keywords": ["pr", "github", "conventional-commits"]
}
```

- [ ] **Step 3: Move command**

```bash
git mv commands/create-pr.md plugins/create-pr/commands/create-pr.md
```

- [ ] **Step 4: Verify and commit**

```bash
ls plugins/create-pr/commands/create-pr.md
jq . plugins/create-pr/.claude-plugin/plugin.json
git add plugins/create-pr
git commit --no-verify -m "feat: migrate create-pr command to standalone plugin"
```

---

## Phase 3: Marketplace and Cleanup

### Task 16: Rewrite marketplace.json with 14 plugins

**Files:**
- Modify: `.claude-plugin/marketplace.json`

- [ ] **Step 1: Overwrite marketplace.json**

Replace entire file content with:

```json
{
  "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
  "name": "omokawa-skills",
  "version": "1.0.0",
  "description": "Plan-driven development workflow を構成する個別 skill 群。必要なものだけ install 可能",
  "owner": { "name": "Yasuaki Omokawa", "url": "https://github.com/YasuakiOmokawa" },
  "plugins": [
    {
      "name": "define-acceptance-criteria",
      "description": "プランモード中にプランファイルの受け入れ条件・技術リスクを定義する時に使用。",
      "version": "0.1.0",
      "source": "./plugins/define-acceptance-criteria",
      "category": "productivity",
      "homepage": "https://github.com/YasuakiOmokawa/skills",
      "license": "MIT"
    },
    {
      "name": "mece-plan-review",
      "description": "プランファイルの受け入れ条件（AC）に対しMECE完全性検証を実施。",
      "version": "0.1.0",
      "source": "./plugins/mece-plan-review",
      "category": "productivity",
      "homepage": "https://github.com/YasuakiOmokawa/skills",
      "license": "MIT"
    },
    {
      "name": "finalize-plan",
      "description": "プランモードで設計が確定した後、ブランチ・PR分割・QA手順を追記する。",
      "version": "0.1.0",
      "source": "./plugins/finalize-plan",
      "category": "productivity",
      "homepage": "https://github.com/YasuakiOmokawa/skills",
      "license": "MIT"
    },
    {
      "name": "review-design",
      "description": "新機能の実装開始前、「このコードはどこに置くべきか」と迷った時に使用。",
      "version": "0.1.0",
      "source": "./plugins/review-design",
      "category": "productivity",
      "homepage": "https://github.com/YasuakiOmokawa/skills",
      "license": "MIT"
    },
    {
      "name": "review-code-quality",
      "description": "実装完了後のセルフチェック時、PRレビュー前の品質確認時に使用。",
      "version": "0.1.0",
      "source": "./plugins/review-code-quality",
      "category": "productivity",
      "homepage": "https://github.com/YasuakiOmokawa/skills",
      "license": "MIT"
    },
    {
      "name": "polish-before-commit",
      "description": "コミット前やPR作成前に、プロジェクト規約への準拠・パターン一貫性を確認・修正する。",
      "version": "0.1.0",
      "source": "./plugins/polish-before-commit",
      "category": "productivity",
      "homepage": "https://github.com/YasuakiOmokawa/skills",
      "license": "MIT"
    },
    {
      "name": "model-data",
      "description": "要求文書からDBML形式のER図を生成し、SQLアンチパターンを検出。",
      "version": "0.1.0",
      "source": "./plugins/model-data",
      "category": "productivity",
      "homepage": "https://github.com/YasuakiOmokawa/skills",
      "license": "MIT"
    },
    {
      "name": "map-user-stories",
      "description": "設計書からユーザーストーリーマップを作成しタスク分解・スプリント計画まで行う。",
      "version": "0.1.0",
      "source": "./plugins/map-user-stories",
      "category": "productivity",
      "homepage": "https://github.com/YasuakiOmokawa/skills",
      "license": "MIT"
    },
    {
      "name": "qa-ui",
      "description": "実装完了後にChromeDevTools MCPでUI検証を行う。",
      "version": "0.1.0",
      "source": "./plugins/qa-ui",
      "category": "productivity",
      "homepage": "https://github.com/YasuakiOmokawa/skills",
      "license": "MIT"
    },
    {
      "name": "create-jira-issues",
      "description": "ユーザーストーリーマップやタスク分解プランからJiraチケットを一括作成。",
      "version": "0.1.0",
      "source": "./plugins/create-jira-issues",
      "category": "productivity",
      "homepage": "https://github.com/YasuakiOmokawa/skills",
      "license": "MIT"
    },
    {
      "name": "set-jira-story-points",
      "description": "JiraキーとStory Pointsのマップから一括でStory Pointsを設定する。",
      "version": "0.1.0",
      "source": "./plugins/set-jira-story-points",
      "category": "productivity",
      "homepage": "https://github.com/YasuakiOmokawa/skills",
      "license": "MIT"
    },
    {
      "name": "translate-to-vision-story",
      "description": "プロジェクト活動をビジョン整合した Zenn 記事下書きに翻訳。",
      "version": "0.1.0",
      "source": "./plugins/translate-to-vision-story",
      "category": "personal",
      "homepage": "https://github.com/YasuakiOmokawa/skills",
      "license": "MIT"
    },
    {
      "name": "dry-ssot-text",
      "description": "AI-generated document (plan / design doc / RFC / PR description) を single source of truth に統合。",
      "version": "0.1.0",
      "source": "./plugins/dry-ssot-text",
      "category": "productivity",
      "homepage": "https://github.com/YasuakiOmokawa/skills",
      "license": "MIT"
    },
    {
      "name": "create-pr",
      "description": "カレントブランチをもとにConventional Commits形式のドラフトPRを作成する slash command。",
      "version": "0.1.0",
      "source": "./plugins/create-pr",
      "category": "productivity",
      "homepage": "https://github.com/YasuakiOmokawa/skills",
      "license": "MIT"
    }
  ]
}
```

- [ ] **Step 2: Verify JSON validity**

```bash
jq '.plugins | length' .claude-plugin/marketplace.json
```

Expected: `14`

- [ ] **Step 3: Verify each source path exists**

```bash
jq -r '.plugins[].source' .claude-plugin/marketplace.json | while read src; do test -d "$src" && echo "OK: $src" || echo "MISSING: $src"; done
```

Expected: 全行 `OK: ./plugins/<name>`

- [ ] **Step 4: Commit**

```bash
git add .claude-plugin/marketplace.json
git commit --no-verify -m "feat: rewrite marketplace.json with 14 standalone plugins"
```

---

### Task 17: Remove old top-level skills/, agents/, commands/ directories

**Files:**
- Delete: `skills/`, `agents/`, `commands/` (root level, all should be empty after migrations)

- [ ] **Step 1: Verify old directories are empty**

```bash
ls skills/ 2>/dev/null
ls agents/ 2>/dev/null
ls commands/ 2>/dev/null
```

Expected: 全部 empty (no output) or directories already deleted.

- [ ] **Step 2: Remove empty old directories**

```bash
rmdir skills agents commands 2>/dev/null || true
ls -d skills agents commands 2>/dev/null
```

Expected: no output (directories removed) or `ls: cannot access ...`

- [ ] **Step 3: Verify with git**

```bash
git status
```

Expected: Either clean tree (rmdir didn't change tracked files) or no `skills/` `agents/` `commands/` remaining as tracked dirs.

- [ ] **Step 4: Commit if any change**

```bash
git add -A
git diff --cached --quiet && echo "nothing to commit" || git commit --no-verify -m "chore: remove empty top-level skills/agents/commands directories"
```

---

## Phase 4: Documentation Updates

### Task 18: Update README.md

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Replace README content**

Overwrite `README.md` with:

```markdown
# omokawa-skills

Claude Code 用 plan-driven development plugin 群。**14 個の独立 plugin** に分かれており、必要な skill だけを選択的に install できる。

## クイックスタート

```
/plugin marketplace add YasuakiOmokawa/skills
/plugin install <skill-name>@omokawa-skills
```

必要な skill だけを `/plugin install` する。複数 install したい場合はコマンドを繰り返し実行。続けてターミナルで設定値を生成:

```bash
bash ~/.claude/plugins/marketplaces/omokawa-skills/scripts/setup.sh
```

これで `~/.claude/skills-config/jira.md` などが生成される。**全プロジェクト横断で参照されるグローバル設定**で、プロジェクトを切り替えても同じ設定が効く。

## **重要: 旧 `omokawa-skills` plugin を install 済みの方へ**

v2.0.0 で破壊的変更があり、モノリス plugin `omokawa-skills` は廃止された。各 skill は独立 plugin として再配布されている。移行手順:

```
/plugin uninstall omokawa-skills@omokawa-skills
/plugin marketplace update omokawa-skills
/plugin install <必要な skill>@omokawa-skills
```

## Plugins (14)

### プラン駆動 7-skill セット (engineering / プロジェクト非依存)

| Plugin | 役割 |
|---|---|
| [`model-data`](./plugins/model-data/skills/model-data/SKILL.md) | 要求文書から DBML 形式の ER 図を生成 |
| [`map-user-stories`](./plugins/map-user-stories/skills/map-user-stories/SKILL.md) | 設計書から UserStory/Task を分解 |
| [`define-acceptance-criteria`](./plugins/define-acceptance-criteria/skills/define-acceptance-criteria/SKILL.md) | プランに受け入れ条件 を定義 |
| [`mece-plan-review`](./plugins/mece-plan-review/skills/mece-plan-review/SKILL.md) | 受け入れ条件 に対し3視点で MECE 検証 |
| [`review-design`](./plugins/review-design/skills/review-design/SKILL.md) | 「どこに・どう作るか」を判定 |
| [`finalize-plan`](./plugins/finalize-plan/skills/finalize-plan/SKILL.md) | プラン→実装可能形式へ変換 |
| [`polish-before-commit`](./plugins/polish-before-commit/skills/polish-before-commit/SKILL.md) | コミット前の自動仕上げ |

### Jira セット (personal / 環境依存)

| Plugin | 役割 |
|---|---|
| [`create-jira-issues`](./plugins/create-jira-issues/skills/create-jira-issues/SKILL.md) | プランから Jira チケット一括作成 |
| [`set-jira-story-points`](./plugins/set-jira-story-points/skills/set-jira-story-points/SKILL.md) | Story Points 一括設定 |

### キャリアセット (career / 個人ビジョン整合)

| Plugin | 役割 |
|---|---|
| [`translate-to-vision-story`](./plugins/translate-to-vision-story/skills/translate-to-vision-story/SKILL.md) | プロジェクト活動を Zenn 記事下書きに翻訳 |
| [`dry-ssot-text`](./plugins/dry-ssot-text/skills/dry-ssot-text/SKILL.md) | AI-generated document を SSOT に統合 |

### 単独動作 (engineering / プロジェクト非依存)

| Plugin | 役割 |
|---|---|
| [`qa-ui`](./plugins/qa-ui/skills/qa-ui/SKILL.md) | ChromeDevTools MCP で UI 検証 |
| [`review-code-quality`](./plugins/review-code-quality/skills/review-code-quality/SKILL.md) | 設計レベルの品質問題を検出 |
| [`create-pr`](./plugins/create-pr/commands/create-pr.md) | カレントブランチからドラフト PR 作成 (slash command) |

## 設定値の保管 (グローバル)

これらの plugin が参照する設定値は `~/.claude/skills-config/*.md` に保管される。**ユーザーマシンに 1 セット**だけあれば、全プロジェクトから同じ設定が読まれる。サンプルは `examples/skills-config/` 配下:

- [`examples/skills-config/jira.example.md`](./examples/skills-config/jira.example.md)
- [`examples/skills-config/release-labels.example.md`](./examples/skills-config/release-labels.example.md)
- [`examples/skills-config/environments.example.md`](./examples/skills-config/environments.example.md)

`bash scripts/setup.sh` で対話生成するのが推奨。手動なら `*.example.md` を `~/.claude/skills-config/*.md` にコピーして編集。詳細は [`CONTEXT.md`](./CONTEXT.md) を参照。

## 開発ワークフローの推奨例

```
1. 設計してプランファイルつくる
2. /grill-me などで要件を詰める
3. /map-user-stories で US/Task に分解
4. /create-jira-issues で Jira へ一括登録
5. /define-acceptance-criteria で 受け入れ条件定義
6. /mece-plan-review で網羅性検証
7. /review-design で設計レビュー
8. /finalize-plan でブランチ・PR分割・QA計画を策定
9. 実装
10. /qa-ui で UI 検証
11. /review-code-quality + /polish-before-commit で仕上げ
12. /create-pr でドラフトPR作成
```

## ライセンス

MIT。詳細は [`LICENSE`](./LICENSE) を参照。
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit --no-verify -m "docs: rewrite README for 1-plugin-per-skill structure"
```

---

### Task 19: Update CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Replace CLAUDE.md content**

Overwrite `CLAUDE.md` with:

```markdown
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
| Top-level agent | `plugins/<name>/agents/<name>.md` | 自動 |
| Sub-agent (skill 内) | `plugins/<name>/skills/<name>/agents/*.md` | skill 本文から `Task` ツールで呼出 |

`plugin.json` には `skills/commands/agents` 配列を**書かない**。Claude Code はファイル構造から自動 discovery する。

## marketplace.json

リポジトリ root の `.claude-plugin/marketplace.json` に 14 plugins を列挙。各 entry の `source` は `./plugins/<name>` (相対パス)。

新規 plugin を追加する場合は:
1. `plugins/<name>/` ディレクトリと `plugin.json` を作る
2. `marketplace.json` の `plugins` 配列に entry を追加
3. README の該当バケットに行を追加

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
5. `agents/*.md` 内の `${CLAUDE_PLUGIN_ROOT}/skills/<旧名>/` パス
6. `.claude-plugin/marketplace.json` の対応 entry (`name` と `source`)
7. `README.md` のリンク

## 公開前チェック

- 機密情報 (Cloud ID, API キー等) が含まれていないか `grep` でスキャン
- 組織固有のラベル名・環境名・リポジトリ名がプレースホルダー化されているか
- `${CLAUDE_PLUGIN_ROOT}` が一貫して使われているか
- 改名時に旧名残存がないか
- marketplace.json の `plugins` 配列と `plugins/` 配下のディレクトリが一致しているか
```

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit --no-verify -m "docs: rewrite CLAUDE.md for monorepo+N-plugins layout"
```

---

### Task 20: Update CONTEXT.md

**Files:**
- Modify: `CONTEXT.md`

- [ ] **Step 1: Update layout-related section**

`CONTEXT.md` の冒頭 4 行 (`# omokawa-skills 用語集` 直下) に以下を**挿入**する:

```markdown
## リポジトリ構造

omokawa-skills は **monorepo + N plugins** 構造。各 skill / command は `plugins/<name>/` 配下の独立 plugin として配置される。`marketplace.json` が 14 plugins を列挙する。詳細は CLAUDE.md 参照。
```

- [ ] **Step 2: Verify and commit**

```bash
grep -A1 "リポジトリ構造" CONTEXT.md
git add CONTEXT.md
git commit --no-verify -m "docs: add monorepo+N-plugins note to CONTEXT.md"
```

---

### Task 21: Update CHANGELOG.md

**Files:**
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Prepend 2.0.0 entry**

`CHANGELOG.md` の先頭 (`# Changelog` の下) に以下を挿入:

```markdown
## v2.0.0 (BREAKING) - 2026-05-14

**破壊的変更:** モノリス plugin `omokawa-skills` (v0.11.0) を廃止し、14 個の独立 plugin に分割。

### 移行手順

```
/plugin uninstall omokawa-skills@omokawa-skills
/plugin marketplace update omokawa-skills
/plugin install <必要な skill>@omokawa-skills
```

### 新規 plugin (各 v0.1.0)

- `define-acceptance-criteria`, `mece-plan-review`, `finalize-plan` (+ agent), `review-design` (+ agent), `review-code-quality` (+ agent), `polish-before-commit` (+ agent), `model-data`, `map-user-stories`, `qa-ui`, `create-jira-issues`, `set-jira-story-points`, `translate-to-vision-story`, `dry-ssot-text`
- `create-pr` (slash command-only plugin)

### 理由

ユーザーが必要な skill だけを選択的に install できるようにするため。Jira/ChromeDevTools/個人 vision 関連は利用者によっては不要だが、旧構造ではすべて同梱されていた。
```

- [ ] **Step 2: Commit**

```bash
git add CHANGELOG.md
git commit --no-verify -m "docs: add v2.0.0 BREAKING entry for plugin split"
```

---

## Phase 5: Helper Scripts

### Task 22: Update scripts/link-*.sh for new layout

**Files:**
- Modify: `scripts/link-skills.sh`
- Modify: `scripts/link-agents.sh`
- Modify: `scripts/link-commands.sh`
- Modify: `scripts/list-skills.sh`

これらのスクリプトは旧 `skills/` `agents/` `commands/` 配下を symlink するためのもの。新レイアウトでは `plugins/<name>/...` に変更する。

- [ ] **Step 1: Update link-skills.sh**

`scripts/link-skills.sh` の `find` 行を以下に置換:

旧:
```bash
find "$REPO/skills" -name SKILL.md -not -path '*/node_modules/*' -print0 |
```

新:
```bash
find "$REPO/plugins" -path '*/skills/*/SKILL.md' -not -path '*/node_modules/*' -print0 |
```

- [ ] **Step 2: Update link-agents.sh**

`scripts/link-agents.sh` の `for src` 行を以下に置換:

旧:
```bash
for src in "$REPO/agents"/*.md; do
```

新:
```bash
for src in "$REPO"/plugins/*/agents/*.md; do
```

- [ ] **Step 3: Update link-commands.sh**

`scripts/link-commands.sh` の `for src` 行を以下に置換:

旧:
```bash
for src in "$REPO/commands"/*.md; do
```

新:
```bash
for src in "$REPO"/plugins/*/commands/*.md; do
```

- [ ] **Step 4: Update list-skills.sh**

`scripts/list-skills.sh` 全文を以下に置換:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Lists all skills, commands, and agents across all plugins in this repository.

REPO="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO"

echo "=== Plugins ==="
ls -1 plugins/ 2>/dev/null | sort

echo ""
echo "=== Skills ==="
find plugins -path '*/skills/*/SKILL.md' | sed 's|/SKILL.md$||' | sort

echo ""
echo "=== Commands ==="
find plugins -path '*/commands/*.md' | sort

echo ""
echo "=== Top-level Agents ==="
find plugins -path '*/agents/*.md' -not -path '*/skills/*' | sort
```

- [ ] **Step 5: Verify scripts work**

```bash
bash scripts/list-skills.sh
```

Expected: 14 plugins listed under `=== Plugins ===`, 13 SKILL.md paths under `=== Skills ===`, 1 command under `=== Commands ===`, 4 top-level agents.

- [ ] **Step 6: Commit**

```bash
git add scripts/link-skills.sh scripts/link-agents.sh scripts/link-commands.sh scripts/list-skills.sh
git commit --no-verify -m "chore: update helper scripts for plugins/ layout"
```

---

## Phase 6: SKILL.md Augmentation

### Task 23: Add 「併用推奨 skill」 sections where missing

**Files:**
- Modify: SKILL.md of skills with cross-references

対象 skill と追加内容:

| Plugin | 併用推奨 skill |
|---|---|
| define-acceptance-criteria | `/mece-plan-review` (AC 網羅性検証), `/finalize-plan` (実装準備フェーズ) |
| mece-plan-review | `/define-acceptance-criteria` (AC 定義), `/finalize-plan` (実装準備フェーズ) |
| finalize-plan | `/define-acceptance-criteria`, `/mece-plan-review`, `/qa-ui` (実装後 UI 検証), `/create-pr` (PR 作成) |
| map-user-stories | `/create-jira-issues` (チケット化), `/define-acceptance-criteria` (AC 定義) |
| create-jira-issues | `/map-user-stories` (US 分解), `/set-jira-story-points` (SP 設定) |
| review-design | `/define-acceptance-criteria` (実装前 AC 定義) |
| review-code-quality | `/polish-before-commit` (コミット前仕上げ), `/qa-ui` (UI 検証) |
| polish-before-commit | `/review-code-quality` (設計レビュー), `/create-pr` (PR 作成) |
| qa-ui | `/finalize-plan` (AC 参照元), `/review-code-quality` (品質確認) |

- [ ] **Step 1: For each SKILL.md above, append a section**

各 SKILL.md ファイル末尾に以下のセクションを追加 (例: define-acceptance-criteria):

```markdown
## 併用推奨 skill

- `/mece-plan-review` — このスキルで定義した AC の網羅性を 3 視点で検証する
- `/finalize-plan` — AC + MECE 結果をもとにブランチ・PR 分割・QA 手順を起こす
```

各 plugin の SKILL.md パスは `plugins/<plugin>/skills/<plugin>/SKILL.md`。

実行手順:

```bash
# 例: define-acceptance-criteria
cat >> plugins/define-acceptance-criteria/skills/define-acceptance-criteria/SKILL.md <<'EOF'

## 併用推奨 skill

- `/mece-plan-review` — このスキルで定義した AC の網羅性を 3 視点で検証する
- `/finalize-plan` — AC + MECE 結果をもとにブランチ・PR 分割・QA 手順を起こす
EOF
```

(quoted `<<'EOF'` 内では backtick は literal、escape 不要)

すべての対象 SKILL.md について上記パターンを繰り返す (内容は表に従う)。

- [ ] **Step 2: Verify all sections present**

```bash
for p in define-acceptance-criteria mece-plan-review finalize-plan map-user-stories create-jira-issues review-design review-code-quality polish-before-commit qa-ui; do
  grep -q "## 併用推奨 skill" "plugins/$p/skills/$p/SKILL.md" && echo "OK: $p" || echo "MISSING: $p"
done
```

Expected: 全 9 plugin で `OK: <name>`

- [ ] **Step 3: Commit**

```bash
git add plugins/*/skills/*/SKILL.md
git commit --no-verify -m "docs: add 併用推奨 skill section to cross-referenced SKILL.md"
```

---

## Phase 7: Final Validation

### Task 24: End-to-end validation

**Files:** (read-only verification)

- [ ] **Step 1: Verify 14 plugin directories exist**

```bash
ls -1 plugins/ | wc -l
```

Expected: `14`

- [ ] **Step 2: Verify each plugin has valid plugin.json**

```bash
for p in plugins/*/.claude-plugin/plugin.json; do jq -e .name "$p" > /dev/null || echo "INVALID: $p"; done
echo "all valid"
```

Expected: `all valid` (no INVALID lines)

- [ ] **Step 3: Verify marketplace.json source paths all exist**

```bash
jq -r '.plugins[].source' .claude-plugin/marketplace.json | while read src; do test -d "$src" || echo "MISSING: $src"; done
echo "all sources exist"
```

Expected: `all sources exist`

- [ ] **Step 4: Verify no old top-level skill/agent/command dirs**

```bash
for d in skills agents commands; do test -d "$d" && echo "STILL EXISTS: $d" || true; done
echo "old dirs removed"
```

Expected: `old dirs removed`

- [ ] **Step 5: Verify no remaining references to old paths in docs**

```bash
grep -r "skills/[a-z-]*/SKILL.md" README.md CLAUDE.md CONTEXT.md 2>/dev/null | grep -v "plugins/" | grep -v "examples/" || echo "no stale path references in docs"
```

Expected: `no stale path references in docs`

- [ ] **Step 6: Verify SKILL.md count = 13**

```bash
find plugins -path '*/skills/*/SKILL.md' | wc -l
```

Expected: `13`

- [ ] **Step 7: Verify create-pr command exists**

```bash
ls plugins/create-pr/commands/create-pr.md
```

Expected: path printed.

- [ ] **Step 8: Verify top-level agent count = 4**

```bash
find plugins -path '*/agents/*.md' -not -path '*/skills/*' | wc -l
```

Expected: `4`

- [ ] **Step 9: Verify scripts/setup.sh path reference unchanged**

```bash
grep -c "skills-config" scripts/setup.sh
```

Expected: 数字 > 0 (setup.sh は `~/.claude/skills-config/` に書き込むので変更不要)

- [ ] **Step 10: Final commit and push branch**

```bash
git status  # should be clean
git log --oneline -20
git push -u origin feat/one-plugin-per-skill
```

- [ ] **Step 11: Open PR**

```bash
gh pr create --title "feat: split omokawa-skills into 14 standalone plugins (BREAKING)" --body "$(cat <<'EOF'
## Summary
- omokawa-skills モノリス plugin を 14 個の独立 plugin (13 skills + 1 command) に分割
- marketplace.json + plugins/ 構造へ変更
- 旧 omokawa-skills plugin は即時廃止 (BREAKING)

## Test plan
- [ ] /plugin marketplace add YasuakiOmokawa/skills が 14 plugins を listing する
- [ ] 各 plugin の単独 install が動く
- [ ] agent 同梱 plugin (review-design, review-code-quality, finalize-plan, polish-before-commit) で ${CLAUDE_PLUGIN_ROOT} 解決が正しい
- [ ] bash scripts/setup.sh が動く
- [ ] CHANGELOG / README の移行手順が辿れる

Spec: docs/superpowers/specs/2026-05-14-monorepo-one-plugin-per-skill-design.md
Plan: docs/superpowers/plans/2026-05-14-monorepo-one-plugin-per-skill.md

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)" --draft
```

---

## 完了条件

- [ ] Task 1-24 すべて完了
- [ ] PR がドラフト状態で作成されている
- [ ] CHANGELOG v2.0.0 が記述されている
- [ ] README に旧ユーザー向け移行セクションがある
- [ ] `bash scripts/list-skills.sh` が 14 plugins / 13 skills / 1 command / 4 agents を表示する

## マニュアル検証 (PR マージ前に user が実施)

以下は自動化できないため、PR レビュー時または merge 後に user が手動で確認する:

- [ ] `/plugin marketplace add YasuakiOmokawa/skills` で 14 plugins が listing される
- [ ] 任意の plugin (例: `define-acceptance-criteria`) を `/plugin install <name>@omokawa-skills` で install できる
- [ ] agent 同梱 plugin (`review-design` 等) を install 後、skill 内 agent 呼出で `${CLAUDE_PLUGIN_ROOT}` が plugin ディレクトリに解決される
- [ ] 旧 `omokawa-skills` plugin を install していた環境で `/plugin uninstall omokawa-skills@omokawa-skills` → `/plugin marketplace update omokawa-skills` → 新 plugin install の移行手順が成立する
