---
name: model-data
description: 要求文書からDBML形式のER図を生成し、SQLアンチパターンを検出。DB設計、ER図作成、スキーマ正規化、既存設計レビュー時に使用。
---

# Data Modeling

要求文書からDBML形式のER図を生成するマルチエージェントスキル。

## Workflow

```
要求文書
  ▼
Phase 1: requirements-analyst → 要件分析（JSON）
  ▼
Phase 2: conceptual-designer → 概念モデル（YAML）
  ▼
Phase 3: conceptual-reviewer → PASS/FAIL（FAIL時はPhase 2へ、最大3回）
  ▼
Phase 4: logical-designer → 正規化済み論理モデル（YAML）
  ▼
Phase 5: dbml-generator → DBML出力
```

## Execution

### Step 1: 入力取得

- ファイルパス引数 → Read で読み込み
- テキスト引数 → そのまま使用
- 引数なし → プランファイル or 会話コンテキストから判断

### Step 2: エージェント順次起動

Task ツールで各エージェントを起動し、前フェーズの出力を入力として渡す:

```
Task ツール:
  subagent_type: "general-purpose"
  prompt: |
    ${CLAUDE_PLUGIN_ROOT}/skills/model-data/agents/<agent-name>.md を読み込み、
    以下の入力に対して処理を実行してください:
    [前フェーズの出力]
```

Phase 3 が FAIL → 修正提案とともに Phase 2 を再起動（最大3回）。

### Step 3: 結果出力

最終DBMLをファイルに書き込み、dbdiagram.io での視覚化を提案。

## References

- [references/dbml-syntax.md](references/dbml-syntax.md) - DBML構文
- [references/sql-antipatterns.md](references/sql-antipatterns.md) - アンチパターン検出基準
