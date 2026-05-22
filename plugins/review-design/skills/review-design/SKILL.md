---
name: review-design
description: 新機能の実装開始前、ファイルやモジュールの追加時、「このコードはどこに置くべきか」と迷った時に使用。
---

# My Code Design

## Quick Start: 3 つの質問

設計開始時に 3 質問で方向性を決め、答えに応じて Reviewer を選ぶ。

| 質問 | 答え | 次アクション |
|---|---|---|
| Q1: 類似機能はどこにある? | 見つかった + 健全 (テストあり / 責務明確 / ≤200 行 / public ≤10) | 同パターンで実装。Reviewer は anti-pattern-checker のみ |
| Q1 (同上) | 見つかった + 不健全 (テストなし / God Class / ≥300 行 / コールバック ≥3 連鎖) | 新パターン検討 + 改善案。全 Reviewer 起動 |
| Q1 (同上) | 見つからない | Q2 へ |
| Q2: 責務は一言で言えるか? | 言える | 1 ファイルで実装し Q3 へ |
| Q2 (同上) | 「〜と〜」になる | 分割してから Q3 へ |
| Q3: テストしやすいか? (依存差し替え可) | Yes | 実装開始 |
| Q3 (同上) | No | 引数 / DI で注入できる設計に修正 |

### 判断例

| ケース | Q1 | Q1.1 | Q2 | Q3 | 結論 |
|---|---|---|---|---|---|
| 新しい Service 追加 | `app/services/` に類似あり | テストあり、80 行 | 「契約を作成する」 | mock 可 | 類似に従って実装 |
| 複雑なビジネスロジック | 類似なし | — | 「検証と通知と保存」 | — | 3 つに分割してから実装 |
| 外部 API 連携 | 類似なし | — | 「Slack 通知する」 | 外部依存あり | Adapter パターン検討 → 詳細ワークフローへ |
| 既存パターンに問題あり | 類似あり | テストなし 400 行 God Class | — | — | 新パターン検討 + 改善提案 |

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

### Step 2: Reviewer 選択

Q1-Q3 の結果から下表で Reviewer を決定する。**「全 Reviewer」= `anti-pattern-checker` + `ddd-reviewer` + `hexagonal-reviewer` + `clean-architecture-reviewer` の 4 種**。

| 状況 | 起動する Reviewer |
|---|---|
| Q1 類似機能あり + Q1.1 健全 + Q2 単一責務 | anti-pattern-checker のみ |
| Q1 類似機能あり + Q1.1 健全 + Q2 「〜と〜」(分割必要) | anti-pattern-checker + ddd-reviewer |
| Q1 類似機能あり + Q1.1 不健全 | 全 Reviewer (並列) |
| Q1 類似なし + 複雑なビジネスルール | ddd-reviewer + anti-pattern-checker |
| Q1 類似なし + 外部依存あり (API/DB 差替) | hexagonal-reviewer + anti-pattern-checker |
| Q1 類似なし + 新規設計 (レイヤー検討) | clean-architecture-reviewer + anti-pattern-checker |
| 複合ケース | 該当する全 Reviewer を並列起動 |

**表の優先順位**: 上から順に評価して最初にマッチした行を採用 (Q1.1 健全行は Q2 単一/分割で 2 行に分割済みなので、Q2 結果で機械的に決まる)。

### Step 3: Parallel Task Invocation

選択された Reviewer を Task ツール（`subagent_type: "general-purpose"`）で**並列起動**する。各 Reviewer の agent ファイル（`agents/*.md`）を読み込ませ、設計判断の内容を渡すこと。

**各 Reviewer の役割**:
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

Parallel Review 後、Devil's Advocate (DA) で設計判断への反論を生成する。**inline default** モードで main agent 自身が反論を生成し、特定の昇格条件を満たすときのみ subagent dispatch に切り替える。

#### 用語の区別

