---
name: purge-private-vocab
description: Use after generating PR description, Jira ticket, design doc, RFC, or other reader-facing text from a local plan/spec file, to detect and rewrite vocabulary that exists only in the source and would confuse readers without it. Triggers when output of /create-pr, Jira create, design doc draft, or similar derives from a local plan.
---

# Purge Private Vocabulary

## Overview

ローカルプランファイル (`~/.claude/plans/**/*.md` 等) には設計時の思考効率を上げるため、自分用の造語・略号・番号ラベルが多用される。例: `Single Switch Principle`, `Provider 内吸収型`, `Critical-A/B/C/D`, `4 象限`, `α/β/γ 層`, `rollout enabler`, `AC-12`, `§設計詳細`。

これらは plan 内では文脈があるため有効に機能するが、plan を読まない読者 (PR レビュワー / Jira watcher / design doc 閲覧者) が**そのまま読まされると decode 不能**で混乱する。

本 skill は、ローカル plan から派生した**対外文書**を点検し、ローカル固有語を「読者がそのまま理解できる表現」に書き換える。

**核心原則**: 「読者が source plan を持っていない前提で読み下せるか」。書き手 (AI 自身) が plan を読んだ状態で書くと、無意識に plan 内造語を持ち込みがち。

## When to Use

主条件 (どれかに該当):
- ローカル plan ファイルから PR description / Jira / design doc / RFC / Slack / メール下書きを**生成した直後**
- `/create-pr` 等のコマンド実行直後 (plan が source の場合)
- 上記文書をレビューに出す**直前**

副条件:
- target 文書を読む人が plan ファイルに**アクセスできない**
- target 文書が plan を持たない第三者 (PSIRT, PdM, 外部監査) にも到達する

**When NOT to use**:
- target が plan そのもの (内部設計ノート、自分用メモ)
- target の読者全員が plan を読んでいる前提のチーム内資料
- API リファレンスなど語彙が codebase に直接マップされ、読者が grep で辿れる文書

## Core Pattern: 3 分類判定

検出した候補語を以下の 3 分類に振り分ける:

| 分類 | 例 | アクション | 理由 |
|---|---|---|---|
| **持ち込み可** | Flipper flag 名 (`fy26q3_ebis_client`)、class/file 名 (`Freee::Client`)、Jira ID (`XPROJ-663`)、Issue 番号 (`#34074`) | **維持** | codebase / 公開 issue tracker で grep 可能。読者が辿れる |
| **要 in-line 定義** | 文書内で **2+ 回**登場する有用な短縮形 (`Single Switch`, `Provider 内吸収型`) | **初出箇所で `用語 (= 短い説明)` を補う** | 略号として有用、定義 1 箇所追加で全箇所が読める |
| **要言い換えまたは削除** | 1 回しか出ない造語、内部番号 (`Critical-A`, `α/β/γ 層`, `AC-12`)、section anchor (`§設計詳細`) | **平易な日本語に書き換え、または文ごと削除** | 略す価値が無いか、参照先が target に無いため link 切れ |

## Detection Heuristics

**重要**: 本セクションは Step 2「候補抽出」専用。パターンにヒットした語は **false positive を含む候補リスト**。実際の分類は Step 3 の決定木で行う (heuristic ヒット ≠ 自動的に要対応)。

target 文書から以下のパターンを候補としてリストアップ:

| パターン | 候補例 | typical false positive (Step 3 で「持ち込み可」に倒れやすい例) |
|---|---|---|
| カタカナ + 「型」「主義」「原則」「論」「系」 | `Provider 内吸収型`, `短絡型`, `Critical-A/D 系` | `Faraday 系` (gem 名 + 系)、`同期型/非同期型` (一般用語) |
| 強調された (`**...**` / 「...」) 専門フレーズ | `**Single Switch**`, `「Provider 内吸収型」` | 強調された codebase 識別子、見出し用の強調 |
| アルファベットラベル + 数字: `[A-Z]+-[0-9a-z]+` | `Critical-A`, `AC-12`, `α 層` 番号 | `XPROJ-663` (Jira ID)、`AUTH-203` (Jira ID)、`PR4-a` 等 (target 内で全展開済なら OK) |
| ギリシャ文字 + 「層/相」: `[α-ω]\s*層` | `α 層`, `β 層`, `γ 層` | 数学/物理文脈の正当な α/β 層 |
| section anchor: `§...` | `§設計詳細`, `§Single Switch` | (基本 false positive なし、target 内に該当 section があれば OK) |
| フェーズ分類用語 | `rollout enabler`, `enabler` | `kill switch` (英語圏で確立済)、`feature flag` 等 |
| 数字 + 「象限/層」 | `4 象限`, `3 層` (文中で各要素が説明されていない場合) | OSI 7 層など公知の分類 |

**heuristic ヒット後の方針**: 列挙された語は**全件 Step 3 へ渡す**。Step 3 の決定木で分類されるまで「要対応」と決めつけない。

