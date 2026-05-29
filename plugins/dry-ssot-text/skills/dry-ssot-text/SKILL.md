---
name: dry-ssot-text
description: Use when an AI-generated document (plan / design doc / RFC / PR description) has grown long with the same concept explained in multiple places.
---

# DRY/SSOT Text Refactor

AI 生成の長文 (plan / design doc / RFC / PR / README) で同一概念が複数箇所で繰り返される症状を、1 箇所に集約 (Single Source of Truth) + 他箇所をクロスリファレンスに置換することで解消する。同時に navigation aid (TOC / checklist / progress table) は残す。

**核心原則**: 「同じ事実を 2 度書かない」だが「ナビゲーション目的の重複は別物」。

## Task complexity tier

| Tier | 判定 | アクション |
|---|---|---|
| **skip** | 文書 <100 行 / 重複箇所数 ≤2 / 外向き説明資料 (顧客向け・ブログ) / API ref のような網羅列挙文書 | **skip** (集約効果薄) |
| **lite** | 100-300 行, 重複 3-5 箇所 | dry-run 省略、直接 Edit 可 (4. の dry-run レポートは出力しない) |
| **standard** (default) | 300+ 行 or 共有前文書 or 重複 6+ 箇所 | dry-run レポート必須 → 承認後 Edit |
| **deep** | 600+ 行 / 複数 doc 跨り (plan + design doc 一致) / 既存 cross-reference に依存 | dry-run + 各 reference 先のアンカー疎通検証 + 適用後の `grep -c` 重複ゼロ確認 |

**tier 名規約**: 4 tier (skip / lite / standard / deep) は本 skill 内の判定軸であり、他 skill の "standard" / "lite" 命名と直接対応しない (本 skill では 300+ 行が standard、100-300 行は lite)。other skill から「standard median な文書」と呼ばれる 200 行・3 箇所重複ケースは本 skill では **lite** tier として処理する。

## Core Pattern: 必要重複 vs 不要重複

| 種類 | 例 | DRY 化するか | 理由 |
|---|---|---|---|
| **不要: 説明文** | 同じ設計判断を PR1/PR2/PR3 で再記述 | **する** | 1 箇所更新で済む |
| **不要: 表/コード** | 同じ table が 2 箇所、片方に「再掲」 | **する** | 1 箇所更新で済む |
| **不要: 引用文** | 公式ドキュメントの同一一節を 2 箇所引用 | **する** | 引用元に集約 |
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

### 4. Dry-run レポート (300 行+ または共有前文書では必須)

いきなり書き換えず提案レポートを先に作る:

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
| アンカーリンク形式 | `[表示文字列](#anchor)`。anchor は小文字 + スペース → ハイフン |
| dry-run トリガ | 300 行+ または レビュー前 |
| SSOT 配置先 | 文書末尾の §設計詳細 / §参照 |

## Advanced

- [references/pitfalls.md](references/pitfalls.md) — Common pitfalls (過 DRY / TOC 削除 / canonical 任意位置 / dry-run 飛ばし / 必要重複の判定漏れ)

## 併用推奨 skill

- `/purge-private-vocab` — plan 由来の対外文書から造語を除去 (本 skill とは独立した別目的)
