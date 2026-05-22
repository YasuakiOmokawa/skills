---
name: purge-private-vocab
description: Use after generating PR description, Jira ticket, design doc, RFC, or other reader-facing text from a local plan/spec file, when readers don't share the source plan.
---

# Purge Private Vocabulary

ローカルプランの造語・略号・番号ラベル (`Single Switch`, `Provider 内吸収型`, `Critical-A`, `α 層`, `AC-12`, `§設計詳細` 等) が plan 由来の対外文書に持ち込まれる症状を検出し、読者が plan を持たない前提で書き換える。

**核心原則**: 「読者が source plan を持っていない前提で読み下せるか」。書き手 (AI 自身) が plan を読んだ状態で書くと無意識に plan 内造語を持ち込む。

## Task complexity tier

| Tier | 判定 | アクション |
|---|---|---|
| **lite (skip)** | target = plan そのもの / 読者全員が plan 共有済のチーム内資料 / API ref (codebase 直 map) | **skip** |
| **lite** | target ≤300 字 or plan-only 語ヒット ≤2 | 1-pass 直接修正 (dry-run レポート省略、Step 4 飛ばして Step 5 のみ) |
| **standard** (default) | 中規模 doc (PR description / Jira description 等、300-2000 字) | Step 1-5 全実行、dry-run レポート提示 → 承認後 Edit |
| **deep** | design doc / RFC / 公開資料 / 2000+ 字 | dry-run + 適用後の再読検証必須 + heuristics-and-pitfalls.md 全件チェック + 下記 **deep 必須前置**を Step 1 で実施 |

**deep 必須前置** (Step 1 の入力収集を拡張):
1. **target の文構造を直読み**: `**用語**: 説明` のような Label vs Body 構造かを目視確認し、Label vs Body 分離ルートの適用可否を Step 3 までに確定する
2. **AC-* / Critical-* / RFC-* 等の ID 紐付け**: target に登場する全 ID (`AC-7`, `Critical-A` 等) を source plan / analysis ファイルから 1:1 で索引し、各 ID の元内容を「展開」または「文ごと削除」のどちらにするか Step 4 提案レポートに明記する
3. **layer label (α/β/γ 層 等) の対応コンポーネント名解決**: source plan から各 layer の実コンポーネント名 (Web / Service / Persistence 等) を引き、推測補完にせず実値で言い換える

## Core Pattern: 3 分類

| 分類 | 例 | アクション |
|---|---|---|
| **持ち込み可** | Flipper flag (`fy26q3_ebis_client`)、class/file 名、Jira ID (`XPROJ-663`)、Issue 番号 (`#34074`) | **維持** |
| **要 in-line 定義** | 2+ 回登場する有用な短縮形 (`Single Switch`, `Provider 内吸収型`) | **初出箇所で `用語 (= 短い説明)` を補う** |
| **要言い換えまたは削除** | 1 回しか出ない造語、番号 (`Critical-A`, `α 層`, `AC-12`)、section anchor (`§設計詳細`) | **平易な日本語に書き換え、または文ごと削除** |

## Workflow

### 1. 入力収集

- **target**: 検査対象 (PR body、Jira description、design doc 等)。ファイルパス or インラインテキスト
- **source plan**: target の生成元 (`~/.claude/plans/<topic>/plan.md` 等)

両方を Read。

### 2. 候補抽出

target 全文から [references/heuristics-and-pitfalls.md](references/heuristics-and-pitfalls.md) の検出パターン (カタカナ+型/主義/原則/論/系、強調フレーズ、ラベル+番号、ギリシャ文字+層、`§...` anchor、フェーズ用語、数字+象限/層) にマッチする語を**全件**列挙する。heuristic ヒット ≠ 要対応で、分類は Step 3 で決める。

### 3. 分類 — 決定木

各候補語を**上から順に**当てはめる。最初にヒットした分岐で確定:

