---
name: review-design
description: 新機能の実装開始前、ファイルやモジュールの追加時、「このコードはどこに置くべきか」と迷った時に使用。
---

# My Code Design

## Quick Start: 3つの質問

```
Q1: 類似機能はどこにある？
    │
    ├─ 見つかった → Q1.1: その類似機能は健全か？
    │     │
    │     ├─ 健全 → 同じパターンで作れ。→ anti-pattern-checker のみ起動
    │     │   （健全の条件: テストあり、責務明確、行数200以下、publicメソッド10以下）
    │     │
    │     └─ 不健全 → 新パターンを検討。改善案もレビュー結果に含めよ。→ 全Reviewer起動
    │         （不健全の兆候: テストなし、God Class化、行数300+、コールバック3つ以上連鎖）
    │
    └─ 見つからない → Q2 へ
        │
        ▼
Q2: 責務は一言で言えるか？
    │
    ├─ 言える → そのまま1ファイルで実装。Q3 へ。
    │
    └─ 「〜と〜」になる → 分割してから Q3 へ
        │
        ▼
Q3: テストしやすいか？（依存を差し替えられるか？）
    │
    ├─ Yes → 実装開始。
    │
    └─ No → 依存を引数/DI で注入できる設計に修正
```

### 判断例

| ケース | Q1 | Q1.1 | Q2 | Q3 | 結論 |
|--------|----|----|-----|---|------|
| 新しい Service 追加 | `app/services/` に類似あり | テストあり、80行 | 「契約を作成する」| mock可 | 類似に従って実装 |
| 複雑なビジネスロジック | 類似なし | — | 「検証と通知と保存」| — | 3つに分割してから実装 |
| 外部API連携 | 類似なし | — | 「Slack通知する」| 外部依存あり | Adapter パターン検討 → 詳細ワークフローへ |
| 既存パターンに問題あり | 類似あり | テストなし、400行のGod Class | — | — | 新パターン検討 + 改善提案 |

## Arguments

- `$ARGUMENTS`: 実装予定の機能説明（省略可）
  - 指定あり: 指定された機能についてアーキテクチャ適合を確認
  - 指定なし:
    1. プランモードの場合: Plan File Info からプランファイルを読み込み
    2. プランファイルがない場合: 会話コンテキストから判断

## Step 0: 対象の特定

引数が指定されていない場合、以下の順序で対象を特定:

1. **プランモード判定**
   - 会話コンテキスト内に `Plan File Info:` セクションがあるか確認
   - あれば、パスを抽出（例: `/home/user/.claude/plans/xxx.md`）

2. **プランファイル読み込み**
   - 抽出したパスのファイルを Read ツールで読み込み
   - 設計内容を把握

3. **フォールバック**
   - プランファイルがない/読み込めない場合 → 会話コンテキストから判断

## Parallel Review Workflow

### Step 1: Quick Start Questions (Q1-Q3)

まず Q1-Q3 を実行し、設計の方向性を決定する。

### Step 2: Reviewer Selection

Q1-Q3の結果に基づき、適切なReviewerを選択する。

