# omokawa-skills

Yasuaki Omokawa の Claude Code 用 skills / commands / agents 集。**プラン駆動開発**（spec → AC → MECE → finalize → implement）を支える小さな道具を、付け外し可能なまま並べてあります。

## クイックスタート

### 推奨：`npx skills` でインストール

```bash
# 1. インストーラ起動（mattpocock らが配布している汎用 skills CLI）
npx skills@latest add YasuakiOmokawa/skills

# 2. インストールしたいスキル/コマンド/エージェントを対話で選択
#    （`/setup-omokawa-skills` を必ず含めること）

# 3. プロジェクトごとの設定値を対話生成
/setup-omokawa-skills
```

これで `docs/agents/jira.md` などが生成され、各スキルが透過的に動きます。

### 代替：手動 clone + シンボリックリンク

```bash
git clone https://github.com/YasuakiOmokawa/skills.git ~/projects/skills
cd ~/projects/skills
./scripts/link-skills.sh    # ~/.claude/skills/ にリンク
./scripts/link-commands.sh  # ~/.claude/commands/ にリンク
./scripts/link-agents.sh    # ~/.claude/agents/ にリンク

# その後 Claude Code を起動して
/setup-omokawa-skills
```

`npx` を使えない環境（オフライン・社内 npm registry 制限など）はこちらを推奨。

## なぜこのリポジトリが存在するか

Claude Code に「**何をする道具か**」を動詞で名付け、`docs/agents/*.md` で**プロジェクト固有値を外出し**することで、自分の開発フロー全体を**他人にも他リポにも持ち運べる形**にする。元は freee 社内向けに育てた skills だったが、社内固有部分を剥がして再利用可能にした。

## Skills（11 個）

### `skills/engineering/` — 日常開発のスキル

プラン駆動開発の流れ（**spec → AC → MECE → finalize → implement → review**）に対応：

| スキル | 役割 |
|---|---|
| [`map-user-stories`](./skills/engineering/map-user-stories/SKILL.md) | 設計書/Jira epic から US/Task を分解。後段の `create-jira-issues` と契約フォーマットで連携 |
| [`define-acceptance-criteria`](./skills/engineering/define-acceptance-criteria/SKILL.md) | プランに **4カテゴリ × 観点マトリクス**で AC を定義。`mece-plan-review` の検証ターゲット |
| [`mece-plan-review`](./skills/engineering/mece-plan-review/SKILL.md) | AC に対し3視点（QA / Tech / Red Team）で MECE 検証。サブエージェント並列分析 |
| [`finalize-plan`](./skills/engineering/finalize-plan/SKILL.md) | プラン→実装可能形式へ変換。**4 サブエージェント並列**（Branch / PR-split / Manual-QA / Auto-QA） |
| [`review-design`](./skills/engineering/review-design/SKILL.md) | 「どこに・どう作るか」を **4 reviewer 並列**で判定（Clean Architecture / Hexagonal / DDD / Anti-pattern） |
| [`model-data`](./skills/engineering/model-data/SKILL.md) | 要求文書から DBML 形式の ER 図を生成。Requirements → Conceptual → Logical のパイプライン |
| [`polish-before-commit`](./skills/engineering/polish-before-commit/SKILL.md) | コミット前にプロジェクト規約への準拠とパターン一貫性を**自動修正** |
| [`review-code-quality`](./skills/engineering/review-code-quality/SKILL.md) | 設計レベルの問題（凝集度/結合度/可読性）を**3 analyzer 並列**で検出。提案のみ |
| [`qa-ui`](./skills/engineering/qa-ui/SKILL.md) | ChromeDevTools MCP で UI 検証。**Generator-Evaluator 分離**で別コンテキストが判定 |

### `skills/personal/` — 環境依存スキル

| スキル | 役割 |
|---|---|
| [`create-jira-issues`](./skills/personal/create-jira-issues/SKILL.md) | プランファイルから Jira チケット一括作成。`docs/agents/jira.md` を参照 |
| [`set-jira-story-points`](./skills/personal/set-jira-story-points/SKILL.md) | Jira キー → SP マップから一括設定。Atlassian MCP 必須 |

## Commands（2 個）

| コマンド | 役割 |
|---|---|
| [`/create-pr`](./commands/create-pr/create-pr.md) | カレントブランチからドラフト PR を作成。Conventional Commits タイトル + テンプレ準拠 + ラベル自動付与（`docs/agents/release-labels.md` から動的取得） |
| [`/setup-omokawa-skills`](./commands/setup-omokawa-skills/setup-omokawa-skills.md) | 初回利用時の対話セットアップ。`docs/agents/*.md` を生成 |

## Agents（4 個）

各エージェントは対応するスキルとセットで動作。サブエージェント並列起動の司令塔。

| エージェント | 司令塔として呼ぶサブエージェント数 |
|---|---|
| [`review-design`](./agents/review-design.md) | 4（Clean Architecture / Hexagonal / DDD / Anti-pattern） |
| [`review-code-quality`](./agents/review-code-quality.md) | 3（Cohesion / Coupling / Readability） |
| [`finalize-plan`](./agents/finalize-plan.md) | 4（Branch-planner / PR-splitter / Manual-QA / Auto-QA） |
| [`polish-before-commit`](./agents/polish-before-commit.md) | 1+α（外部 `code-simplifier` / `feature-dev` プラグインがあれば連携） |

## 設定値の保管

これらのスキル/コマンドが必要とする**プロジェクト固有値**は `docs/agents/*.md` に保管：

- [`docs/agents/jira.example.md`](./docs/agents/jira.example.md) — Jira Cloud ID, プロジェクトキー, MCP プレフィックス
- [`docs/agents/release-labels.example.md`](./docs/agents/release-labels.example.md) — Productivity / AI Contribution / Release Level ラベル定義
- [`docs/agents/environments.example.md`](./docs/agents/environments.example.md) — integration 環境名

`*.example.md` をコピーして `*.md` を作るか、`/setup-omokawa-skills` で対話生成。詳細は [`CONTEXT.md`](./CONTEXT.md) を参照。

## 開発ワークフローの推奨例

```
1. /grill-me で要件をストレステスト
2. /map-user-stories で US/Task に分解
3. /create-jira-issues で Jira へ一括登録
4. プランモードで設計
5. /define-acceptance-criteria で AC を定義
6. /mece-plan-review で網羅性検証
7. /finalize-plan でブランチ・PR分割・QA計画を策定
8. 実装
9. /qa-ui で UI 検証
10. /review-code-quality + /polish-before-commit で仕上げ
11. /create-pr でドラフトPR作成
```

## 開発ガイド

- [`CLAUDE.md`](./CLAUDE.md) — バケット運用ルール、命名規約、改名チェックリスト
- [`CONTEXT.md`](./CONTEXT.md) — 用語集（プランファイル / 分析ファイル / AC / MECE 等）

## ライセンス

MIT。詳細は [`LICENSE`](./LICENSE) を参照。
