# omokawa-skills を 1 plugin 1 skill 構造へ再編

**Status:** Draft
**Date:** 2026-05-14
**Author:** Yasuaki Omokawa

## 1. 目的・背景

**目的:** ユーザーが必要な skill だけを選択的に install できるようにする。

**現状の課題:**

- `omokawa-skills` 1 plugin に 13 skills + 1 command + 4 agents が同梱されている。Jira / ChromeDevTools / 個人 vision 関連など、利用者によっては不要な skill が常に同梱される。
- skill 単独で更新したくても plugin 全体の version が上がる。

**成功基準:**

- `/plugin install <skill>@omokawa-skills` で skill 単位の install が可能になる。
- 各 skill が独立した version を持つ。
- 既存ドキュメント (CLAUDE.md / CONTEXT.md / README.md) の意味する「リポジトリ全体観」は維持される。

## 2. スコープ / 非スコープ

**スコープ:**

- リポジトリレイアウトの再編 (1 plugin 1 skill 化)
- `marketplace.json` を 14 plugins 列挙形式へ書き換え
- 各 plugin に独立した `plugin.json` を配置
- 既存 `omokawa-skills` plugin エントリを `marketplace.json` から削除
- README に install 手順と、旧ユーザー向け移行手順 (`/plugin uninstall omokawa-skills`) を明記

**非スコープ:**

- skill 本文の改修 (内容は現状維持)
- skill 間の依存自動解決 (README/SKILL.md の文書示唆のみ)
- skill 名の改名

## 3. 全体ディレクトリレイアウト

```
omokawa-skills/                              # GitHub リポジトリ root
├── .claude-plugin/
│   └── marketplace.json                     # 14 plugins を列挙 (source: ./plugins/<name>)
├── plugins/                                 # 各 plugin 独立配置
│   ├── define-acceptance-criteria/
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/define-acceptance-criteria/SKILL.md
│   ├── mece-plan-review/
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/mece-plan-review/SKILL.md
│   ├── finalize-plan/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── skills/finalize-plan/SKILL.md
│   │   └── agents/finalize-plan.md          # 同梱
│   ├── review-design/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── skills/review-design/SKILL.md
│   │   └── agents/review-design.md
│   ├── review-code-quality/                 # 同上、agent 同梱
│   ├── polish-before-commit/                # 同上、agent 同梱
│   ├── model-data/
│   ├── map-user-stories/
│   ├── qa-ui/
│   ├── create-jira-issues/
│   ├── set-jira-story-points/
│   ├── translate-to-vision-story/
│   ├── dry-ssot-text/
│   └── create-pr/                           # command-only plugin
│       ├── .claude-plugin/plugin.json
│       └── commands/create-pr.md
├── scripts/setup.sh                         # 全 skill 共通の skills-config 生成
├── examples/skills-config/                  # サンプル設定
├── CLAUDE.md                                # 開発ガイド (更新)
├── CONTEXT.md                               # 用語集 (更新)
├── README.md                                # 利用者向け (更新)
├── CHANGELOG.md                             # 横断 changelog (簡素化)
└── LICENSE
```

**ポイント:**

- `${CLAUDE_PLUGIN_ROOT}` は各 plugin ディレクトリ (例 `plugins/review-design/`) に解決される。`${CLAUDE_PLUGIN_ROOT}/skills/<name>/<file>` の相対構造は不変なので、既存 agent からの skill 内ファイル参照はそのまま動く。
- `scripts/setup.sh` は plugin 外（リポジトリ root）に置く。利用者は `~/.claude/plugins/marketplaces/omokawa-skills/scripts/setup.sh` から実行 (現状の README と同じ案内)。

## 4. plugin.json と marketplace.json の構成

**各 plugin の `plugin.json` (例: define-acceptance-criteria):**

```json
{
  "name": "define-acceptance-criteria",
  "description": "プランモード中にプランファイルの受け入れ条件・技術リスクを定義する...",
  "version": "0.1.0",
  "author": { "name": "Yasuaki Omokawa", "url": "https://github.com/YasuakiOmokawa" },
  "homepage": "https://github.com/YasuakiOmokawa/skills",
  "repository": "https://github.com/YasuakiOmokawa/skills",
  "license": "MIT",
  "keywords": ["acceptance-criteria", "plan-driven", "qa"]
}
```