```
┌─────────────────────────────────────────────────────────────┐
│                    Reviewer Selection Matrix                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Q1: 類似機能あり + Q1.1: 健全                              │
│    └─→ anti-pattern-checker のみ                            │
│                                                              │
│  Q1: 類似機能あり + Q1.1: 不健全                            │
│    └─→ 全 Reviewer を並列起動                               │
│                                                              │
│  Q1: 類似なし + Q2/Q3 判断                                   │
│    │                                                         │
│    ├─ 複雑なビジネスルール                                   │
│    │   └─→ ddd-reviewer + anti-pattern-checker              │
│    │                                                         │
│    ├─ 外部依存あり（API/DB差し替え必要）                     │
│    │   └─→ hexagonal-reviewer + anti-pattern-checker        │
│    │                                                         │
│    ├─ 新規設計（レイヤー検討必要）                           │
│    │   └─→ clean-architecture-reviewer + anti-pattern-checker│
│    │                                                         │
│    └─ 複合ケース                                             │
│        └─→ 該当する全 Reviewer を並列起動                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Step 3: Parallel Task Invocation

選択された Reviewer を Task ツール（`subagent_type: "general-purpose"`）で**並列起動**する。各 Reviewer の agent ファイル（`agents/*.md`）を読み込ませ、設計判断の内容を渡すこと。

**現時点の Reviewer 一覧** (「全 Reviewer」とはこの 4 種を指す):
- `anti-pattern-checker` — 全レビューで必須
- `ddd-reviewer` — ビジネスルール観点
- `hexagonal-reviewer` — 外部依存の差し替え観点
- `clean-architecture-reviewer` — レイヤー分離観点

**Task ツールが利用不可な環境** (既に subagent として動作中 / tool が deferred / dispatch 権限なし):
1. 該当する `agents/*.md` を Read で直接読み込む
2. 本 agent 自身がその判定基準を適用し、Reviewer ごとの判定結果を**内部処理として** Devil's Advocate 判定に渡す（ユーザーへは中間出力しない）
3. 最終報告本文末尾に `(in-context 代替モード: <代替した reviewer 名>)` と1行だけ明記する（独立視点での検証という本来の意図が失われるため透明性を確保）

### Step 4: プランファイルへの反映

各 Reviewer の結果を統合し、**問題があればプランファイルを直接修正する**（Edit ツール使用）:
- ファイル配置の変更 → プランの該当セクションを書き換え
- 責務分割が必要 → プランにファイル分割を反映
- パターン変更 → プランの設計方針を修正

**重要**: 分析サマリやレポートをプランに貼り付けない。プランの設計自体を修正すること。

最終報告フォーマットは **「Step 5: Devil's Advocate レビュー」節 → 最終報告フォーマット** に合流させる（Step 4 時点で報告を出さない）。Devil's Advocate を必ず通してから報告する。

### Step 5: Devil's Advocate レビュー（必須・標準フロー）

Parallel Review 後、Task ツール（`subagent_type: "general-purpose"`）で設計判断への反論を生成する。Task 不可環境では Step 3 と同じく in-context で本 agent が反論を生成する（代替モード明記）。

**指示内容**: 反対意見を3つ挙げ、各意見を「致命的（設計変更すべき）」か「許容可能（理由つき）」で判定。見落としている前提も指摘。

**致命的判定の基準**（これに該当するもののみ「致命的」。主観的な好みは「許容可能」）:
- `agents/anti-pattern-checker.md` の判定表で ❌ に該当
- DB トランザクション境界違反（例: コールバック内で外部API呼び出し）
- 並行性 / 冪等性の欠陥（例: レースコンディション、二重通知）
- セキュリティ脆弱性（例: 個人情報の平文保存、認証バイパス）
- 既存契約違反（例: 既存 interface の破壊、後方互換性喪失）

**フィードバックループ**: 「致命的」判定があれば以下を実行:
1. Edit ツールでプランファイルの該当箇所を修正
2. 修正後に再度 Parallel Review (Step 2-4) を実行して検証
3. 全項目が「許容可能」になるまで繰り返す

### Step 6: 最終報告フォーマット（Parallel Review + Devil's Advocate の合流）

最終的なプランファイル変更の有無で分岐する（Devil's Advocate で致命的判定が出て Edit した場合は「問題ありルート」）:

- **問題なしルート** (Parallel Review ✅ かつ Devil's Advocate 致命的 0 件):
  ```
  設計レビュー完了。問題なし。
  ```
- **問題ありルート** (Parallel Review ❌/⚠️ または Devil's Advocate 致命的 ≥ 1 件で Edit 実行):
  ```
  設計レビュー完了。以下を修正しました:
  - <何を→どう直したか（1論点=1行）>
  - <...>
  ```
  プランファイル本体にはレポート / 分析サマリを貼り付けない。設計自体を書き換える。

**「1問題1行」の粒度**: 「1論点 = 1行」に統一する。同じ論点の波及で複数ファイル / 複数箇所を Edit した場合でも 1 行にまとめる。逆に、独立した問題（例: トランザクション境界違反と God Class 回避）は別行に分ける。

**in-context 代替モード時の表記**: Step 3 で fallback を使った場合、最終報告本文の**末尾に 1 行だけ** `(in-context 代替モード: <代替した reviewer 名>)` を追加する。それ以外の中間出力（reviewer ごとの判定結果、Devil's Advocate の反論詳細等）は最終報告に含めない。

## Detailed Workflow (複雑なケース用)

Quick Start + Parallel Review (Step 1-6) で解決しない場合のみ、[references/detailed-workflow.md](references/detailed-workflow.md) に従って実行する。

## Quality Standards

- **Consistency**: 既存パターンとの一貫性を重視
- **Simplicity**: 最小限の構成で目的を達成
- **Criticism**: 問題を見つけることを優先（デフォルトは「問題あり」）
