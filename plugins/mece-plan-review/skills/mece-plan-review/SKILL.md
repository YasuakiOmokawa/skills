---
name: mece-plan-review
description: プランファイルの受け入れ条件（AC）に対しMECE完全性検証を実施し、ユースケース漏れ・技術的対応漏れ・ACの改善点を検出して分析ファイルに記録する。プランにACが定義済みで実装前にMECE検証が必要な時に使用。事前に /define-acceptance-criteria でACを定義しておくこと。
---

# MECE Plan Review

## Overview

プランファイルを **Black Box (仕様情報源) + White Box (コード情報源) + Wiki (Devin 深掘り) + Fresh Red Team** の 4 役割で MECE 分析し、結果を分析ファイルに記録する。プランファイル本文には品質検証サマリー 1 行のみ追記。

empirical 検証で「役割名で分けただけの旧 QA/Tech は情報源を共有していたため Critical の 70-100% が重複していた」ことが判明。情報源で責務を分離 (BB = 仕様のみ、WB = コードのみ) することで、Critical 検出力が 2.4 倍に向上することを実測済 (plans/mece-improvement.md §「Variant D 追加検証」参照)。

```
メインエージェント: 初期化 + 結果集約 + 分析ファイル書込み
├─ BB Analyst        AC / プラン / Devin wiki / 仕様で AC のユースケース検証 [Task subagent]
├─ WB Analyst        コード / schema / 依存ライブラリ実挙動で AC のユースケース検証 [Task subagent]
├─ Wiki Researcher   Devin wiki 深掘り (BB の補助、関連リポ含む) [Task subagent]
└─ Fresh Red Team    BB+WB+Wiki 結果のみで 4 分類クロスリファレンス + 純技術リスク補完 [Task subagent]
```

```
Step 0: 初期化（引数パース、AC抽出、リポ取得）
         │
Step 1: 3 並列 Analyst 起動 (同一メッセージで起動)
         │  BB Analyst:        仕様情報源で AC 検証
         │  WB Analyst:        コード情報源で AC 検証
         │  Wiki Researcher:   Devin wiki から関連 context を収集
         │
Step 2: Fresh Red Team subagent 起動
         │  入力: BB結果 + WB結果 + Wiki結果 + red-team-checklist.md
         │  入力に含めない: プラン本文 / AC 本文 (真の freshness 確保)
         │  出力: 4 分類クロスリファレンス + お見合い検出 + 純技術リスク補完 + MECE 判定
         │
Step 3: 機械処理 (main agent)
         │  全指摘を分析ファイルに記録
         │  ACブラッシュアップ → 分析ファイルで [MECE追加] タグ付き
         │  サマリー1行 → プランファイルの品質検証セクション
```

## 重要ルール

1. **分析ファイルへの記録はメインエージェント（あなた）のみ**が行う
2. **Critical=0なら「MECE OK」**、1件以上なら「要修正」→ 分析ファイルに記録（プラン本文は変更しない）
3. **BB / WB Analyst は情報源を完全に分離**: BB はコード参照禁止、WB は仕様 / wiki 参照禁止 (独立性の構造保証)
4. **Fresh Red Team はプラン / AC を持たない**: BB+WB+Wiki 出力のみが入力 (真のクロスリファレンス確保)
5. **指摘件数の縛りなし**: 該当時のみ指摘、0件なら根拠 1 文

## 進捗チェックリスト

TodoWrite で以下のステップを記録すること:
- Step 0: 初期化 (プラン読み込み、AC抽出、リポ取得)
- Step 1: 3 並列 Analyst 起動 (BB + WB + Wiki Researcher)
- Step 1: 3 役の結果受信
- Step 2: Fresh Red Team subagent 起動
- Step 2: Red Team 結果受信
- Step 3-1: 全指摘の分析ファイル記録
- Step 3-2: ACブラッシュアップ (分析ファイル)
- Step 3-3: MECE 分析結果セクション追記 (分析ファイル)
- Step 3-4: プランファイルにサマリー1行追記