**`marketplace.json` (抜粋):**

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
      "description": "...",
      "version": "0.1.0",
      "source": "./plugins/define-acceptance-criteria",
      "category": "productivity",
      "homepage": "https://github.com/YasuakiOmokawa/skills",
      "license": "MIT"
    },
    { "name": "mece-plan-review", "source": "./plugins/mece-plan-review", "...": "..." },
    { "name": "create-pr", "source": "./plugins/create-pr", "...": "..." }
  ]
}
```

**version 戦略:**

- 各 plugin は `0.1.0` から開始する (新規 plugin として扱い、旧 `omokawa-skills` の `0.11.0` は引き継がない)。
- 旧 plugin の version 履歴は `CHANGELOG.md` 内に残し、新 plugin の version は独立採番。
- marketplace 全体の version は別軸 `1.0.0` で「再編メジャーリリース」を表現する。
- 以降 plugin 単位で SemVer 更新する。

## 5. 共有資源の配置と参照パス

| 資源 | 配置 | 参照方法 |
|---|---|---|
| `scripts/setup.sh` | リポジトリ root | README で `bash ~/.claude/plugins/marketplaces/omokawa-skills/scripts/setup.sh` を案内 |
| `examples/skills-config/*.example.md` | リポジトリ root | README から相対リンク |
| `CLAUDE.md` | リポジトリ root | 開発ガイド (新レイアウトを反映して全面改訂) |
| `CONTEXT.md` | リポジトリ root | 用語集 (内容ほぼ維持、配置の説明だけ更新) |
| `README.md` | リポジトリ root | install 手順を「個別 install ベース」に書き換え |

**SKILL.md からの skills-config 参照は不変:** 各 skill は `~/.claude/skills-config/<name>.md` を Read で取得する記述を維持する。setup.sh が生成する config ファイルは全 plugin から共通参照される。

**`${CLAUDE_PLUGIN_ROOT}` 参照:** plugin 内のパスは `${CLAUDE_PLUGIN_ROOT}/skills/<name>/...` のまま。plugin root が `plugins/<name>/` に解決されるだけで相対構造は崩れない。

## 6. 依存関係の表現

- 各 SKILL.md に「**併用推奨 skill:**」セクションが未記載なら追加する (既存 description 内に `/<skill>` 参照がある場合はそれを活かしつつ、本文に明示セクションを設ける)。
  - 例 (define-acceptance-criteria): 「`/mece-plan-review` で AC の網羅性検証、`/finalize-plan` で実装準備フェーズ移行」
- README に「推奨セット」を明示する。
  - **プラン駆動 7-skill セット:** `model-data`, `map-user-stories`, `define-acceptance-criteria`, `mece-plan-review`, `review-design`, `finalize-plan`, `polish-before-commit`
  - **Jira セット:** `create-jira-issues`, `set-jira-story-points`
  - **キャリアセット:** `translate-to-vision-story`, `dry-ssot-text`
  - **単独動作:** `qa-ui`, `review-code-quality`, `create-pr`

`plugin.json` には依存定義を書かない (公式仕様未確認 + メンテ複雑化を避ける)。install は完全にユーザー判断。

## 7. 移行戦略

**即時廃止方針:**

1. `marketplace.json` から旧 `omokawa-skills` エントリを削除し、14 plugins へ差し替える。
2. README に「**重要: 旧 `omokawa-skills` plugin を install 済みの方へ**」セクションを冒頭に追加する。

   ```
   /plugin uninstall omokawa-skills@omokawa-skills
   /plugin marketplace update omokawa-skills
   /plugin install <必要な skill>@omokawa-skills  # 個別 install
   ```

3. `CHANGELOG.md` に移行リリースとして `2.0.0 (BREAKING)` を記録する。
4. PR description に明確に「破壊的変更: 旧 omokawa-skills は廃止」と書く。

## 8. 残るオープン論点 (実装時に判断)

- `CHANGELOG.md` の形式: 横断 1 ファイルで「v2.0.0 - <skill>: ...」とフラットに並べる方針 (現状維持を簡素化)
- 移行 PR を skill 単位で細分化するか、1 つの巨大 PR で出すか → `finalize-plan` skill のガイドに従い実装時に決定する。

## 9. 検証ターゲット

実装後の動作確認で押さえる項目:

- `marketplace add YasuakiOmokawa/skills` で 14 plugins が listing に表示される。
- 各 plugin の単独 install が成功し、対応する skill / command が discovery される。
- agent を呼ぶ skill (`review-design`, `review-code-quality`, `finalize-plan`, `polish-before-commit`) で `${CLAUDE_PLUGIN_ROOT}` 解決が正しく動く。
- `bash ~/.claude/plugins/marketplaces/omokawa-skills/scripts/setup.sh` が新レイアウト下でも実行できる。
- 旧 `omokawa-skills` plugin を install 済みの環境で `marketplace update` 後に旧 plugin が表示されない (= 既存ユーザーは uninstall が必要であることを認識できる)。
