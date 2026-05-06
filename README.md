# omokawa-skills

Claude Code 用。プラン駆動開発を推進するためのもの。

## クイックスタート

Claude Code 内で次の 2 ステップを実行：

```
/plugin marketplace add YasuakiOmokawa/skills
/plugin install omokawa-skills@omokawa-skills
```

続けてターミナルで設定値を生成：

```bash
bash ~/.claude/plugins/marketplaces/omokawa-skills/scripts/setup.sh
```

これで `~/.claude/skills-config/jira.md` などが生成されます。**全プロジェクト横断で参照されるグローバル設定**で、プロジェクトを切り替えても同じ設定が効きます。

## Skills

### engineering 系（プロジェクト非依存）

プラン駆動開発に対応：

| スキル | 役割 |
|---|---|
| [`model-data`](./skills/model-data/SKILL.md) | 要求文書から DBML 形式の ER 図を生成 |
| [`map-user-stories`](./skills/map-user-stories/SKILL.md) | 設計書から UserStory/Task を分解。後段の `create-jira-issues` と契約フォーマットで連携 |
| [`define-acceptance-criteria`](./skills/define-acceptance-criteria/SKILL.md) | プランに受け入れ条件 を定義。`mece-plan-review` の検証ターゲット |
| [`mece-plan-review`](./skills/mece-plan-review/SKILL.md) | 受け入れ条件 に対し3視点（QA / Tech / Red Team）で MECE 検証 |
| [`review-design`](./skills/review-design/SKILL.md) | 「どこに・どう作るか」を 判定（Clean Architecture / Hexagonal / DDD / Anti-pattern） |
| [`finalize-plan`](./skills/finalize-plan/SKILL.md) | プラン→実装可能形式へ変換 |
| [`qa-ui`](./skills/qa-ui/SKILL.md) | ChromeDevTools MCP で UI 検証 |
| [`review-code-quality`](./skills/review-code-quality/SKILL.md) | 設計レベルの問題（凝集度/結合度/可読性）を検出 |
| [`polish-before-commit`](./skills/polish-before-commit/SKILL.md) | コミット前にプロジェクト規約への準拠とパターン一貫性を**自動修正** |

### personal 系（環境依存）

| スキル | 役割 |
|---|---|
| [`create-jira-issues`](./skills/create-jira-issues/SKILL.md) | プランファイルから Jira チケット一括作成。`~/.claude/skills-config/jira.md` を参照 |
| [`set-jira-story-points`](./skills/set-jira-story-points/SKILL.md) | Jira キー → StoryPoint マップから一括設定。Atlassian MCP 必須 |

## Commands

| コマンド | 役割 |
|---|---|
| [`/create-pr`](./commands/create-pr.md) | カレントブランチからドラフト PR を作成。ラベル自動付与（`~/.claude/skills-config/release-labels.md` から動的取得） |

## 設定値の保管（グローバル）

これらのスキル/コマンドが必要とする設定値は `~/.claude/skills-config/*.md` に保管します。**ユーザーマシンに 1 セット**だけあれば、全プロジェクトから同じ設定が読まれます。サンプルは `examples/skills-config/` 配下：

- [`examples/skills-config/jira.example.md`](./examples/skills-config/jira.example.md) — Jira Cloud ID, プロジェクトキー, MCP プレフィックス
- [`examples/skills-config/release-labels.example.md`](./examples/skills-config/release-labels.example.md) — Productivity / AI Contribution / Release Level ラベル定義
- [`examples/skills-config/environments.example.md`](./examples/skills-config/environments.example.md) — integration 環境名

`bash scripts/setup.sh` で対話生成するのが推奨。手動なら `*.example.md` を `~/.claude/skills-config/*.md` にコピーして編集。詳細は [`CONTEXT.md`](./CONTEXT.md) を参照。

## 開発ワークフローの推奨例

```
1. 設計してプランファイルつくる
2. /grill-me などで要件を詰める
2. /map-user-stories で US/Task に分解
3. /create-jira-issues で Jira へ一括登録
5. /define-acceptance-criteria で 受け入れ条件定義
6. /mece-plan-review で網羅性検証
7. /review-design で設計レビュー
7. /finalize-plan でブランチ・PR分割・QA計画を策定
8. 実装
9. /qa-ui で UI 検証
10. /review-code-quality + /polish-before-commit で仕上げ
11. /create-pr でドラフトPR作成
```

## ライセンス

MIT。詳細は [`LICENSE`](./LICENSE) を参照。