```
Q1. codebase identifier / 公開規格名 / 公知の Jira/Issue ID か?
  YES → 【持ち込み可】 (例: Freee::Client, fy26q3_ebis_client, JWT, RFC 7519, XPROJ-663)
  NO  → Q2

Q2. target 自身の中で**直近に定義/展開**されているか?
     (見出し直後の本文で挙動を平易に説明、bullet で全要素列挙、等)
  YES → 【持ち込み可 (target self-contained)】
  NO  → Q3

Q3. source plan にしか定義がなく、target の読者は外部リソースで辿れないか?
  YES → Q4 (要対応)
  NO  → 【持ち込み可】 (公知用語)

Q4. target 内の出現回数は?
  2+ 回 → 【要 in-line 定義】 (初出箇所で `用語 (= 短い説明)` を補う)
  1 回   → 【要言い換えまたは削除】 (平易な日本語に書き換え、または文ごと削除)
```

**Q1 判定**: codebase identifier = `git grep <語>` が 1+ ヒット、公開規格 = RFC/W3C/ISO/IETF 等、公知 Issue/Jira = 公開 tracker でアクセス可。

**Q2 判定**: 見出し+直後本文に平易な説明があれば self-contained。ただし説明に plan 内造語がさらに混入していれば NO。迷ったら「plan 未読の同僚が target だけ読み下せるか」を音読で確認。

**Label vs Body 分離** (Q2 の partial 抜けに使う既定ルート): 構造が `**plan-only ラベル**: 平易な説明文…` の場合、ラベルは Q4 で「要言い換えまたは削除」、本文は維持。例: `**Single Switch**: Flipper の参照を 1 箇所に集約` → ラベルを `**Flipper 参照の 1 箇所集約**` に置換、本文は維持。

### 4. 提案レポート (Dry-run、書き換え前)

書き換え前に提案レポートを提示し承認を取る。Q1–Q4 のどの分岐で分類されたかを併記:

```markdown
## 語彙チェック提案レポート

### 持ち込み可 (維持) — Q1 / Q2 該当
- (Q1) `fy26q3_ebis_client` (Flipper flag 名、codebase 検索可)
- (Q1) `XPROJ-663` (Jira ID)
- (Q2) `PR4-a/b/c/d` (target L12-L20 で全 PR が展開済)

### 要 in-line 定義 (2+ 回出現) — Q4 該当
1. **Single Switch** (3 箇所: L14, L42, L58)
   - 提案: 初出 L14 を `Single Switch (= Flipper 参照を 1 箇所に閉じ込める設計)` に変更

### 要言い換えまたは削除 (1 回出現または番号ラベル) — Q4 該当
1. `rollout enabler` (L18) → 「Flipper による本番経路切替を可能にする土台」に言い換え
2. `§設計詳細` (L33) → target に該当セクションなし、文ごと削除
```

「持ち込み可」セクションは reviewer 誤検出疑念回避のため、heuristic ヒットして Q1/Q2 で抜けた語と、heuristic 未ヒットだが疑われそうな公開語 (JWT, RFC, Express 等) を明示する。

### 5. 適用

承認後、Edit で target に修正を適用。検証: 初出箇所のみ定義があるか / 削除した語の周辺文が文として成立しているか (主述破綻していないか) / 言い換え箇所が plan 未読でも読み下せるか **再読**。

## Quick Reference

| 操作 | コマンド |
|---|---|
| 候補語の出現回数 | `grep -c '<語>' <target>` |
| codebase 検索 (Q1 判定) | `git grep '<語>'` |
| in-line 定義形式 | `<用語> (= <短い説明>)` を初出箇所のみに |

## Advanced

- [references/heuristics-and-pitfalls.md](references/heuristics-and-pitfalls.md) — 検出パターン全表 + grep 例 + Common pitfalls (codebase identifier の誤書換、in-line 定義の冗長化、anchor の機械削除で文破綻、source plan 未収集、dry-run 飛ばし)

## 併用推奨 skill

本 skill は以下が **ローカル plan を source とする対外文書**を生成した直後に組み合わせると効果が高い:

- `/create-pr` — plan から PR description を生成 → 本 skill で語彙点検
- `/create-jira-issues` — plan からチケット生成 → 本 skill で description を点検
- `/finalize-plan` — 計画完成後、対外公開する design doc に派生させる際
- `/dry-ssot-text` — 同一文書内の重複集約 (本 skill とは独立した別目的)
