---
name: dry-ssot-text
description: Collapses repeated explanations of one concept into a single source of truth plus cross-references, while keeping navigation aids like TOCs and progress tables. Use when an AI-generated document (plan / design doc / RFC / PR description) has grown long with the same concept explained in multiple places, when the same why-explanation is repeated across multiple code comments, or when the user says "この文書の重複をまとめて" / "この文書を DRY にして" / "同じ説明が何回も出てくるので整理して". Prose duplication inside code comments is in scope; code structure duplication / refactoring is out of scope.
---

# DRY/SSOT Text Refactor

AI 生成の長文 (plan / design doc / RFC / PR / README) で同一概念が複数箇所で繰り返される症状を、1 箇所に集約 (Single Source of Truth) + 他箇所をクロスリファレンスに置換することで解消する。同時に navigation aid (TOC / checklist / progress table) は残す。

**核心原則**: 「同じ事実を 2 度書かない」だが「ナビゲーション目的の重複は別物」。

**対象範囲**: 文書に加えて**コードコメント内の説明文**も対象 (同じ why 説明・設計判断が複数コメントに散っている場合、正本を ADR / 1 箇所のコメントに集約し他は参照へ)。呼び出し側の識別子から正本コメントへ grep で到達できる場合、参照コメントは置かず削除してよい (1 行 why に参照コメントを足すと元と同じ長さに戻るため)。対象外はコード構造そのものの重複 (メソッド・ロジックの重複解消はリファクタリングの領分で本 skill は扱わない)。

## Task complexity tier

| Tier | 判定 | アクション |
|---|---|---|
| **skip** | 文書 <100 行 / 重複箇所数 ≤2 / 外向き説明資料 (顧客向け・ブログ) / API ref のような網羅列挙文書 | **skip** (集約効果薄) |
| **lite** | 100-300 行, 重複 3-5 箇所 | dry-run 省略、直接 Edit 可 (4. の dry-run レポートは出力しない)。適用後に「何を何箇所→1 箇所に縮約したか」の 1 行レポートは必須 (省略の監査痕跡) |
| **standard** (default) | 300+ 行 or 共有前文書 or 重複 6+ 箇所 | dry-run レポート必須 → 承認後 Edit |
| **deep** | 600+ 行 / 複数 doc 跨り (plan + design doc 一致) / 既存 cross-reference に依存 | dry-run + 各 reference 先のアンカー疎通検証 + 適用後の `grep -c` 重複ゼロ確認 |

**複数 tier 該当時の優先**: 1 文書が複数 tier の条件に該当する場合 (例: 55 行で skip の「<100 行」に該当するが重複 3 箇所で lite の「3-5 箇所」にも該当) は、**重複箇所数を優先**する。skip は「重複箇所数 ≤2」が必須条件 — 行数が短くても重複が 3+ なら lite 以上として集約に進む。重複箇所数は**同一概念ごとに数える** (複数の重複グループが併存する場合は最大のグループの箇所数で判定し、全グループを合算しない)。

**tier 名規約**: 4 tier (skip / lite / standard / deep) は本 skill 内の判定軸であり、他 skill の "standard" / "lite" 命名と直接対応しない (本 skill では 300+ 行が standard、100-300 行は lite)。other skill から「standard median な文書」と呼ばれる 200 行・3 箇所重複ケースは本 skill では **lite** tier として処理する。

## Core Pattern: 必要重複 vs 不要重複

| 種類 | 例 | DRY 化するか | 理由 |
|---|---|---|---|
| **不要: 説明文** | 同じ設計判断を PR1/PR2/PR3 で再記述 | **する** | 1 箇所更新で済む |
| **不要: 表/コード** | 同じ table が 2 箇所、片方に「再掲」 | **する** | 1 箇所更新で済む |
| **不要: 引用文** | 公式ドキュメントの同一一節を 2 箇所引用 | **する** | 引用元に集約 |
| **不要: 旧版が新版に包含** | 中間サマリ表が最終サマリ表に subsume / 粗い旧 QA が詳細 QA に含まれる | **する** | 詳細版を正本にし旧粗版は削除 or 1 行参照に縮約 (相互リンクでなく旧版を除く点が同一重複と異なる) |
| **不要: 同一対象の表記ゆれ** | 同じ ADR を `docs/adr/0004` と `ADR-0004` の 2 表記で参照 | **する** | 解決可能な方 (パス・正式 ID) へ全箇所寄せる (2 表記は同一概念の重複) |
| **必要: TOC / 進捗 table** | 章立て一覧、PR 進捗表 | **しない** | 俯瞰 navigation |
| **必要: checklist サマリ** | AC リスト 1 行 + 詳細は §設計詳細 | **しない** | 確認用 |
| **必要: header + body 同名** | 「§Provider 内吸収型」見出しと本文冒頭 | **しない** | index 機能 |

## Workflow

### 1. 重複の特定

文書全文を Read → 同一概念 (同じ事実、同じ table、同じコード片) が複数箇所で出現するパターンを列挙 → 上記判定表で「不要重複」「必要重複」に分類。

### 2. Canonical location の決定 (SSOT)

不要重複ごとに、唯一の真実源を 1 箇所に決める。

**推奨**: 文書末尾の **§設計詳細 / §参照** に専用セクションを設けて集約 (文書全体を散歩しなくて済む)。

**例外**: 概念が **文書冒頭の前提知識** (例: 「ゴール」「アーキテクチャ」) なら冒頭近くに配置。

**避ける**: 最初に出現する PR/章のセクション内 → 後の章で「§PR1 参照」と書かれ、PR1 更新時に他章の意味が崩壊。文書途中の任意位置 → 読み手が forward/backward 両ジャンプ必要。

