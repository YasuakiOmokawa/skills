# Changelog

All notable changes to omokawa-skills will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## v7.0.0 - 2026-08-16

### Changed

- **`qa-ui` 2.0.0 (BREAKING):** 利用者が選ぶ Manual / Automation / Orchestrated モードを廃止。QA-ID source がある場合は `finalize-plan` の `manual` / `auto` 手段をそのまま実行し、QA-ID source がない場合だけ browser fallback を使う。
- Orchestrated 用 escalation ledger、held ID、browser 生成 QA-ID を削除し、QA ledger は初期化・auto command gate・完了集計に限定。QA-ID なし fallback と委譲時の handoff 境界は維持した。
- ルートの agent 指示を Claude Code と Codex で共有するため、`AGENTS.md` を `CLAUDE.md` への相対 symlink として追加した。

## v6.3.0 - 2026-08-15

### Changed

- 15 skills を frontier-model 向けに縮約し、重複説明・履歴・実行環境固有の制御を削減。判断境界と安全ゲートを自己完結させた。
- 各 skill の fixed regression を fresh executor で再検証し、description・plugin metadata・marketplace metadata を現行契約へ同期した。

## v3.100.0 - 2026-08-08

### Changed

- **`finalize-plan` skill: eval 繰り越し 10 件を消化 (2.10.0 → 2.11.0)**: PR #139 の fresh executor 再実行で観測した spec gap 10 件を、薄い規則 (表記の SSOT 整合・1〜2 行の規則・位置宣言) だけで消化した。表記 SSOT 整合: Step 1.7 の `0/0` という独自略記 (テンプレに実在せず executor が redo した) を output-template.md の `カテゴリ名+0` へ統一。lite tier の下流規定: 自動QA サブセクションは節ごと落とさず `自動QA: lite tier のため対象外 (auto 0 件)` の 1 行を残し (canonical 文言は output-template.md)、Step 4 は auto 0 件を正常扱いとする。代行時に `agents/manual-qa-planner.md` を Read する手続き (in-context fallback と同一) も明記。位置 SSOT: Step 3.5 のゲート結果行は「手動QA手順の末尾 = `### 自動QA` 見出しの直前」と output-template.md で宣言し、SKILL.md は参照のみ。
- **孤児 QA-ID を完了ブロック側へ**: manual/auto どちらの planner 出力にも載らない QA-ID の初期状態を `対象外(N/A)` (完了集計で許容) から手段 `-`・状態 `要人間確認` (許容されない) へ変更。割当漏れで実際に落ちた AC が黙って完了判定を通る穴を塞ぐ。`要人間確認` は qa-ui の完了判定 Bash (終端状態は `PASS` / `検証不能(真の制約)` / `対象外(N/A)` のみ) がそのままブロックするため、qa-ui 側の変更は不要。
- **照合・判定の曖昧さ解消ほか**: planner が出した検証内容が enumerate 元 AC と対応しない QA-ID は統合せず `要人間確認` に回す規則を Step 3 に追加 (QA-ID だけ合っていて中身がすり替わる経路は既存ゲートが素通しするため)。Step 3.5 の「実質同一」判定はプラン本文を対象とすると明記。Step 1.5 の ledger 駆動例外に固定の終了メッセージを追加 (従来は出力未定義の分岐だった)。⛔ 中断メッセージ 3 行目を「分析ファイルを一度も作っていない場合」に限定し、AC 済み・MECE 未了のプロトタイプ先行ユーザーを ledger 代替へ差し戻さないようにした。preflight は権限用途の逆算補完 (逆算元 QA-ID が特定できる範囲) とセル注記禁止 (後段が機械的に読む表のため) を明文化。evals/regression.md は孤児 QA-ID の assertion を追随更新 (シナリオ追加なし)。

## v3.99.0 - 2026-08-08

### Changed

- **`finalize-plan` skill: ブランチ戦略ロールを廃止 (2.9.0 → 2.10.0)**: Step 2A (起点ブランチ確定 + 作業ブランチ命名 + 重複チェック) と `## 実装準備` の `### ブランチ戦略` 出力サブセクション (新規作成形式・カレント継続形式の 2 テンプレ) を撤去し、Step 2B を Step 2 へ改称した。実装開始時に「カレントブランチから新しく切って実装」と指示すれば足り、事前のブランチ計画は欠陥検出に寄与しないため (利用者決定 2026-08-08)。2026-08-02 の branch-planner インライン化に続く簡素化で、`## 実装準備` は 手動QA手順 / 自動QA（テストコード仕様） の 2 サブセクションになった。
- **preflight の 起点ブランチ 欄は存置し、供給元だけ差し替え**: `/review-plan-diff` がこの欄を diff 比較元として読む (git 参照は禁止されている) ため欄自体は残し、Step 5 が `git branch --show-current` の値を機械転記する方式に変更 (判断・命名は行わない。detached HEAD 等で取得できない場合は `未定` として既存の AskUserQuestion 一括確認へ流す)。
- **連動更新**: `iterate-with-prototypes` (0.18.0 → 0.19.0) の ledger 駆動フォールバックを「ブランチ戦略 + QA 手順の 2 点」→「QA 手順」へ、`define-acceptance-criteria` (0.31.0 → 0.32.0) の併用推奨記述を「ブランチ・QA 手順を起こす」→「QA 手順を起こす」へ。両 plugin の evals/regression.md の該当 assertion も新仕様へ移行。finalize-plan の trigger から「ブランチ戦略を決めて」を削除。

