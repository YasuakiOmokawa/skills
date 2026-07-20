# YasuakiOmokawa/skills

開発効率化スキル群。提供する開発スタイルは2つ：

- 上流開発 ... AIでプロトタイプを高速で作って、コード設計とデザインドキュメントを成果物として作成するスキル
- 下流開発 ... デザインドキュメントを基にタスクを切ってコード実装し、プルリクエストを成果物として作成するスキル

## クイックスタート

```bash
npx skills add YasuakiOmokawa/skills
```

対話で必要な skill を選んで install。

### 設定値の生成

続けてターミナルで設定値を生成:

```bash
bash scripts/setup.sh
```

これで `~/.claude/skills-config/jira.md` などが生成される。**全プロジェクト横断で参照されるグローバル設定**で、プロジェクトを切り替えても同じ設定が効く。

## Plugins

### プラン駆動

| Plugin | 役割 |
|---|---|
| [`model-data`](./plugins/model-data/skills/model-data/SKILL.md) | 要求文書から DBML 形式の ER 図を生成 |
| [`map-user-stories`](./plugins/map-user-stories/skills/map-user-stories/SKILL.md) | 設計書から UserStory/Task を分解 |
| [`define-acceptance-criteria`](./plugins/define-acceptance-criteria/skills/define-acceptance-criteria/SKILL.md) | プランに受け入れ条件 を定義 |
| [`mece-plan-review`](./plugins/mece-plan-review/skills/mece-plan-review/SKILL.md) | 受け入れ条件 に対し3視点で MECE 検証 |
| [`review-design`](./plugins/review-design/skills/review-design/SKILL.md) | 「どこに・どう作るか」を判定 |
| [`finalize-plan`](./plugins/finalize-plan/skills/finalize-plan/SKILL.md) | プラン→実装可能形式へ変換 |
| [`polish-before-commit`](./plugins/polish-before-commit/skills/polish-before-commit/SKILL.md) | コミット前の自動仕上げ |

### Jira セット

| Plugin | 役割 |
|---|---|
| [`create-jira-issues`](./plugins/create-jira-issues/skills/create-jira-issues/SKILL.md) | プランから Jira チケット一括作成 |
| [`set-jira-story-points`](./plugins/set-jira-story-points/skills/set-jira-story-points/SKILL.md) | Story Points 一括設定 |

### キャリアセット

| Plugin | 役割 |
|---|---|
| [`translate-to-vision-story`](./plugins/translate-to-vision-story/skills/translate-to-vision-story/SKILL.md) | プロジェクト活動を Zenn 記事下書きに翻訳 |

### 単独動作

| Plugin | 役割 |
|---|---|
| [`iterate-with-prototypes`](./plugins/iterate-with-prototypes/skills/iterate-with-prototypes/SKILL.md) | 未検証仮定のある複雑機能を code-first(動かしてから設計)で本番まで回す |
| [`extract-figma-spec`](./plugins/extract-figma-spec/skills/extract-figma-spec/SKILL.md) | Figma 指定を全プロパティ抽出しチェックリスト照合して反映漏れを防ぐ |
| [`qa-ui`](./plugins/qa-ui/skills/qa-ui/SKILL.md) | ChromeDevTools MCP で UI 検証 |
| [`review-code-quality`](./plugins/review-code-quality/skills/review-code-quality/SKILL.md) | 設計レベルの品質問題を検出 |
| [`express-intent-in-code`](./plugins/express-intent-in-code/skills/express-intent-in-code/SKILL.md) | 機構名/形状名を目的(why)表明形へ変換し why コメント依存を減らす |
| [`create-pr`](./plugins/create-pr/skills/create-pr/SKILL.md) | カレントブランチからドラフト PR 作成 |
| [`dry-ssot-text`](./plugins/dry-ssot-text/skills/dry-ssot-text/SKILL.md) | AI-generated document を SSOT に統合 |
| [`purge-private-vocab`](./plugins/purge-private-vocab/skills/purge-private-vocab/SKILL.md) | plan 由来の固有語を対外文書から除染 |
| [`review-plan-diff`](./plugins/review-plan-diff/skills/review-plan-diff/SKILL.md) | 確定プランと実装後の diff を突き合わせ実装漏れ・仕様逸脱を検出 |
| [`build-poc`](./plugins/build-poc/skills/build-poc/SKILL.md) | やりたいことを技術調査 → 星取表 → 最小実装で裏どりして PoC 化 |
| [`build-prototype`](./plugins/build-prototype/skills/build-prototype/SKILL.md) | PoC を既存コードベース慣習に合わせ DD を起こせる水準のプロトタイプへ実装 |
| [`create-design-doc`](./plugins/create-design-doc/skills/create-design-doc/SKILL.md) | プロトタイプと申し送りから DD (Design Doc) を作成 |

## 設定値の保管 (グローバル)

設定値は `~/.claude/skills-config/*.md` に保管される。**ユーザーマシンに 1 セット**だけあれば、全プロジェクトから同じ設定が読まれる。

## 開発ワークフローの推奨例

### プロトタイプ駆動で、DDまで作成

```
/build-poc
/build-prototype
/create-design-doc
```

### 単発の設計 => 実装

```
プランファイルをつくって /grill-with-docs

/review-design
/define-acceptance-criteria
/mece-plan-review
/finalize-plan
/dry-ssot-text → /purge-private-vocab → /cognitive-rhythm-writing

/express-intent-in-code のガイドラインで実装。コミットは指示まで禁止

/review-plan-diff
/qa-ui

/simplify
/vercel-react-best-practices
/vercel-composition-patterns
/react-doctor
/review-code-quality
/express-intent-in-code
/polish-before-commit
コードコメントと md ファイルに /dry-ssot-text → /purge-private-vocab → /cognitive-rhythm-writing

/create-pr
```

## 出典

- grill-with-docs ... https://github.com/mattpocock/skills
- cognitive-rhythm-writing ... https://gist.github.com/k16shikano/eb2929f13ed19c97188393d297be8432

## ライセンス

MIT。詳細は [`LICENSE`](./LICENSE) を参照。
