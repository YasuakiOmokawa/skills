# 境界とスコープ

## スコープ内 / 外

**スコープ内**:
- 対象が確定した working code 1 点 (メソッド/値/型) を受け、名前/型/構造/テストを why 表明形へ**深く変換**する (経路1)。出力は before/after 変換・改名 3 案・昇格削除コメント一覧・残す真 why。
- `/review-code-quality` が needs-judgment として申し送った naming/凝集 finding を受け取り、変換を実行する**直列の後段**を担う。
- **生成時 (経路2)**: いま書いているコードに [generation-recipe.md](generation-recipe.md) の3つの瞬間を適用する。対象は新規に書く行のみで、既存行の改名は経路1 の手続き (Step 0 の適用判定) に従う。生成時適用は drive-by 改名に当たらない (既存コードを触らないため)。

**スコープ外**:
- diff 全体を広く浅くスキャンして「何を直すか」診断すること → `/review-code-quality` の責務。本スキルに診断基準を再掲しない。
- working code でない (今回追加/変更していない) 隣接メソッドの drive-by 改名 → Surgical Changes を継承し対象 1 点に絞る。
- 規約テキスト依存の機械的コメント整形 → `/polish-before-commit` Step 7。
- コードから絶対に読めない真の why 4 類型 (外部仕様/トレードオフ根拠/危険・順序依存/将来予定) の撲滅 → 昇格を試みず残す。ゴールは撲滅でなく純化。
- 共有ドメイン語が無いのに「それっぽい」語を造って段4 に上げること → 造語は禁止。段4 は**実在証拠への接地が前提**で、探索が空振りなら段3 で据え置き探索ログを残す ([domain-abstraction.md](domain-abstraction.md))。
- 段4 へ到達した型を**全 call site へ波及させる広域改名** → 対象 1 点のみ変換する (Surgical Changes)。

## review-code-quality との責務分担

| | `/review-code-quality` (診断器) | `express-intent-in-code` (変換器) |
|---|---|---|
| 入口 | `origin/develop...HEAD` の diff 全体 | 直す対象が確定した working code 1 点 |
| 広さ×深さ | 広く浅く (凝集/結合 + 条件付き業務副作用の 3 観点。可読性は組み込み /code-review へ委譲) | 狭く深く一点突破 |
| 出力 | 指摘リスト + 重大度 | before/after 変換 + 改名 3 案 + 昇格/残置コメント |
| 自動適用 | なし (🔴/🟠 は全件 /polish-before-commit へ申し送り。機械的な自動修正は組み込み /code-review の --fix が担当) | 変換が本体 (lint/test で都度検証) |
| トリガ | self-review 完了時・PR 前・domain attribute 更新時 | 対象が判明し「目的を名前で表明したい」時 |

## 非重複の保ち方 (5 項)

1. **診断基準を再掲しない**: 凝集度・結合度スコアリングは review-code-quality、ambiguous name / boolean 否定形 / lint で拾える naming は組み込み /code-review が既に持つ。本スキルに転記せず、診断は委譲する。
2. **広く浅く vs 狭く深く**: review-code-quality は diff 全体、本スキルは対象 1 点を最上段まで。
3. **入口の違い**: review-code-quality は「何を直すか」を診断、本スキルは「直す対象が確定した後」の変換を担う。
4. **Surgical Changes の継承**: 動くコードの命名を要求なく触らない。対象メソッドが今回の変更対象である時に限り適用する。**対象 1 点の昇格に内在する分割 (T2 で同一本体から機構メソッドを抽出する等) は「1 点の変換」に含む** — スコープ違反になるのは、抽出した新型を**全 call site へ波及**させること・依頼外の**隣接メソッドを改名**すること・ガード/述語の改名 (既存述語があれば段4 snap より既存慣習を優先し別コミット) の方。
5. **dry-ssot-text との役割分担**: 「同一 why コメントの重複」を両スキルとも検出対象に掲げるが、蒸留先が違う。T3 (コメント→名前/型/定数 蒸留) で名前/型/定数へ昇格できる重複は本スキルが担当し、蒸留しきれず文章のまま複数箇所に残る真の why コメントの集約は `/dry-ssot-text` が担当する (本スキルの T3 で削りきれなかった残りを引き取る後段)。

## 直列運用フロー

```mermaid
flowchart LR
  A[実装完了] --> B[/review-code-quality\n診断]
  B -->|naming/凝集 finding\nを needs-judgment 申し送り| C[/express-intent-in-code\n変換]
  C --> D[/polish-before-commit\n規約整形・最終仕上げ]
```

診断は前者・変換は後者。この責務分担を崩さない。
