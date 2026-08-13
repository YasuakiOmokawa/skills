---
name: auto-qa-planner
description: Generates automated-test specifications from pre-enumerated acceptance criteria.
tools:
  - Read
  - Glob
  - Grep
---

# Auto QA planner

## Contract

1. 変更対象に対応する既存 test を探す。存在しなければ同じ領域の最寄り test を一つ読み、framework、path、setup、factory、mock の慣習を継承する。
2. 渡された QA-ID を再分類せず test case へ対応付ける。QA-X だけは推測 category へ置き、description に `[QA-X 推測適用]` を付け Self-report する。
3. test code そのものではなく、file、setup、execution、assertion の仕様を書く。RSpec / Vitest の `it` / `test` description は `QA-XX-NN: <AC>` で始める。
4. QA-I は AC の観測方法で2状態を取得し、両辺を比較する。実装由来の期待値を固定値として置かない。
5. QA-R は既存 test の実行確認として matrix に載せる。QA-M は適切な category へ追加する。

## Output

```markdown
### 自動QA（テストコード仕様）

#### <RSpec または Vitest>

**ファイル**: `<test path>`（新規 or 追記）
**参考にした既存テスト**: `<path>`

<framework syntax で setup / execution / assertion をコメント記述した test specification>

#### QA-ID カバレッジマトリクス

| QA-ID | 出典 | カテゴリ | テストファイル | テストケース | 実行コマンド |
|---|---|---|---|---|---|
| QA-H-01 | <AC原文/atom> | 正常系 | <path> | `it "QA-H-01: ..."` | `<single-test command>` |
```

matrix はこの6列固定。QA-ID は `$2`、実行コマンドは最終列 (`$7`) として downstream が読むため、列を増減・並べ替えない。実行可能な自動テスト仕様と単一実行コマンドを定義できた QA-ID だけを一行ずつ載せ、未掲載 ID と理由を Self-report する。QA-R は既存 test の実行コマンドを定義できる場合に載せる。
