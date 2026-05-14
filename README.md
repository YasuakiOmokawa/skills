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
