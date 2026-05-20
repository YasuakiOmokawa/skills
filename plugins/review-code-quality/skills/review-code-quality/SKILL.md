---
name: review-code-quality
description: 実装完了後のセルフチェック時、PRレビュー前の品質確認時に使用。RuboCop/ESLintでは検出できない設計レベルの問題と、domain model attribute (plan_code / role / status 等) を更新する変更時の caller 業務副作用 (機能フラグ復活 / 認可 bypass 等の 2 段階副作用 chain) を検出する。
---

# My Code Quality

**提案のみ行い、自動修正は行わない。**

## Arguments

- `$ARGUMENTS`: 品質チェック対象のファイルパス（省略可）
  - 指定あり: 指定されたファイルのみをチェック
  - 指定なし: git diff で変更されたファイルをすべてチェック

## Quality Standards（厳格モード）

- **Default Stance**: デフォルトは「問題あり」。問題なしの場合のみ根拠を明示
- **Minimum Findings**: 各エージェントは最低3件の指摘。0件は見落としを疑い、理由を200字以上で説明
- **No Sugar-Coating**: 「多分大丈夫」は禁止。確信がなければ指摘せよ

### 重大度

| アイコン | レベル | 対処 |
|---------|--------|------|
| 🔴 | Critical | 即座に修正 |
| 🟠 | Major | このPRで修正 |
| 🟡 | Minor | 次のPRで修正推奨 |
| 🔵 | Info | 認識しておく |
| ✅ | Good | 維持する |

## Workflow

### Step 1: 対象ファイルの特定

引数指定時は `$ARGUMENTS` を使用。なければ `git diff --name-only origin/develop...HEAD` で取得。0件なら終了。

### Step 2: Quality Analysis

#### 処理方式の選択

| 条件 | 処理方式 |
|-----|---------|
| ファイル ≤ 2 | main thread で 4 観点を順次分析（下記「main thread 代替実行」） |
| ファイル > 2 かつ Task ツール使用可 | 4 エージェント並列（下記「並列実行」） |
| ファイル > 2 かつ Task ツール使用不可（例: 本 skill が subagent から呼ばれた nested 実行） | main thread で 4 観点を順次分析（下記「main thread 代替実行」）+ 冒頭で fallback 理由を明示 |

#### 並列実行（ファイル > 2 かつ Task 使用可の場合）

Task ツール（`subagent_type: "general-purpose"`）で**同一メッセージ内に 4 つの Task 呼び出しを並べて起動**（並列化のため単一メッセージ内が必須）。各 agent ファイル（`agents/*.md`）を Read で読み込ませ、対象ファイルの**絶対パスを改行区切りで明示**して渡す。

agent 起動プロンプトの最小テンプレ:
```
あなたは <agent 名> です。以下の agent 定義を読んで従ってください:
<agents/xxx-analyzer.md の絶対パス>

対象ファイル（絶対パス）:
- /abs/path/a.rb
- /abs/path/b.rb
- /abs/path/c.rb

指定された出力フォーマットで分析結果のみを返してください。
```

| Agent | ファイル | 観点 |
|-------|---------|------|
| cohesion-analyzer | `agents/cohesion-analyzer.md` | 凝集度（[references/cohesion.md](references/cohesion.md)） |
| coupling-analyzer | `agents/coupling-analyzer.md` | 結合度（[references/coupling.md](references/coupling.md)） |
| readability-analyzer | `agents/readability-analyzer.md` | 可読性（[references/readability.md](references/readability.md)） |
| business-impact-analyzer | `agents/business-impact-analyzer.md` | 業務副作用 chain（[references/business-impact.md](references/business-impact.md)）— domain model attribute を更新する change のみ対象。skip 判定あり |

#### main thread 代替実行（ファイル ≤ 2 または Task 使用不可の場合）

main thread で以下を順次実行:
1. 4 つの agent ファイル（`agents/*.md`）をすべて Read
2. 各 agent ファイルが指定する `references/*.md` を Read（agent 側が「起動時に必ず読む」としているため、代替実行時は main thread が責任を持つ）
3. 各観点で agent の検出基準 / 判定基準 / 出力フォーマットをそのまま適用して分析結果を生成

#### 指摘件数の単位

- 「最低 3 件」は **observation axis（agent）単位 / 対象ファイル群全体** でカウント。ファイル単位ではない
- **business-impact-analyzer の例外**: 本 agent は起動条件 (domain model attribute の更新変更が diff に含まれる) に該当しない場合、最低件数を満たさず skip 報告で終了してよい
- **Escape hatch**: 対象ファイルの合計行数が 50 行未満の場合、観点あたり最低 1 件まで緩和可。ただしその観点で「なぜ他の指摘が無いか」を 200 字以上で説明すること（指摘の水増しで SN 比を落とさないため）
- `references/*.md` の内容は agent ファイル側で読むのが原則。本 SKILL.md から二重に読む必要はない

### Step 3: 統合分析

3エージェントの結果を収集し、以下を実行:

1. **根本原因の特定**: 複数軸で同じファイルが指摘されている場合、根本原因を1つに特定
2. **優先度判定**: 重大度順（🔴 > 🟠 > 🟡 > 🔵）を基本とし、同重大度内では参照箇所数が多いものを上位に
3. **レポート出力**:

#### 出力ルール

- 重大度アイコン（🔴🟠🟡🔵✅）は **該当する指摘があるときのみ** 使用。該当なしのレベルはセクションごと省略してよい。ただし全体サマリー行では `🔴 0 / 🟠 N / 🟡 N` のように 0 件を含めて総数を明示する
- 各指摘は **`/abs/path:line_number` 形式** で位置情報を付ける。範囲なら `:10-18`、クラス全体なら `:class` サフィックス、ファイル全体なら `:file` サフィックス
- 「改善の余地」は各 agent セクションに配置する（統合レポート側では不要）

```markdown
## 設計レビュー結果

### 🔴 Critical / 🟠 Major
[最優先で対処すべき問題]

### 🟡 Minor
[改善推奨の問題]

### 根本原因分析
[複数軸から同一原因に帰着する問題の特定]

### アクションプラン
1. [何を] → [どう変えるか]（重大度、影響範囲）

### 総合サマリー
🔴 0件 / 🟠 N件 / 🟡 N件 / 🔵 N件
```

## 併用推奨 skill

- `/polish-before-commit` — 検出された問題を踏まえてコミット前の最終仕上げを行う
- `/qa-ui` — コード品質と並行して実装後 UI を検証する