## Workflow

### 1. 入力収集 (Collect)

- **target**: 検査対象の文書 (PR body、Jira description、design doc、RFC 等)。ファイルパス or インラインテキスト
- **source plan**: target の生成元。Claude Code session で plan を扱った直後なら `~/.claude/plans/<topic>/plan.md` 等

両方を Read。

### 2. 候補抽出 (Extract candidates)

target 全文を読み、§Detection Heuristics の各パターンにマッチする語を列挙。

参考 grep 例:
```bash
# カタカナ造語パターン
grep -oE '[ァ-ヴー一-龥a-zA-Z]+(型|主義|原則|論|系)' <target>

# section anchor
grep -oE '§[^ ,。、）]+' <target>

# アルファベット + 番号ラベル
grep -oE '[A-Z][A-Za-z]*-[0-9a-z]+' <target>
```

### 3. 分類 (Classify) — 決定木

各候補語を以下の決定木に**上から順に**当てはめる。最初にヒットした分岐で分類確定:

```
Q1. codebase identifier / 公開規格名 / 公知の Jira/Issue ID か?
  YES → 【持ち込み可】 (例: Freee::Client, fy26q3_ebis_client, JWT, RFC 7519, XPROJ-663)
  NO  → Q2 へ

Q2. target 自身の中で**直近に定義/展開**されているか?
     (見出し直後の本文で挙動を平易に説明、bullet で全要素列挙、等)
  YES → 【持ち込み可 (target self-contained)】
  NO  → Q3 へ

Q3. source plan にしか定義がなく、target の読者は外部リソースで辿れないか?
  YES → Q4 へ (要対応)
  NO  → 【持ち込み可】 (公知用語など)

Q4. target 内の出現回数は?
  2+ 回 → 【要 in-line 定義】 (初出箇所で `用語 (= 短い説明)` を補う)
  1 回   → 【要言い換えまたは削除】 (平易な日本語に書き換え、または文ごと削除)
```

**Q2 の判定基準** (重要、しばしば衝突する):
- 見出しラベル + 直後本文に**意味が成立する平易な説明**があれば self-contained と判定
- ただし「説明に plan 内造語がさらに混入」していれば NO (例: `Single Switch: Single Switch Principle により ...` は self-contained ではない)
- 迷ったら「plan を見たことが無い同僚に target だけ渡して読み下せるか」を**音読**で確認

**Label vs Body の機能分離** (重要、Q2 が partial になる典型ケース):
- 構造が `**plan-only ラベル**: 平易な説明文…` の場合、**ラベルと本文を独立に扱う**:
  - **ラベル**: plan 内 navigation 用 → Q4 で「要言い換えまたは削除」(ラベルを平易表現に置き換え、または太字部を削除)
  - **本文**: 既に reviewer 用に書かれている → そのまま維持
- これは Q2 を partial で抜ける default ルート。
- 例: `**Single Switch**: Flipper の参照を 1 箇所に集約` → ラベルを `**Flipper 参照の 1 箇所集約**` に置換、本文は維持

**Q1 の判定基準**:
- codebase identifier: `git grep <語> | wc -l` が 1+ ヒット (プロジェクトルートで実行)
- 公開規格名: RFC/W3C/ISO/IETF 等で定義
- 公知の Issue/Jira ID: 公開 issue tracker でアクセス可能

### 4. 提案レポート (Dry-run)

書き換え前に提案レポートを提示し承認を取る。**Step 3 の決定木の Q1–Q4 のどの分岐で分類されたか**を併記すると、ユーザの誤検出疑念を減らせる:

```markdown
## 語彙チェック提案レポート

### 持ち込み可 (維持) — Q1 / Q2 該当
- (Q1) `fy26q3_ebis_client` (Flipper flag 名、codebase 検索可)
- (Q1) `XPROJ-663` (Jira ID)
- (Q1) `Freee::Client` (class 名)
- (Q1) `JWT`, `RFC 7519` (公開規格名、heuristic 未ヒットだが reviewer 誤検出疑念回避のため明示)
- (Q2) `PR4-a/b/c/d` (target L12-L20 で全 PR が展開済 = target self-contained)

### 要 in-line 定義 (target 内 2+ 回出現) — Q4 該当
1. **Single Switch** (3 箇所: L14, L42, L58)
   - 提案: 初出 L14 を `Single Switch (= Flipper 参照を 1 箇所に閉じ込める設計)` に変更
2. **Provider 内吸収型** (2 箇所: L26, L44)
   - 提案: 初出 L26 を `Provider 内吸収型 (= OIDC nil を Provider 内で吸収し caller の挙動を変えない方式)` に変更

### 要言い換えまたは削除 (1 回出現または番号ラベル) — Q4 該当
1. `rollout enabler` (L18) → 「Flipper による本番経路切替を可能にする土台」に言い換え
2. `§設計詳細` (L33) → target には該当セクションなし、文ごと削除または該当内容をインライン化

### 確認ポイント
- in-line 定義の文言は妥当か？
- 持ち込み可リストに漏れはないか？
- Q2 (target self-contained) の判定で見落としはないか？
```

