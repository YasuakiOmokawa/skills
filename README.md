# omokawa-skills

Yasuaki Omokawa の Claude Code 用 skills / commands / agents 集。**プラン駆動開発**（spec → AC → MECE → finalize → implement）を支える小さな道具を、付け外し可能なまま並べてあります。

## クイックスタート

Claude Code 内で次の 2 ステップを実行：

```
/plugin marketplace add YasuakiOmokawa/skills
/plugin install omokawa-skills@omokawa-skills
```

これで **11 skills + 1 command + 4 agents** が一括でインストールされます。続けてターミナルで設定値を生成：

```bash
bash ~/.claude/plugins/marketplaces/omokawa-skills/scripts/setup.sh
```

これで `~/.claude/skills-config/jira.md` などが生成されます。**全プロジェクト横断で参照されるグローバル設定**で、プロジェクトを切り替えても同じ設定が効きます。

> ⚠️ **セキュリティ設計**：セットアップは Claude を介さず bash で実行します。Jira Cloud ID などの設定値が AI のコンテキスト（transcript / API ログ）に乗らないよう、`scripts/setup.sh` がローカルで対話受付してファイルに直接書き込みます。

## Skills（11 個）

### engineering 系（プロジェクト非依存）

プラン駆動開発の流れ（**spec → AC → MECE → finalize → implement → review**）に対応：

| スキル | 役割 |
|---|---|
| [`map-user-stories`](./skills/map-user-stories/SKILL.md) | 設計書/Jira epic から US/Task を分解。後段の `create-jira-issues` と契約フォーマットで連携 |
| [`define-acceptance-criteria`](./skills/define-acceptance-criteria/SKILL.md) | プランに **4カテゴリ × 観点マトリクス**で AC を定義。`mece-plan-review` の検証ターゲット |
| [`mece-plan-review`](./skills/mece-plan-review/SKILL.md) | AC に対し3視点（QA / Tech / Red Team）で MECE 検証。サブエージェント並列分析 |
| [`finalize-plan`](./skills/finalize-plan/SKILL.md) | プラン→実装可能形式へ変換。**4 サブエージェント並列**（Branch / PR-split / Manual-QA / Auto-QA） |
| [`review-design`](./skills/review-design/SKILL.md) | 「どこに・どう作るか」を **4 reviewer 並列**で判定（Clean Architecture / Hexagonal / DDD / Anti-pattern） |
| [`model-data`](./skills/model-data/SKILL.md) | 要求文書から DBML 形式の ER 図を生成。Requirements → Conceptual → Logical のパイプライン |
| [`polish-before-commit`](./skills/polish-before-commit/SKILL.md) | コミット前にプロジェクト規約への準拠とパターン一貫性を**自動修正** |
| [`review-code-quality`](./skills/review-code-quality/SKILL.md) | 設計レベルの問題（凝集度/結合度/可読性）を**3 analyzer 並列**で検出。提案のみ |
| [`qa-ui`](./skills/qa-ui/SKILL.md) | ChromeDevTools MCP で UI 検証。**Generator-Evaluator 分離**で別コンテキストが判定 |

### personal 系（環境依存）

| スキル | 役割 |
|---|---|
| [`create-jira-issues`](./skills/create-jira-issues/SKILL.md) | プランファイルから Jira チケット一括作成。`~/.claude/skills-config/jira.md` を参照 |
| [`set-jira-story-points`](./skills/set-jira-story-points/SKILL.md) | Jira キー → SP マップから一括設定。Atlassian MCP 必須 |

## Commands（1 個）

| コマンド | 役割 |
|---|---|
| [`/create-pr`](./commands/create-pr/create-pr.md) | カレントブランチからドラフト PR を作成。Conventional Commits タイトル + テンプレ準拠 + ラベル自動付与（`~/.claude/skills-config/release-labels.md` から動的取得） |

初回セットアップは Claude のスラッシュコマンドではなく bash スクリプト（[`scripts/setup.sh`](./scripts/setup.sh)）で行います。理由は上記「セキュリティ設計」の節を参照。

## Agents（4 個）

各エージェントは対応するスキルとセットで動作。サブエージェント並列起動の司令塔。

| エージェント | 司令塔として呼ぶサブエージェント数 |
|---|---|
| [`review-design`](./agents/review-design.md) | 4（Clean Architecture / Hexagonal / DDD / Anti-pattern） |
| [`review-code-quality`](./agents/review-code-quality.md) | 3（Cohesion / Coupling / Readability） |
| [`finalize-plan`](./agents/finalize-plan.md) | 4（Branch-planner / PR-splitter / Manual-QA / Auto-QA） |
| [`polish-before-commit`](./agents/polish-before-commit.md) | 1+α（外部 `code-simplifier` / `feature-dev` プラグインがあれば連携） |

## 設定値の保管（グローバル）

これらのスキル/コマンドが必要とする設定値は `~/.claude/skills-config/*.md` に保管します。**ユーザーマシンに 1 セット**だけあれば、全プロジェクトから同じ設定が読まれます。サンプルは `examples/skills-config/` 配下：

- [`examples/skills-config/jira.example.md`](./examples/skills-config/jira.example.md) — Jira Cloud ID, プロジェクトキー, MCP プレフィックス
- [`examples/skills-config/release-labels.example.md`](./examples/skills-config/release-labels.example.md) — Productivity / AI Contribution / Release Level ラベル定義
- [`examples/skills-config/environments.example.md`](./examples/skills-config/environments.example.md) — integration 環境名

`bash scripts/setup.sh` で対話生成するのが推奨。手動なら `*.example.md` を `~/.claude/skills-config/*.md` にコピーして編集。詳細は [`CONTEXT.md`](./CONTEXT.md) を参照。

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