## Arguments

- `$ARGUMENTS`: プランファイルのパス
  - パス指定なし時: システムプロンプトの Plan File Info から取得
  - 例: `/mece-plan-review path/to/plan.md`

## Step 0: 初期化

### 0-1: 引数パースとプランファイル特定

`$ARGUMENTS` からプランファイルパスを取得（省略時はシステムプロンプトの Plan File Info から取得）。
プランファイル全文を Read で読み込む。

### 0-2: 分析ファイルから受け入れ条件（AC）の抽出【必須】

**分析ファイルパス**: プランファイルの拡張子前に `.analysis` を挿入する。
- 例: `plans/feature-xxx.md` → `plans/feature-xxx.analysis.md`

分析ファイルから `## 受け入れ条件` セクションを抽出する。

- **ACあり**: 検証ターゲットとして Step 1 の各サブエージェントに配布
- **分析ファイルが存在しない or ACなし**: **即座に中断**:

### 0-3: AC の enumerate (AC-ID 付与)

抽出した AC セクションを行単位でパースし、`- [ ]` で始まる項目に AC-ID (`AC-1, AC-2, ...`) を機械的に付与する。各項目のカテゴリ (正常系/異常系/エッジケース/非影響確認) も保持する。

```
${ENUMERATED_AC} の生成例:
- AC-1 (正常系): 既存ユーザが /auth/login → 200 + JWT
- AC-2 (正常系): 新規ユーザが /auth/saml/login → IdP リダイレクト → callback → ユーザ作成 + JWT + /dashboard
- AC-3 (異常系): SAML 有効ユーザが /auth/login → 403
- ...
```

BB / WB Analyst には `${ENUMERATED_AC}` を渡し、各 AC-ID に対する判定 (充足 / 不十分 / 言及なし) を返してもらう (output-format.md「ACカバレッジ機械合成」参照)。

```
⛔ 受け入れ条件（AC）が見つかりません。

分析ファイル（{分析ファイルパス}）にACが定義されている必要があります。
MECEは「何に対して漏れがないか」を検証するプロセスです。
検証ターゲットなしでは分析の精度が保証できないため、先にACを定義してください。

👉 /define-acceptance-criteria を実行してACを定義した後、再度 /mece-plan-review を実行してください。
```

### 0-4: リポジトリ名取得

```bash
git remote get-url origin | sed 's/.*github.com[:/]\(.*\)\.git/\1/'
```

### 0-5: 関連リポジトリ取得（オプション、Wiki Researcher 用）

```bash
gh repo list <YOUR_GITHUB_ORG> --limit 200 --json name,description --jq '.[] | "\(.name)\t\(.description)"'
```

取得したリポジトリ一覧とプラン内容を照合し、関連性の高いリポジトリを 5〜10 件選定。

**⚠️ 重要**: 選定したリポジトリ名は `<YOUR_GITHUB_ORG>/<リポジトリ名>` 形式で保持する (Devin wiki の `repoName` 引数にそのまま渡す)。

## Step 1: 3 並列 Analyst 起動

### 1-1: プロンプト読み込み

```
bb_prompt = Read("${CLAUDE_PLUGIN_ROOT}/skills/mece-plan-review/references/bb-analyst-prompt.md")
wb_prompt = Read("${CLAUDE_PLUGIN_ROOT}/skills/mece-plan-review/references/wb-analyst-prompt.md")
```

Wiki Researcher 専用プロンプトは不要 (BB の Phase 0 と同じ仕様で、subagent の役割として Devin wiki 探索のみに集中させる)。

### 1-2: 3 つの Task subagent を同一メッセージ内で並列起動