### 3. クロスリファレンス置換

**remedy は文書の読まれ方で分岐する**: 参照される長文 (plan / design doc / RFC) は重複説明をアンカーリンク参照に置換する (下記)。一方、線形に通読される短文 (PR description / ~150 行以下の reader-facing 文書) は、アンカーリンク化せず**その場で言い換え・縮約して 1 箇所に寄せる** — アンカーリンクは線形読みに forward/backward ジャンプを強い、かえって可読性を下げる (PR description は skip ではなくこの言い換え remedy で処理する)。**skip しないと決めた線形短文は重複箇所数によらず lite 相当として扱い、dry-run を省略して直接 Edit してよい** (重複 ≤2 で skip 必須条件に形式上該当しても、言い換え remedy にルーティングした以上 tier 表の lite に落とす — workflow 駆動が宙に浮かないように)。以下のアンカーリンク手順は前者 (参照される長文) に適用する:

他箇所の説明文を markdown アンカーリンクで置換:

```markdown
<!-- Before -->
重要な設計判断: AuthGateway は単一の責務に閉じ込め、ユーザ管理や権限管理は別サービスに委譲する。

<!-- After -->
**設計判断**: §[重要な設計判断](#重要な設計判断) 参照
```

**置換時の注意**:
- セクション参照は markdown アンカーリンク `[表示文字列](#anchor)` 形式
- 参照は **その PR セクションの冒頭近く** に置く (実装の前に設計を読ませる)
- 各 PR セクションは「スコープ 1 文 + 設計判断リンク + 実装ファイル table」の三段構造を維持し、スコープ説明まで削らない (過 DRY 防止)
- **関連が弱い PR の扱い**: PR の内容が SSOT に直結しない場合、**default は省略** (リンクを貼らない)。関連性が補完的に有用なら 1 句で関連性を補足。迷ったら省略 (過リンク防止を優先)
- **既存表記スタイルの維持**: 元文書が散文ならそのまま散文で残す (表記スタイル変更は別 task)
- **AC / checklist 内のクロスリファレンス**: 括弧書き `(<参照テキスト>参照)` は括弧構造を保ちつつ中身をアンカーリンクに置換 (例: 元 `(Token rotation の挙動表参照)` → `(§[Token rotation 挙動表](#token-rotation-挙動表) 参照)`)

### 4. Dry-run レポート (standard / deep tier では必須 — 条件は tier 表が canonical)

tier 表の dry-run 要否は**下限**を定める — lite で省略可でも、**呼び出し側が dry-run を明示要求した場合は tier 問わず提示**する。いきなり書き換えず提案レポートを先に作る:

```markdown
## DRY 化提案レポート

### 不要重複 (集約候補)
1. **「AuthGateway 単一責務」** (3 箇所: L40, L75, L105) → §設計詳細 に集約
2. **Token rotation 表** (2 箇所: L120-128, L145-153) → §設計詳細 に集約

### 必要重複 (維持)
1. **PR 進捗 table** (L25-32) → index 機能、維持
2. **AC checklist** (L180-200) → 確認用、維持

### 想定される行数削減
元: 250 行 → 後: 約 180 行 (28% 削減)

### 確認ポイント
- canonical location を §設計詳細 (文書末尾) に置く案で問題ないか?
- 各 PR セクションのスコープ説明 (1 文) は維持するか?
```

### 5. 実適用

承認後 (対話承認者が不在の自動実行フローでは、dry-run レポートを提示したうえで self-approve して適用に進んでよい — レポート提示自体が監査痕跡)、Edit / Write で書き換え。検証:
- `grep -c "<重複していた canonical フレーズ>" <file>` で 1 件のみヒット
- 文書を冒頭から線形に読み、参照リンクが機能しているか
- `wc -l` で行数測定 (**ただし行数は増減両方ありうる**。重視するのは **同一情報の重複箇所数の減少**、行数ではない)

## Quick Reference

| 操作 | コマンド / パターン |
|---|---|
| 重複検出 | `grep -nE "<重複候補フレーズ>" <file>` |
| アンカーリンク形式 | `[表示文字列](#anchor)`。anchor 生成規則: ASCII を小文字化 → 空白をハイフン化 → 記号 (`§ : / . ( )` 等) と先頭/末尾の空白を除去 (日本語文字は残す)。例: 見出し `## §設計詳細` → `#設計詳細` / `## Token rotation: 挙動表 (v2)` → `#token-rotation-挙動表-v2`。生成後は §5 検証で実リンク疎通を確認 (記号入り見出しはずれやすい) |
| dry-run トリガ | tier 表の standard / deep に該当 (300+ 行 or 共有前文書 or 重複 6+ 箇所) |
| SSOT 配置先 | 文書末尾の §設計詳細 / §参照 |

## Advanced

- [references/pitfalls.md](references/pitfalls.md) — Common pitfalls (過 DRY / TOC 削除 / canonical 任意位置 / dry-run 飛ばし / 必要重複の判定漏れ)

## 併用推奨 skill

- `/purge-private-vocab` — plan 由来の対外文書から造語を除去 (本 skill とは独立した別目的)。purge-private-vocab の出現回数判定 (grep カウント) は完全一致依存のため、表記ゆれがある文書では本 skill で表記統一を先に行うと過小カウントを防げる (本 skill → purge-private-vocab の順を推奨)
- `/express-intent-in-code` — コードコメントの why 重複は、まず express-intent-in-code (T3: コメント→名前/型/定数 蒸留) で名前・型へ蒸留できるか判断する。蒸留できなかった真の why の文章重複だけを本 skill が集約する (express-intent-in-code が前段)