**「持ち込み可」セクションの記述方針**:
- heuristic ヒットして Q1/Q2 で持ち込み可になった語は**全件明示** (false positive と判別したことを示す)
- heuristic 未ヒットだが reviewer が「これは plan 由来では?」と疑いそうな公開語 (JWT, RFC, Express 等) も**列挙推奨** (誤検出疑念の事前回答)
- ファイルパス / メソッド名のような明らかな codebase identifier は**省略可** (冗長になるため、代表例のみ)

### 5. 適用 (Apply)

承認後、Edit で target に修正を適用。

検証:
- in-line 定義を入れた語が target 内で初出箇所のみに定義があり、後続箇所はそのまま使われているか
- 削除した語の周辺文が文として成立しているか (主述破綻していないか)
- 要言い換えした箇所が、plan を見ない読者でも読み下せるか **再読**

## Quick Reference

| 操作 | コマンド / パターン |
|---|---|
| カタカナ造語検出 | `grep -oE '[ァ-ヴー一-龥a-zA-Z]+(型\|主義\|原則\|論\|系)' <target>` |
| section anchor 検出 | `grep -oE '§[^ ,。、）]+' <target>` |
| 番号ラベル検出 | `grep -oE '[A-Z][A-Za-z]*-[0-9a-z]+' <target>` |
| 候補語の出現回数 | `grep -c '<語>' <target>` |
| codebase 検索 (持ち込み可判定) | `git grep '<語>'` |
| in-line 定義形式 | `<用語> (= <短い説明>)` を初出箇所のみに |

## Common Mistakes

### ❌ 持ち込み可な codebase 固有名詞まで言い換えてしまう

**症状**: `Freee::Client` を「ライセンスクライアント」に言い換え。読者が grep できなくなり混乱が増す。

**修正**: class/file/Flipper flag 名は維持。読者は codebase で確認できる前提。

### ❌ in-line 定義を毎回繰り返して冗長化

**症状**: `Single Switch (Flipper 参照を 1 箇所に集約)` を出現箇所 3 回すべてに付ける。文書が読みづらくなる。

**修正**: 定義は **初出 1 回のみ**。2 回目以降は短縮形のまま使う。

### ❌ 番号ラベル / section anchor の機械的削除

**症状**: `§設計詳細` を機械削除。直前の「§設計詳細 を参照」が「を参照」だけ残り文として壊れる。

**修正**: 番号ラベル / anchor を削除する場合は**文単位で再構成**する。参照元が target に無いなら、参照先の要点を 1 文でインライン化するか、文ごと削除。

### ❌ source plan を未収集のまま target だけ点検

**症状**: target にある「Single Switch」が plan 内造語か codebase 由来か判別できないまま「要言い換え」に分類してしまう。

**修正**: source plan path を最初に確認。直前の Claude Code session で plan を扱っていれば `~/.claude/plans/<topic>/plan.md` を Read。無ければユーザに確認。

### ❌ Dry-run なしで直接書き換え

**症状**: 候補語をいきなり言い換え → 「この語は意図的に使った」と後で指摘される。

**修正**: 必ず提案レポートを先に提示し承認を取る。

## Real-World Impact

実証例: PR #39519 (Freee Sign の ebis 移行 PR4-b) を target に検査。

source: `~/.claude/plans/ebis/plan.md` (365 行)、target: PR body (約 80 行)。

検出された plan 内造語と分類:
- `Single Switch` (target 1 箇所、太字ラベル形式、plan §Single Switch Principle 由来) → Q4: 1 回 → **要言い換え** (Label vs Body 分離適用、ラベルを「Flipper 参照の 1 箇所集約」に置換、本文は維持)
- `Provider 内吸収型` (target 1 箇所、太字ラベル形式、plan §Provider 内吸収型 由来) → Q4: 1 回 → **要言い換え** (Label vs Body 分離適用、ラベルを「PublicApi 側で OIDC nil を吸収する戦略」に置換)
- `rollout enabler` (target 2 箇所、plan PR 進捗 table のフェーズ分類由来) → Q4: 2+ 回 → **要 in-line 定義** (初出箇所で `(rollout enabler = Flipper による本番経路切替を可能にする土台 PR)` を補う)

結果: plan 未読の PR レビュワーが PR body だけで設計判断を理解可能に。

## 併用推奨 skill

本 skill は以下の skill / command が **ローカル plan を source とする対外文書**を生成した直後に組み合わせると効果が高い:

- `/create-pr` — plan から PR description を生成 → 本 skill で語彙点検
- `/create-jira-issues` — plan からチケット生成 → 本 skill で description を点検
- `/finalize-plan` — 計画完成後、対外公開する design doc に派生させる際
- `/dry-ssot-text` — 同一文書内の重複集約 (本 skill とは独立した別目的)