```
Task(subagent_type="general-purpose", name="bb-analyst", prompt="""
あなたは MECE 分析の Black Box Analyst です。以下のプロンプトに従い分析を実行してください。

${bb_prompt}

---
リポジトリ: ${REPO_NAME}
関連リポジトリ (Devin wiki の repoName にそのまま使用可能):
${RELATED_REPOS}
プランファイル:
${PLAN_CONTENT}
受け入れ条件 (AC-ID 付き、検証ターゲット):
${ENUMERATED_AC}

分析結果を Markdown 形式で返してください。
""")

Task(subagent_type="general-purpose", name="wb-analyst", prompt="""
あなたは MECE 分析の White Box Analyst です。以下のプロンプトに従い分析を実行してください。
BB Analyst の結果は参照せず、コード情報源だけで独立に調査してください。

${wb_prompt}

---
リポジトリ: ${REPO_NAME}
プランファイル:
${PLAN_CONTENT}
受け入れ条件 (AC-ID 付き、検証ターゲット):
${ENUMERATED_AC}

分析結果を Markdown 形式で返してください。
""")

Task(subagent_type="general-purpose", name="wiki-researcher", prompt="""
あなたは MECE 分析の Wiki Researcher です。Devin wiki から関連 context を収集し、BB Analyst の補助情報として整理してください。

リポジトリ: ${REPO_NAME}
関連リポジトリ:
${RELATED_REPOS}
プランファイル:
${PLAN_CONTENT}

以下を実行:
1. `ToolSearch("+fdev-devin")` で devin ツール取得
2. `read_wiki_structure(repoName)` で wiki 構造取得
3. プラン関連ページを `read_wiki_contents` で読む
4. 関連リポも同様に調査
5. 不明点のみ `ask_question` で補足

⚠️ Devin wiki の repoName は必ず `<YOUR_GITHUB_ORG>/<リポジトリ名>` 形式。

出力: Markdown でユースケース・既知のエッジケース・連携先システムの動作を整理。
分析判断 (Critical / Important) はせず、事実情報のみ。
""")
```

### 1-3: 3 つの結果を受信

Task の戻り値として自動的に取得。変数 `${BB_RESULT}` / `${WB_RESULT}` / `${WIKI_RESULT}` として保持。

## Step 2: Fresh Red Team subagent 起動

### 2-1: チェックリスト読み込み

```
red_team_checklist = Read("${CLAUDE_PLUGIN_ROOT}/skills/mece-plan-review/references/red-team-checklist.md")
```

### 2-2: Fresh Red Team subagent dispatch

**⚠️ 重要**: Red Team subagent の入力にプラン本文 / AC 本文を含めない (真の freshness 確保)。BB / WB / Wiki の出力と checklist のみ。

```
Task(subagent_type="general-purpose", name="fresh-red-team", prompt="""
あなたは MECE 分析の Fresh Red Team Reviewer です。プラン本文 / AC 本文を持たない状態で、BB Analyst と WB Analyst の分析結果のみを入力としてクロスリファレンスを実行してください。

${red_team_checklist}

---
BB Analyst の分析結果:
${BB_RESULT}

WB Analyst の分析結果:
${WB_RESULT}

Wiki Researcher の参考情報:
${WIKI_RESULT}

統合評価レポートを red-team-checklist.md の「統合評価レポートのフォーマット」に従って出力してください。
""")
```

### 2-3: Red Team 結果受信

`${RED_TEAM_RESULT}` として保持。

## Step 3: 分析結果出力

**出力先ルール**: 全分析結果は **分析ファイル** に記録する。プランファイルにはサマリー 1 行のみ追記。プラン本文は一切変更しない。

### 3-1: AC カバレッジ表を機械合成 + 全指摘の分析ファイル記録

**AC カバレッジ表の機械合成** (main agent):
1. BB が返した「AC 判定」テーブルと WB が返した「AC 判定」テーブルを AC-ID で join
2. 各 AC-ID について [references/red-team-checklist.md](references/red-team-checklist.md) の「AC カバレッジ機械合成」ルールで総合判定を決定:
   - どちらか「不十分 / ❌」 → 不十分
   - 両方「言及なし」 → 不十分 (お見合い検出対象)
   - 少なくとも一方「充足 / ✅」+ 他方「充足」or「言及なし」 → 充足
