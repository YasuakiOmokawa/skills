# omokawa-skills 用語集

このリポジトリで頻出する独自用語の定義。スキル本文を読む前提知識として参照。

## プラン駆動開発

このリポジトリのスキル群は「**プラン駆動開発**」（plan-driven development）を前提に設計されている。Claude Code のプランモードで設計を立て → 受け入れ条件を定義 → MECE 検証 → 実装準備 → 実装、という流れ。

## プランファイル / 分析ファイル

**プランファイル**: Claude Code のプランモードで作成される `<name>.md` ファイル。設計判断・実装手順・受け入れ条件などが書かれる。

**分析ファイル**: プランファイルと対になる `<name>.analysis.md` ファイル。MECE 検証結果やリスク分析など、**プランファイル本文を肥大化させたくないメタ情報**を退避する場所。

両者の役割分離は `define-acceptance-criteria` と `mece-plan-review` の前提。

## AC（受け入れ条件）

**AC** = Acceptance Criteria。プランファイル内の `## 受け入れ条件` セクション。`define-acceptance-criteria` スキルで「正常系/異常系/エッジケース/非影響確認」の4カテゴリ × 観点列のマトリクス形式で定義する。

`mece-plan-review` の検証ターゲット、`finalize-plan` の QA 計画の入力になる。

## MECE 検証

**MECE** = Mutually Exclusive, Collectively Exhaustive。AC の網羅性を3視点（QA / Tech / Red Team）で検証する。`mece-plan-review` の主目的。

## サブエージェント / 並列起動

メインエージェントが複数の **specialist エージェント** を `Task` ツールで並列起動して結果を統合する設計パターン。
- `review-design`: 4 reviewer 並列（Clean Architecture / Hexagonal / DDD / Anti-pattern）
- `review-code-quality`: 3 analyzer 並列（Cohesion / Coupling / Readability）
- `finalize-plan`: 4 planner 並列（Branch / PR-split / Manual-QA / Auto-QA）
- `model-data`: パイプライン式（Requirements → Conceptual → Logical → DBML）

## ~/.claude/skills-config/*.md

**ユーザーマシンに 1 セットだけ存在するグローバル設定**の保管場所。`/setup-omokawa-skills` で初期生成。**全プロジェクト横断**で参照される（プロジェクトを切り替えても同じ設定が効く）。**機密ではない**前提（テナント識別子レベル）。

- `jira.md` — Jira Cloud ID, プロジェクトキー, MCP プレフィックス
- `release-labels.md` — Productivity / AI Contribution / Release Level ラベル定義
- `environments.md` — integration 環境名（rollback 対象）

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

`qa-ui` / `mece-plan-review` で採用するパターン：**実装したエージェント自身では評価しない**。別コンテキストの evaluator エージェントが画面/プランを見て判定する。バイアスを避けるため。
