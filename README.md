# YasuakiOmokawa/skills

開発効率化スキル群。提供する開発スタイルは2つ：

- 上流開発 ... AIでプロトタイプを高速で作って、コード設計とデザインドキュメントを成果物として提供するスキル
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

`ai-prototype-flow` を使う場合は、自組織の DD テンプレート・実例 (組織固有情報のためリポジトリに同梱していない) も、このスクリプトが手元のファイルから `~/.claude/skills-config/ai-prototype-flow/` にコピーして配置する。

## Plugins (20)

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

### 単独動作 (engineering / プロジェクト非依存)

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
| [`ai-prototype-flow`](./plugins/ai-prototype-flow/skills/ai-prototype-flow/SKILL.md) | AI プロトタイプ駆動開発フロー (PoC → 設計確定 → DD 作成 → 出荷実装) を 1 フェーズずつ実行する dispatcher |

## 設定値の保管 (グローバル)

これらの plugin が参照する設定値は `~/.claude/skills-config/*.md` に保管される。**ユーザーマシンに 1 セット**だけあれば、全プロジェクトから同じ設定が読まれる。サンプルは `examples/skills-config/` 配下:

- [`examples/skills-config/jira.example.md`](./examples/skills-config/jira.example.md)
- [`examples/skills-config/release-labels.example.md`](./examples/skills-config/release-labels.example.md)
- [`examples/skills-config/environments.example.md`](./examples/skills-config/environments.example.md)

`bash scripts/setup.sh` で対話生成するのが推奨。手動なら `*.example.md` を `~/.claude/skills-config/*.md` にコピーして編集。`ai-prototype-flow` の DD 文書 (テンプレート・実例) は組織固有のため example を同梱しない — setup.sh が手元のファイルを `~/.claude/skills-config/ai-prototype-flow/` にコピーする。詳細は [`CONTEXT.md`](./CONTEXT.md) を参照。

## 開発ワークフローの推奨例

```
0. 未検証の仮定がある複雑機能なら /iterate-with-prototypes（code-first: 動かしてから設計し、設計書はコードから起こす。戻しにくいスキーマ/API契約が主リスクなら不適）
1. 設計してプランファイルつくる
2. 要件を精査する
3. /map-user-stories で US/Task に分解
4. /create-jira-issues で Jira へ一括登録
5. /define-acceptance-criteria で 受け入れ条件定義
6. /mece-plan-review で網羅性検証
7. /review-design で設計レビュー
8. /finalize-plan でブランチ・QA計画を策定
9. 実装（Figma 反映を含むなら /extract-figma-spec で全プロパティを抽出・照合し反映漏れを防ぐ）
10. /review-plan-diff でプランと実装 diff を突き合わせ、実装漏れ・計画外差異を検出
11. /qa-ui で UI 検証
12. /review-code-quality + /polish-before-commit で仕上げ
13. /create-pr でドラフトPR作成
```

## 出典

- grill-with-docs ... https://github.com/mattpocock/skills

## ライセンス

MIT。詳細は [`LICENSE`](./LICENSE) を参照。