3. 元 AC 文の「カテゴリ」(正常系/異常系/エッジ/非影響) を分析ファイルの AC セクションから補完
4. [references/output-format.md](references/output-format.md) のフォーマットで分析ファイルに記録

**指摘の記録**:
Red Team の統合 Critical / Important / Nice-to-have を **分析ファイル** に記録する。

- **🔴 Critical**: プラン内の該当箇所 (セクション名・内容) と推奨修正内容を併記
- **🟡 Important / 🟢 Nice-to-have**: 簡潔に記録

### 3-2: AC ブラッシュアップ

Red Team の 4 分類結果から AC 改善点を統合:

- **実装漏れ** (BB ✓ WB —) → 該当 AC を強調 + Critical 指摘
- **仕様漏れ** (BB — WB ✓) → AC 追加 (`[MECE追加]` タグ)
- **お見合い** (両者言及なし、Red Team 検出) → AC 追加 (`[MECE追加]` タグ)

分析ファイルの受け入れ条件セクションに対して:
- **新規 AC 項目追加**: `[MECE追加]` タグを付与し、元の AC と区別
- **既存 AC 修正**: 曖昧・不十分だった AC 項目の具体化
- **AC 修正**: 技術的に実現不可能な AC は理由付きで修正

### 3-3: MECE分析結果を分析ファイルに追記

[references/output-format.md](references/output-format.md) のフォーマットに従い、**分析ファイル**末尾に追記。

### 3-4: プランファイルにサマリーを追記

プランファイルの `## 品質検証` セクションに以下を追記する（セクションがなければ作成）:

```markdown
- MECE判定: [OK or 要修正（Critical N件）] / ACカバレッジ [N]/[M]項目 / 漏れ [X]件 / 重複 [Y]件 → [分析ファイル名]
```

## Error Handling

### Devin MCP 利用不可

```
ToolSearch("+fdev-devin") → 失敗
  → BB Analyst と Wiki Researcher は wiki なしで継続 (BB はローカル仕様 + 一般知識でフォールバック)
  → 結果に [Devin未使用] タグ付与
```

### Analyst subagent 失敗

```
Task の戻り値がエラーまたはタイムアウト:
  → 該当ロールを [未取得] として記録
  → Red Team に「BB or WB のいずれかが取得できなかった」旨を伝え、残りの結果のみで Step 2 を継続
```

### Red Team subagent 失敗

```
Red Team が失敗した場合:
  → メインエージェントが手動で BB+WB の結果を統合 (フォールバック)
  → 結果に [Red Team フォールバック] タグ付与
```

### プランファイル書き込み失敗

AskUserQuestion でパス確認を依頼。

### 分析ファイルが他プロセスで lock 中 / non-git リポジトリ

- 分析ファイル書込み時に lock 検出 → 1 回リトライ、それでも失敗なら AskUserQuestion で対応確認
- non-git リポ (`git remote get-url origin` が失敗) → `${REPO_NAME}` を「unknown-repo」として継続、Wiki Researcher は `[non-git: Devin 未使用]` で skip

## References

- [references/bb-analyst-prompt.md](references/bb-analyst-prompt.md) - BB Analyst プロンプト (仕様情報源限定)
- [references/wb-analyst-prompt.md](references/wb-analyst-prompt.md) - WB Analyst プロンプト (コード情報源限定)
- [references/red-team-checklist.md](references/red-team-checklist.md) - Fresh Red Team クロスリファレンスチェックリスト
- [references/output-format.md](references/output-format.md) - プラン修正・追記フォーマット

## 併用推奨 skill

- `/define-acceptance-criteria` — MECE 検証の対象となる AC を事前に定義する
- `/finalize-plan` — MECE 検証結果を反映してプランを実装フェーズに進める
