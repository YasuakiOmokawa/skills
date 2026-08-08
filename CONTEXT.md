# omokawa-skills 用語集

このリポジトリで頻出する独自用語の定義。スキル本文を読む前提知識として参照。

## リポジトリ構造

omokawa-skills は **monorepo + N plugins** 構造。各 skill / command は `plugins/<name>/` 配下の独立 plugin として配置される。`marketplace.json` が全 plugins (現在 22) を列挙する。詳細は CLAUDE.md 参照。

## プラン駆動開発

このリポジトリのスキル群は「**プラン駆動開発**」（plan-driven development）を前提に設計されている。Claude Code のプランモードで設計を立て → 受け入れ条件を定義 → MECE 検証 → 実装準備 → 実装、という流れ。

## プランファイル / 分析ファイル

**プランファイル**: Claude Code のプランモードで作成される `<name>.md` ファイル。設計判断・実装手順・受け入れ条件などが書かれる。

**分析ファイル**: プランファイルと対になる `<name>.analysis.md` ファイル。MECE 検証結果やリスク分析など、**プランファイル本文を肥大化させたくないメタ情報**を退避する場所。

両者の役割分離は `define-acceptance-criteria` と `mece-plan-review` の前提。

## プロトタイプ駆動 3 スキル (build-poc / build-prototype / create-design-doc)

- **案件** — 1 つのやりたいこと (機能・改善) を PoC → プロトタイプ → DD へ進める単位
- **案件ディレクトリ** — 案件プランファイル・凍結スナップショットの置き場。既定は `~/.claude/prototyping-projects/<案件名>/`
- **案件プランファイル** — `plan_<案件名>.md`。案件のメタ情報・星取表・申し送り節を 1 ファイルに集約する (進捗管理と再入は人力。プランモードの「プランファイル」と同一ファイルになることもある)
- **星取表** — 実現方式の候補 × 評価軸の表。セルは ◯/△/✕ + 根拠。最小実装の裏どりで (未検証) を実測根拠に置き換える
- **申し送り節** — スキル間の受け渡し契約。`## 申し送り (PoC → プロトタイプ)` / `## 申し送り (プロトタイプ → DD)` の見出し文字列は固定、本文は自由形式

## AC（受け入れ条件）

**AC** = Acceptance Criteria。分析ファイル (`<plan>.analysis.md`) 内の `## 受け入れ条件` セクション。`define-acceptance-criteria` スキルで「正常系/異常系/エッジケース」の必須 3 カテゴリ (+ 推奨カテゴリ「非影響確認」) × 観点列のマトリクス形式で定義する。プランファイル末尾の `## 品質検証` には 1 行サマリーだけが追記される。

`mece-plan-review` の検証ターゲット、`finalize-plan` の QA 計画の入力になる。

## MECE 検証

**MECE** = Mutually Exclusive, Collectively Exhaustive。AC の網羅性を BB (仕様) / WB (コード) の 2 視点 + Fresh Red Team で検証する。既定 (standard tier) は main agent が BB+WB を inline 実行し、Critical 候補が出たときだけ Fresh Red Team を dispatch。リスク領域・AC >15 件 (deep tier) は BB / WB を並列 subagent 起動し Red Team 必須。Wiki Researcher (Devin) はユーザー明示 opt-in 時のみ参加する。`mece-plan-review` の主目的。

## サブエージェント / 並列起動

メインエージェントが複数の **specialist エージェント** を `Task` ツールで並列起動して結果を統合する設計パターン。
- `review-design`: anti-pattern 必須 + DDD / Hexagonal / Clean / Deep-Module から Q1-Q3 matrix で選ばれた subset を並列起動 (unhealthy・新規 module・greenfield では all 5) → 必須 Devil's Advocate critique
- `review-code-quality`: 3 analyzer 並列（Cohesion / Coupling / Business-Impact — Business-Impact は domain attribute 変更時のみ）
- `finalize-plan`: Manual-QA / Auto-QA の 2 並列
- `mece-plan-review`: 既定 (standard) は subagent 0 で main agent が inline 実行。deep のみ BB / WB 2 並列 (Wiki Researcher opt-in 時 3 並列) → Fresh Red Team の統合判定
- `model-data`: パイプライン式（Requirements → Conceptual → Conceptual-Review (FAIL 時 Conceptual へ差し戻し、最大 3 回) → Logical → DBML）
- `qa-ui`: automation モード時のみ ui-evaluator を独立コンテキストで起動

## ~/.claude/skills-config/*.md

**ユーザーマシンに 1 セットだけ存在するグローバル設定**の保管場所。`bash scripts/setup.sh` で初期生成。**全プロジェクト横断**で参照される（プロジェクトを切り替えても同じ設定が効く）。**機密ではない**前提（テナント識別子レベル）。

- `jira.md` — Jira Cloud ID, プロジェクトキー, MCP プレフィックス
- `release-labels.md` — Productivity / AI Contribution / Release Level ラベル定義
- `environments.md` — integration 環境名（rollback 対象）
- `create-design-doc/` — create-design-doc が参照する DD テンプレート・実例（組織の内部文書のためリポジトリには置かない。setup.sh が手元のファイルをコピーして配置）
- `vision.md` — translate-to-vision-story が照合するビジョン要素 (テンプレートは plugin 内 references/vision-config-template.md)
- `mece-plan-review.md` — Wiki Researcher の関連リポ探索に使う github_org (未設定なら git remote から推定)

スキル本文では「このファイルを Read で取得」と書き、ハードコードしない。

## 真の機密 vs グローバル設定 vs プロジェクト固有値

| 種類 | 例 | 保管場所 |
|---|---|---|
| 真の機密 | API トークン、シークレット | `.env` + bash 経由（このリポジトリでは扱わない） |
| グローバル設定 | Jira Cloud ID, ラベル名, 環境名 | `~/.claude/skills-config/*.md`（マシンユーザーごと、全プロジェクト共通） |
| ユーザー個人の好み | 自分のテストアカウント、エディタ設定 | `~/.claude/CLAUDE.md` |
| プロジェクト固有値 | プロジェクトのドメイン用語、CI 構成 | プロジェクト内の `CLAUDE.md` |

## MCP プレフィックス

Atlassian MCP / Jira MCP のツール名は環境によってプレフィックスが異なる：
- `fdev-jira`, `fdev-atlassian-v2`（特定組織の MCP 命名）
- `atlassian` (Atlassian 公式)
- `claude_ai_Atlassian` (Claude.ai 連携)

スキル本文では `<jira-mcp>` / `<atlassian-mcp>` プレースホルダーで記述し、実値は `~/.claude/skills-config/jira.md` から取得する。

## Generator-Evaluator 分離

`qa-ui` / `mece-plan-review` で採用するパターン：**実装したエージェント自身では評価しない**。別コンテキストの evaluator エージェントが画面/プランを見て判定する。バイアスを避けるため。(ただし qa-ui の既定は人間委譲で、evaluator エージェントによる判定は automation モード時のみ。人間委譲でも「実装者自身が判定しない」原則は同じ)
