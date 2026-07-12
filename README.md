# skills

独立した plugin 群。必要な skill だけを選択的に install できる。

## クイックスタート

```bash
npx skills add YasuakiOmokawa/skills
```

対話で必要な skill を選んで install。

### 設定値の生成

続けてターミナルで設定値を生成:

```bash
bash ~/.claude/plugins/marketplaces/omokawa-skills/scripts/setup.sh
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

## AIプロトタイプ駆動開発ワークフローの推奨例

```
## フェーズ0: 技術調査 (候補出しまで)

技術候補の比較・リスク列挙はここまで。確定は spike に譲る
(実案件で調査結果の誤り 3 点を spike が訂正した。調査は仮説の候補リストであり結論ではない)。
調査結果はフェーズ1 の仮説 ledger の入力にする

## フェーズ1: PoC (使い捨て検証・速度優先)

prd から poc をつくりたい。/iterate-with-prototypes に従い、検証したい仮説を
「主張 / 検証方法 / kill 条件」の ledger にしてから spike して。
使い捨て前提なので AC/MECE/finalize のフル計画装備はこのフェーズでは省略

### Figma 再現度が検証対象の仮説に含まれる場合のみ
/extract-figma-spec で figma design をソースコードに反映して

/qa-ui を automation で実行して

仮説 ledger の各項目を grounded / killed / unverified で確定し、
「やらなかったこと」を列挙してプランファイルに記録して

PoC レビューで新しい要望・仮説が出たら、ledger に行を追加して同ブランチで
追加 spike する (フェーズ1 内で完結させる。例: 入力内容のリアルタイムプレビュー)

/create-pr    # draft + DONOTMERGE。merge しない参照用

## フェーズ2: 設計確定 (DD 用)

PoC の仮説 ledger (grounded/killed) と「やらなかったこと」各項目 → 対応先
(ADR / AC / 後続チケット) のマッピング表を作って、本実装設計の入力にして

固めた prd と PoC の学びを参考に本実装を設計。既存コードベースの慣習に従うよう設計して /grill-with-docs
/review-design

カレントブランチから新しくきって、設計書を /express-intent-in-code のガイドラインに
したがって実装。コミットは指示があるまで実施しない

/simplify
/vercel-react-best-practices
/vercel-composition-patterns
/review-code-quality
/express-intent-in-code
コードコメントと md ファイルに /dry-ssot-text → /purge-private-vocab
! npx react-doctor@latest --verbose --diff
/polish-before-commit

/create-pr    # draft。DD 確定用

## フェーズ2.5: DD 作成 → タスク分解

DD テンプレートとプロトタイプ PR に従い、DD 作成

DD に /dry-ssot-text → /purge-private-vocab   # レビュー依頼前に plan 造語を除染

(人間: DD レビュー → LGTM)

/map-user-stories で US / タスクに分解    # 出荷が複数 PR に跨るときのみ。1 タスク ≒ 1 vertical slice ≒ 1 PR
/create-jira-issues で Jira へ一括登録    # チケット運用するなら

## フェーズ3: 出荷実装 (2.5 で分解したタスクごとに 1 周まわす)

全スライスの進捗は progress-ledger (`<prd>.progress-ledger.md`) に追記して追跡する。
フル装備 (AC→MECE→finalize) は重篤度の高いスライスに限る。軽微なスライスは
AC/MECE/finalize を省略し、DD 該当タスクを転記した簡易プラン → 実装 →
/review-plan-diff → /qa-ui → 品質パス → /create-pr の fast path でよい

DD と該当タスクをもとに出荷用プランファイルをつくって /grill-with-docs
/define-acceptance-criteria
/mece-plan-review
/finalize-plan
/dry-ssot-text → /purge-private-vocab → japanese-writing.md と照合

プランファイルを /express-intent-in-code のガイドラインで実装。コミットは指示まで禁止
/review-plan-diff
/qa-ui

/simplify
/vercel-react-best-practices
/vercel-composition-patterns
/review-code-quality
/express-intent-in-code
コードコメントと md ファイルに /dry-ssot-text → /purge-private-vocab
! npx react-doctor@latest --verbose --diff
/polish-before-commit

/create-pr    # 正式な出荷 PR (ready for review)

※ /grill-with-docs ... https://github.com/mattpocock/skills
```


## ライセンス

MIT。詳細は [`LICENSE`](./LICENSE) を参照。