## v3.98.0 - 2026-08-08

### Added

- **setup.sh Section E + `scripts/register-redundancy-guard-hook.sh`: redundancy-guard hook の settings.json 登録を自動化**: plain skill インストールで運べない唯一のマシンローカル要素だった PostToolUse 配線 (`~/.claude/settings.json`) を、対話セットアップの Section E または単体スクリプトで登録できるようにした。冪等 (登録済み検知)・非破壊 (jq 検証 → .bak 退避 → atomic mv)・不正 JSON は無変更で中止・settings 未存在時は新規作成。`CLAUDE_SETTINGS` で対象を差し替え可能 (テスト用)。これで新マシン導入は「skills install → setup.sh (または register スクリプト単体)」に閉じる。検証: fixture 6 種 (hooks なし / Stop のみ / 他 PostToolUse あり / 登録済み / 不正 JSON / ファイル無し) + 実 settings への冪等 no-op を確認。

## v3.97.0 - 2026-08-08

### Changed

- **`express-intent-in-code` skill: redundancy-guard.sh を skill 配下 `scripts/` へ収容し repo 管理化 (0.21.0 → 0.22.0)**: これまで `~/.claude/hooks/` 置きだった PostToolUse hook スクリプトを `skills/express-intent-in-code/scripts/redundancy-guard.sh` に移し、`skills update` で各マシンの `~/.agents/skills/express-intent-in-code/scripts/` へ配布されるようにした。user settings の hook コマンドは installed パスを `bash` 起動する形へ切替済み (exec bit 不問)。旧 `~/.claude/hooks/redundancy-guard.sh` は削除。マシンローカルに残るのは settings.json の配線 1 ブロックのみ (plain skill インストールは hook 登録を運べないため。新マシン導入 = skills install + settings 追記の 2 ステップ)。切替後の発火は live-fire で確認済み。

## v3.96.0 - 2026-08-08

### Changed

- **`express-intent-in-code` skill: ponytail 由来の「書く前の再利用梯子」を追加 (0.20.0 → 0.21.0)**: 新しい関数・ヘルパー・ファイルを書く前に ⓪要るか → ①codebase に既にあるか (隣接 grep) → ②言語標準 → ③プラットフォーム標準 → ④導入済み依存 → ⑤最小コード、を最初に該当した段で打ち切る 6 行を新設 (DietrichGebert/ponytail の ladder を翻案、MIT)。suppression を書きたくなったら①へ戻る接続も明記。description に new-file / before-writing トリガーを追加 (SKILL.md 42→48 行)。対の検知として user settings の redundancy-guard hook に「未追跡ファイル + 同 dir 同拡張子の隣接あり」で 1 回だけ `[reuse-ladder]` を注入する検出を追加。根拠: PR 40148 実測の再発明 4 件 (Capybara.string 不使用 / セレクタだけ違う複製関数 / 既存 pushText 再インライン / shared_examples 不使用) は全て梯子①で止まるべきケースで、5 スキルの誰も所有していなかった。`empirical-prompt-tuning` 2 シナリオ (再利用誘惑 / 移植回帰) で検証: 誘惑側は bias-free executor が書く前に梯子を自己適用し既存ヘルパー 2 本を import (複製ゼロ)、回帰側は純化健在。全 [critical] ○。
- **申し送り**: 既存ファイル内へのコピペブロック追加 (shared_examples ケース) は新規ファイル検知に掛からない — コミット時/CI 層 (バイト一致検知・dry-ssot-text 配線) が未実装の宿題。移植回帰で JSDoc 形式のやや長い why 文面が観測された (非クリティカル、文面は code-comments 7 原則の管轄)。

## v3.95.0 - 2026-08-08

### Changed

- **`express-intent-in-code` skill: 限界薄化 + 発火のハーネス移管 (0.19.0 → 0.20.0, BREAKING)**: SKILL.md を 163 行 → 42 行へ書き直し、references 8 本 (decision-procedure / generation-recipe / technique-catalog 等、計 ~760 行) と agents/intent-reader.md を撤去 (git 履歴に保存。ローカル退避: `~/.agents/skills/.archive/express-intent-in-code-v0.19/`)。残したのは判断規範のみ — 命名梯子 (造語禁止・caller 観測)、コメント昇格先マップ、真の why 4類型の残置基準、歯止め (drive-by 禁止・**n=1 は既存再利用 / rule of three は新抽象** の tie-break を新設)、fresh-eyes 検証。description は 1,048 → 356 chars (trigger-only)。
- **発火責務の分離**: 経路2 (生成時) の発火は user settings の PostToolUse hook (`redundancy-guard.sh`) が決定論的に担う — Edit/Write ごとに diff からコメント追加 / lint-suppression 追加を検知し、本スキルの適用指示を stderr (exit 2) で model へ自動注入する (セッション×ファイル単位の増分 dedup 付き)。根拠: SIGNPBL-103 の transcript 検証で、スキルが実装時に起動・全文ロード済みでも冗長コメントを生成し、効いたのはレビュー時の機械測定だけと判明 (CONTENT LIMIT)。プロンプト量はモデルの推論性能を奪うため、手続き記述を捨て検知をハーネス層へ移した。
- **申し送り**: 薄化後の empirical eval 未実施 (evals/regression.md の A/B 記録は旧 v0.8.0 構成のもの)。batch 起動時の 3 兆候スクリーニング (多義衝突 / 段0 ノイズ語) と出力フォーマット・委譲実行節は撤去 — 必要になった場合は hook 側の検知拡張で対応する方針。

