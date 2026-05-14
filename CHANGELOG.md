# Changelog

All notable changes to omokawa-skills will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.7.0] - 2026-05-14

### Added

- **`/omokawa-skills:create-pr`: カレントブランチ妥当性検証ステップ (1.5) 追加**: PR 作成前に current branch が conventional prefix (`feature/`, `fix/`, `refactor/`, `docs/`, `chore/`, `test/`, `perf/`, `style/`, `ci/`, `build/`) を持つか / default branch と同名か / プロジェクト規約 (`.github/CLAUDE.md` 等) に合致するかを検証し、雑なブランチ名 (worktree 名等) や default branch にいる場合は変更ドメインから推定した `<type>/<scope>-<short-desc>` で `git switch -c` を自動実行する。コミット後の rename は GitHub Branch Rename API の副作用で関連 PR が CLOSED される事故が観測されたため、コミット **前** に切替する設計。`empirical-prompt-tuning` skill で 2 iteration 検証済 (iter 1 baseline accuracy 43% → iter 2 で全 3 シナリオ accuracy 100% + [critical] 全 ○、iter 3 で micro-fix を bundle 適用)。

## [0.6.0] - 2026-05-14

### Added

- **`dry-ssot-text` skill 新設 (engineering bucket)**: AI 生成長文を DRY/SSOT 形式に refactor する。必要重複 (TOC / progress table / checklist) と不要重複 (説明文の二重書き) を判定基準 table で識別、不要重複のみ canonical location (文書末尾 §設計詳細) に集約してアンカーリンクで参照置換する。実証例: 1074 行 plan を 328 行に圧縮。
  - `empirical-prompt-tuning` skill で 3 iteration 検証済 (Accuracy 3 連続 100%、新 unclear points は iter 2 以降 0 件で plateau 確認)。

### Fixed

- `.claude-plugin/marketplace.json` の version が `.claude-plugin/plugin.json` と乖離していた問題を解消 (両方 0.6.0 に統一)。

## [0.2.0] - 2026-05-06

### Added

- **Claude Code marketplace 形式対応**：`/plugin marketplace add YasuakiOmokawa/skills` で 1 行配布が可能に
  - `.claude-plugin/marketplace.json` 新規追加
  - 単一リポで marketplace + plugin を兼任する形式（anthropic-agent-skills と同パターン）
- **`scripts/setup.sh` 新規追加**：bash 経由で `~/.claude/skills-config/*.md` を対話生成
- **`examples/skills-config/`** に設定値テンプレート 3 ファイル
- **`CHANGELOG.md`**（このファイル）

### Changed

- **設定値の保管方式をグローバル化**：プロジェクトごとの `docs/agents/*.md` → ユーザーマシンごとの `~/.claude/skills-config/*.md`
- **skills フラット構造化**：`skills/<bucket>/<name>/SKILL.md` → `skills/<name>/SKILL.md`（Claude Code autodiscovery が 1 階層しか見ない仕様への対応）
- **commands フラット構造化**：`commands/<dir>/<name>.md` → `commands/<name>.md`（コマンド名の冗長表記 `:create-pr:create-pr` を解消）
- **`plugin.json` を簡素化**：skills/commands/agents 配列を削除（Claude Code はファイル構造から autodiscovery する）
- **README**：クイックスタートを `/plugin marketplace add` 方式のみに統一
- **CLAUDE.md / CONTEXT.md**：フラット構造前提に書き換え。「engineering / personal」は説明上の分類のみで、物理ディレクトリは廃止

### Fixed

- `plugin.json` と `marketplace.json` の version 不整合（0.1.0 / 0.2.0）を 0.2.0 に統一
- `agents/*.md` 内の `${CLAUDE_PLUGIN_ROOT}/skills/<bucket>/<name>/` パスを `${CLAUDE_PLUGIN_ROOT}/skills/<name>/` に修正

### Security

- **セットアップ時の機密値が AI のコンテキストに乗らない設計に変更**
  - 旧: `/setup-omokawa-skills` スラッシュコマンド（Claude が AskUserQuestion で値を受け取る → transcript / API ログに残留）
  - 新: `bash scripts/setup.sh`（bash の `read` で値を直接ファイル書き込み、Claude 介在ゼロ）
  - 対象: Jira Cloud ID, プロジェクトキー, MCP プレフィックス等

### Removed

- `commands/setup-omokawa-skills/` スラッシュコマンド（bash 化に伴い廃止）
- 他リポ参照（mattpocock らへの言及、`npx skills` 案）— このリポジトリだけ読めば自己完結する文書に
- `docs/agents/` ディレクトリ（`examples/skills-config/` に移動）
- `.gitignore` の `~/.claude/skills-config/*.md` 関連エントリ（リポ外パスなので不要）

### Verified

別 Claude Code セッションで実機検証済み:

- skill 呼び出し: `omokawa-skills:define-acceptance-criteria` ✓ Successfully loaded
- command 呼び出し: `/omokawa-skills:create-pr` ✓ 単一名で認識・実行
- agents 認識: 4 個（review-design / review-code-quality / finalize-plan / polish-before-commit）

## [0.1.0] - 2026-05-06

### Added

- 初版リリース。プラン駆動開発（spec → AC → MECE → finalize → implement → review）を支える skills 集として公開
- **Skills（11 個）**:
  - `define-acceptance-criteria` — プランに 4 カテゴリ × 観点マトリクスで AC を定義
  - `mece-plan-review` — AC に対し 3 視点（QA / Tech / Red Team）で MECE 検証
  - `finalize-plan` — プラン → 実装可能形式へ変換、4 サブエージェント並列
  - `review-design` — 設計判定、4 reviewer 並列（Clean Architecture / Hexagonal / DDD / Anti-pattern）
  - `review-code-quality` — 設計レベル品質、3 analyzer 並列（凝集度 / 結合度 / 可読性）
  - `polish-before-commit` — コミット前のパターン一貫性自動修正
  - `model-data` — 要求文書から DBML 形式の ER 図生成
  - `map-user-stories` — 設計書 / Jira epic から US/Task 分解
  - `qa-ui` — ChromeDevTools MCP で UI 検証、Generator-Evaluator 分離
  - `create-jira-issues` — Jira チケット一括作成
  - `set-jira-story-points` — Story Points 一括設定
- **Commands（1 個）**: `/create-pr`（Conventional Commits + テンプレ準拠 + ラベル自動付与）
- **Agents（4 個）**: review-design / review-code-quality / finalize-plan / polish-before-commit
- `scripts/`: `link-skills.sh`, `link-commands.sh`, `link-agents.sh`, `list-skills.sh`
- ライセンス: MIT

[0.2.0]: https://github.com/YasuakiOmokawa/skills/releases/tag/v0.2.0
[0.1.0]: https://github.com/YasuakiOmokawa/skills/releases/tag/v0.1.0