| 用語 | 意味 | 適用場面 |
|---|---|---|
| **inline default** (通常モード) | main agent が自前で DA 処理 | デフォルト。Critical candidate が少なく自己批判リスクが小さい場合 |
| **subagent dispatch** (昇格モード) | Task ツールで DA を fresh subagent として起動 | 致命的検出が複雑で fresh 視点が必要な場合 (条件は後述) |
| **in-context fallback** (環境制約モード) | Task ツール自体が使えない環境で main agent が代替実行 | Task tool deferred / dispatch 権限なし。Step 3 の Reviewer fallback と同じ概念 |

`inline default` と `in-context fallback` は**別概念**: 前者は通常運用、後者は環境制約。最終報告の `(in-context 代替モード: ...)` 表記は `in-context fallback` の場合のみで、`inline default` では出さない。

#### subagent dispatch への自動昇格条件 (機械判定)

inline default で開始し、以下のいずれかを満たした場合は subagent dispatch に切り替える:

1. **`❌` を含む Reviewer 数 ≥ 2**: Parallel Review (Step 3) の出力で `❌` 判定を含む Reviewer (anti-pattern-checker / ddd-reviewer / hexagonal-reviewer / clean-architecture-reviewer の 4 種) の数が 2 以上
2. **単独昇格トリガーが 1 件以上**: 以下の項目を Reviewer 出力に検出した場合は 1 件でも昇格 (重要度が高く、自己批判バイアスのリスクを許容できない)
   - DB トランザクション境界違反 (コールバック内で外部 API、複数 Aggregate にまたがる write、saga パターン未実装)
   - 並行性 / 冪等性の欠陥 (race condition、二重通知、複数タブ・複数インスタンス時の競合)
   - セキュリティ脆弱性 (認証バイパス、SQL/XSS/CSRF、平文保存、IDOR、open redirect)
   - 既存契約違反 (公開 API の breaking change、外部 SDK の major version up)
3. **`--strict-da` 引数の指定**: ユーザーが `$ARGUMENTS` に `--strict-da` を含めた場合、無条件で subagent dispatch

#### 「単独昇格トリガー」と「致命的判定基準」の関係

両者は別用途で使う:

| 用語 | 用途 | 適用タイミング |
|---|---|---|
| **単独昇格トリガー** (本セクション) | inline default → subagent dispatch への切り替え判定 | Parallel Review 完了直後、DA 開始前 |
| **致命的判定基準** (次セクション) | DA が反論を「致命的 / 許容可能」で評価 | DA 実行中 (inline / subagent どちらでも) |

**包含関係**: 単独昇格トリガー ⊆ 致命的判定基準。昇格トリガー 4 種 (DB transaction / 並行性 / セキュリティ / 既存契約) は致命的判定基準にも含まれる。致命的判定基準には加えて「anti-pattern ❌」がある (これは既に Parallel Review で検出されるため昇格判定は `❌ Reviewer 数 ≥ 2` の経路で扱う)。

#### inline default の指示内容

main agent は以下のプロンプトを自分自身に課して反論を生成する:

```
あなたは Parallel Review の出力を批判する Devil's Advocate です。次のルールに従ってください:

1. Parallel Review (Step 3) の出力に**書かれていない**観点から反論を 3 つ生成する (既出論点の再掲は禁止、新規視点が必須)
2. 各反論を「致命的 / 許容可能」で判定 (致命的の基準は後述)
3. 見落としている前提を 1-2 件指摘
4. 自己批判バイアス対策: 「Parallel Review が見ているのと同じ視点」では反論しない。代わりに以下のいずれかの視点で攻める:
   - 運用時の障害シナリオ (デプロイ直後 / 退役直前 / 障害時)
   - スケールの拡張 (100 倍トラフィック / 100 倍データ量)
   - 別チーム / 別 plugin / 別サービスから見たときの interface 品質
   - rollback / 取り消しのコスト
```

