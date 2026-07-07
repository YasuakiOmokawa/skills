# Execution details

SKILL.md Step 2 の実行詳細。処理方式の選択ロジック、Task 使用可否の自己判定、agent 起動プロンプトテンプレ、指摘件数ルールを定義する。

## 処理方式の選択

| 条件 | 処理方式 |
|-----|---------|
| ファイル ≤ 2 | main thread で 4 観点を順次分析 |
| ファイル > 2 かつ Task ツール使用可 | 4 agent 並列 (同一メッセージ内に Task 4 つ) |
| ファイル > 2 かつ Task ツール使用不可 (利用可能ツール一覧に Task/Agent が無い場合。nested 実行かどうかとは無関係) | main thread fallback + 冒頭で fallback 理由を明示 |

## Task 使用可否の自己判定

自分の利用可能ツール一覧に Task (Agent) が存在するかで判定する。Task を試行して失敗を確認する必要はない。

Claude Code は subagent からの nested 起動を深さ 5 まで許可しており、本 skill が他 subagent から呼ばれている (nested 実行) こと自体は Task 不可の理由にならない。起動プロンプトの文面 (「You are an executor」等の定型句の有無) だけで判定しない — 定型句が無い自然文の依頼でも一覧に Task があれば使用し、定型句があっても一覧に無ければ使用不可と判定する。

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

- 「最低 3 件」は **observation axis (agent) 単位 / 対象ファイル群全体** での **目標下限**。ファイル単位ではない
- **business-impact-analyzer の例外**: 起動条件 (domain model attribute の更新変更が diff に含まれる) に該当しない場合、最低件数を満たさず skip 報告で終了してよい
- **Escape hatch**: 対象ファイルの合計行数が 50 行未満の場合、観点あたり最低 1 件まで緩和可。ただしその観点で「なぜ他の指摘が無いか」を 200 字以上で説明する (指摘の水増しで SN 比を落とさないため)。**上限の規定はない**
- **真の検出件数が下限未満の場合** (≥50 行で 2 件しか出ない等): 水増し禁止が優先。実際に検出した件数のみ出力し、その axis に「**目標下限未達 (N 件)**: <なぜ他の指摘が無いか 200 字以上>」を必ず添える。SN 比優先 (= 水増し禁止) と最低 3 件 (= 目標下限) は **目標下限を緩和する** 形で整合する
- `references/*.md` の内容は agent ファイル側で読むのが原則。SKILL.md から二重に読む必要はない

### business-impact 起動条件の境界 (意味論的 vs 構文的)

`update!` / `update_column` / migration の構文的判定だけで起動を決めると、`last_export_at` 等の **権限境界ではない attribute** にまで起動してしまい SN 比が落ちる。境界規則:

- **常に起動**: domain model の権限境界 attribute (role / status / plan_code / disabled / archived / approval_state など) への write
- **起動 + Limitation 明示**: 上記以外の `update!` / `update_column` (例: `last_*_at` 等のタイムスタンプ更新)。出力末尾に `Limitation: 権限境界 attribute ではないため caller chain は推測的` と明記し、Info (🔵) レベル止まりとする
- **skip**: `.rb` ファイルなし / `update*` メソッド呼出しなし / migration なし

### 処理方式 (ファイル数) と件数閾値 (行数) は直交

「処理方式の選択」表 (ファイル数 ≤2 / >2) は **dispatch 形態のみ**を決める。Escape hatch (合計行数 < 50) は **件数閾値のみ**を緩和する。両者は独立に評価し、合成挙動は以下:

| ファイル数 | 合計行数 | dispatch | 件数 |
|---|---|---|---|
| ≤2 | <50 | main thread 順次 | 観点あたり最低 1 件 + 200 字理由 |
| ≤2 | ≥50 | main thread 順次 | 観点あたり最低 3 件 |
| >2 | <50 | 4 agent 並列 (Task 可) / main thread fallback | 観点あたり最低 1 件 + 200 字理由 |
| >2 | ≥50 | 4 agent 並列 (Task 可) / main thread fallback | 観点あたり最低 3 件 |

### codebase access 不可時 (diff のみ)

実 codebase に grep / Read できない (PR 単独レビュー / walk-through) 場合、business-impact-analyzer は **diff 内 caller のみで chain を仮説提示**し、出力末尾に `Limitation: caller grep 未実施 (codebase 未アクセス)` を明記する。skip と区別するため、起動条件は満たしているが範囲が限定的であることを明示する。
