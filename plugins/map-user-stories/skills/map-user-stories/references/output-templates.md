# Output contract

Emit these sections in order:

1. `## Context`
2. one or more `## Phase N: {name}` story tables
3. `## スプリントマッピング`
4. `## Jira ↔ US マッピング`
5. `## タスクリスト`
6. `## US TSV`
7. `## 未解決事項`

## Context

State source, DD review status when applicable, scheduling assumptions, and unresolved capacity or workload-estimate units. Sprint allocation requires capacity and workload in the same explicit unit plus known duration.

## Phase story table

```markdown
| US_ID | ユーザー | ストーリー | 受入条件 | 依存US | Jira | 技術メモ |
|---|---|---|---|---|---|---|
```

IDs are `US-001` onward across phases. Separate multiple AC or note entries with `<br>`. Leave dependency/Jira cells visibly empty. `やらない:` / `対象外:` prefixes are valid only in the technical-note column.

## Sprint mapping

```markdown
| Sprint/波 | 期間 | US | Tasks | 達成目標 |
|---|---|---|---|---|
```

## Jira mapping

```markdown
| 既存Jira | 対応US/タスク | 状態 |
|---|---|---|
```

With no Jira input, add one row: `| なし | — | 新規作成予定 |`.

## Task TSV

Use a fenced `tsv` block. Every row has exactly nine tab-separated cells:

`US_ID, Task_ID, タスク名, やること, やらないこと, 完了条件, 依存タスク, Jira, 備考`

`Task_ID` is `T-001` onward. Multiple parent stories are comma-separated. No tabs/newlines inside a cell; use ` / ` for lists. Empty `やらないこと` becomes `（特になし）` downstream; empty completion inherits the parent AC.

## US TSV

Every row has exactly eight tab-separated cells:

`US_ID, Phase, ユーザー, ストーリー, 受入条件, 依存US, Jira, 技術メモ`

## Unresolved

Use checkboxes for decisions still needed. Use plain `スコープ外: ...` lines for unmatched exclusions. If none, write `- なし`.

The downstream Jira description maps dependencies to 着手条件, story/task work to やること, exclusions to やらないこと, and AC/completion to 完了条件.