**致命的判定の基準**（これに該当するもののみ「致命的」。主観的な好みは「許容可能」）:
- `agents/anti-pattern-checker.md` の判定表で ❌ に該当
- DB トランザクション境界違反（例: コールバック内で外部API呼び出し）
- 並行性 / 冪等性の欠陥（例: レースコンディション、二重通知）
- セキュリティ脆弱性（例: 個人情報の平文保存、認証バイパス）
- 既存契約違反（例: 既存 interface の破壊、後方互換性喪失）

#### subagent dispatch の指示内容 (昇格時のみ)

```
Task(subagent_type="general-purpose", prompt="""
あなたは fresh subagent として Devil's Advocate を実行します。Parallel Review の出力に対して反論を 3 つ生成し、致命的 / 許容可能で判定してください。Parallel Review に書かれていない観点から反論すること。

## Parallel Review の出力:
${PARALLEL_REVIEW_RESULT}

## 致命的判定の基準:
[本 SKILL.md 「致命的判定の基準」セクションをそのままコピー]
""")
```

**フィードバックループ**: 「致命的」判定があれば以下を実行 (inline default / subagent dispatch どちらでも同じ手順):
1. Edit ツールでプランファイルの該当箇所を修正
2. 修正後に再度 Parallel Review (Step 2-4) を実行して検証
3. 全項目が「許容可能」になるまで繰り返す
4. **再 Review 時の DA は inline default を再評価**: 修正後の Parallel Review 出力で昇格条件を再判定 (`❌` Reviewer 数 / 単独致命的トリガー)。前回 subagent だったからといって今回も subagent とは限らない

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

**in-context 代替モード時の表記** (※ Task ツールが利用不可な環境制約での fallback 時のみ。Step 5 の `inline default` (通常モード) では記載しない): Step 3 (Parallel Review) または Step 5 (Devil's Advocate) のいずれか **1 つ以上** で **Task tool deferred / dispatch 権限なし** により fallback を使った場合、最終報告本文の**末尾に 1 行だけ**以下を追加する:

```
(in-context 代替モード: <代替したエージェント名をスラッシュ区切り>)
```

- 対象集合: Reviewer (4 種) **および** `devil's-advocate` を含む (Step 5 の Devil's Advocate の subagent dispatch 試行が環境制約で失敗した場合)
- 書式例 (Devil's Advocate のみ代替): `(in-context 代替モード: devil's-advocate)`
- 書式例 (全 Reviewer + Devil's Advocate 代替): `(in-context 代替モード: anti-pattern-checker / ddd-reviewer / hexagonal-reviewer / clean-architecture-reviewer / devil's-advocate)`

**重要**: Step 5 の `inline default` モード (昇格条件を満たさず main agent が DA を inline 処理した通常運用) では、この表記は**出さない** (環境制約による fallback ではないため)。読み手が「環境問題で代替実行された」と誤解しないよう、用語を厳密に区別すること。

それ以外の中間出力 (reviewer ごとの判定結果、Devil's Advocate の反論詳細、フィードバックループの再 Review 詳細等) は最終報告に含めない。**フィードバックループの再 Review** が in-context モードで必要になった場合は、本 agent が内部で再判定し、最終報告には「致命的が解消したこと」のみを修正行に織り込む (再 Review の詳細手順は出力しない)。

## Detailed Workflow (複雑なケース用)

Quick Start + Parallel Review (Step 1-6) で解決しない場合のみ、[references/detailed-workflow.md](references/detailed-workflow.md) に従って実行する。

## Quality Standards

- **Consistency**: 既存パターンとの一貫性を重視
- **Simplicity**: 最小限の構成で目的を達成
- **Criticism**: 問題を見つけることを優先（デフォルトは「問題あり」）

## 併用推奨 skill

- `/define-acceptance-criteria` — 設計レビュー後、実装前に AC を定義する