## v3.94.0 - 2026-08-07

### Changed

- **`finalize-plan` skill: Figma 正本の未抽出検知 (能動ゲート) を Step 1.5 に追加 (2.8.0 → 2.9.0)**: プラン/DD 本文に Figma URL があるのに分析ファイルへ `## 正本抽出結果` が無い場合、警告して `/extract-figma-spec` の先行実行を提案する (委譲実行では要人間確認項目に含めて続行)。受動的な併用推奨だけでは実行が飛ばされ、実装後の Figma 照合で 24 atom 中 7 差分・2 ラウンドの手戻りが発生した実測に基づく。あわせて Gotchas に「QA planner への dispatch prompt で列構成を独自指定しない (qa-ui 審判ゲートの 6 列契約が壊れる)」を追記。`empirical-prompt-tuning` で 2 シナリオ (発火系 / 誤発火なし系) を検証し全 [critical] ○、accuracy 100%。
- **申し送り (今回未修正の既知課題)**: 分析ファイル内 Tier 表記の競合解決規則なし / 正本カバレッジ skip 行文言の SSOT 不一致 (SKILL.md・coverage-gate-bash・output-template) / lite tier と Step 3 テンプレ・Step 4 割当の整合未定義 / dual coverage 規則で manual 行が全消滅するケース / preflight の 未定 vs 該当なし の適用順。empirical 検証の executor 申告から採取。

## v2.2.0 (BREAKING for map-user-stories consumers) - 2026-05-15

### Changed

- **`map-user-stories` skill: タスク TSV カラム構造を再設計 (0.1.0 → 0.2.0, BREAKING)**: 旧フォーマットの「説明」列にプレフィックス記法（`完了条件: ` / `AC: `）を、「備考」列に `やらない: ` / `対象外: ` を書く運用を廃止し、専用列 `やること / やらないこと / 完了条件` の 3 列を新設。タスク TSV は 7 列 → 9 列に拡張。カラム順は Jira description のセクション順（`着手条件 → やること → やらないこと → 完了条件`）に揃え、`US_ID	Task_ID	タスク名	やること	やらないこと	完了条件	依存タスク	Jira	備考` とする。「備考」列は Ready 条件・参考リンク等の自由テキスト枠として残置（プレフィックス禁止）。US テーブル側の「技術メモ」列はプレフィックス記法を維持（後方互換）。`empirical-prompt-tuning` で 2 シナリオ（中規模 DD / 小規模仕様）を subagent 派遣検証して全 [critical] ○、accuracy 100%。
- **影響範囲**: `create-jira-issues` 側のパース仕様は別途追従が必要（タスク description の「やること」「やらないこと」「完了条件」の抽出元列名が変わる）。`map-user-stories` から出力された旧 7 列フォーマットのファイルは `create-jira-issues` で正しくパースされなくなる可能性があるため、本 bump 以降は新フォーマットでの再生成を推奨。

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

## [0.8.0] - 2026-05-14

### Added

- **`polish-before-commit` skill: Dead mock 削除ステップ (Step 6) 追加**: 実装側で `delegate :X` / `def X` を撤去した PR で、spec の対応 mock (`receive(:X)` / `receive_messages(X:)` / `instance_double(..., X:)` / `double(..., X:)`) が残置していないか検証し、orphaned mock を user 承認後に削除する。CI も lint も検出できない「dead mock 残置」によるレビュー差し戻しを構造的に防ぐ。
  - 削除単位の分類 (auto / Manual Review) を明文化: `receive(:X)` 単独 + `receive_messages` 全 key 削除済 → auto / `receive_messages` 部分削除 → Manual Review (書換え候補併記可)。
  - 同一 PR 内で同名 method が `+` で再追加されている場合は除外する exclusion ロジック。
  - 編集後は触った spec 全件を `bundle exec rspec <file1> <file2> ...` で検証し 0 failures を確認。
  - 非 Ruby プロジェクト (`*.rb` 変更なし or `spec/` 不在) では `[dead mock: スキップ (Ruby/RSpec 対象外)]` を最終レポートに明記してスキップ。
- `empirical-prompt-tuning` skill で 3 iteration 検証: median / partial-removal / non-Ruby-skip の 3 シナリオで Accuracy 100%、iter 3 で plateau。出典: 社内プランのレビュー指摘。

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
