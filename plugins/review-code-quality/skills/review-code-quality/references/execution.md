# Execution details

SKILL.md Step 2 の実行詳細。処理方式の選択ロジック、Task 使用可否の自己判定、agent 起動プロンプトテンプレ、指摘件数ルールを定義する。

## 処理方式の選択

| 条件 | 処理方式 |
|-----|---------|
| ファイル ≤ 2 | main thread で 4 観点を順次分析 |
| ファイル > 2 かつ Task ツール使用可 | 4 agent 並列 (同一メッセージ内に Task 4 つ) |
| ファイル > 2 かつ Task ツール使用不可 (nested 実行) | main thread fallback + 冒頭で fallback 理由を明示 |

## Task 使用可否の自己判定 (nested 実行検知)

本 skill が他 subagent から呼ばれている (nested 実行) 場合、Task ツールは使用不可とみなす。Task を試行して失敗を確認する必要はない。

判定基準: 本 skill 起動時に system prompt に「You are an executor」「以下の agent 定義を Read で読み込み」等の subagent 起動文脈が含まれていれば nested 実行とみなす。

## 並列実行 (ファイル > 2 かつ Task 使用可)

Task ツール (`subagent_type: "general-purpose"`) で**同一メッセージ内に 4 つの Task 呼び出しを並べて起動** (並列化のため単一メッセージ内が必須)。各 agent ファイル (`agents/*.md`) を Read で読み込ませ、対象ファイルの**絶対パスを改行区切り**で渡す。

agent 起動プロンプトの最小テンプレ:

```
あなたは <agent 名> です。以下の agent 定義を読んで従ってください:
<agents/xxx-analyzer.md の絶対パス>

対象ファイル (絶対パス):
- /abs/path/a.rb
- /abs/path/b.rb
- /abs/path/c.rb

指定された出力フォーマットで分析結果のみを返してください。
```

| Agent | ファイル | 観点 |
|-------|---------|------|
| cohesion-analyzer | `agents/cohesion-analyzer.md` | 凝集度 ([references/cohesion.md](cohesion.md)) |
| coupling-analyzer | `agents/coupling-analyzer.md` | 結合度 ([references/coupling.md](coupling.md)) |
| readability-analyzer | `agents/readability-analyzer.md` | 可読性 ([references/readability.md](readability.md)) |
| business-impact-analyzer | `agents/business-impact-analyzer.md` | 業務副作用 chain ([references/business-impact.md](business-impact.md)) — domain model attribute を更新する change のみ対象。skip 可 |

## main thread 代替実行 (ファイル ≤ 2 または Task 使用不可)

main thread で以下を順次実行:

1. 4 つの agent ファイル (`agents/*.md`) をすべて Read
2. 各 agent ファイルが指定する `references/*.md` を Read (agent 側が「起動時に必ず読む」としているため、代替実行時は main thread が責任を持つ)
3. 各観点で agent の検出基準 / 判定基準 / 出力フォーマットをそのまま適用して分析結果を生成

## 指摘件数ルール

- 「最低 3 件」は **observation axis (agent) 単位 / 対象ファイル群全体** でカウント。ファイル単位ではない
- **business-impact-analyzer の例外**: 起動条件 (domain model attribute の更新変更が diff に含まれる) に該当しない場合、最低件数を満たさず skip 報告で終了してよい
- **Escape hatch**: 対象ファイルの合計行数が 50 行未満の場合、観点あたり最低 1 件まで緩和可。ただしその観点で「なぜ他の指摘が無いか」を 200 字以上で説明する (指摘の水増しで SN 比を落とさないため)
- `references/*.md` の内容は agent ファイル側で読むのが原則。SKILL.md から二重に読む必要はない
