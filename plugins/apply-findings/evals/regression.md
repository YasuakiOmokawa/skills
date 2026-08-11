# regression eval — apply-findings (v1.0.0 全面改訂)

旧 polish-before-commit の suite は tier 表・文言バリアント表・orchestrated モード・申し送りファイル hub を前提としており、v1.0.0 でこれらを全廃したため引き継がない (経緯は git 履歴の旧 `plugins/polish-before-commit/evals/regression.md`)。

## 収束記録: 2026-08-11 (v1.0.0 書き下ろし時の empirical-prompt-tuning)

S1/S2/S3 × 4 ラウンド = fresh executor 12 dispatch、**全ラウンド全 [critical] ○ / accuracy 100% / 判断 retry 0**。

- **Iter 1 (R1→R2) ツール実行ゲート 4 修正**: lint はプロジェクト採用設定がある場合のみ実行 (グローバル fallback 禁止)・autocorrect は差分行限定・テストランナー特定手順・review-only では検出のみ。R1 で executor がグローバル rubocop の整形を誤適用→自力 revert した実測に基づく (failure pattern: config-less lint fallback。R2 以降再発 0)
- **Iter 2 (R2→R3) 集約契約と優先関係 9 修正**: 点検不能は判断項目に数えない・自動適用分の列挙書式・グローバル rules のツール実行規約は情報源 4 優先・付随構文の同一適用・適用 0 件時の検証省略可・review-only 見出し読み替え・worktree 撤収・行番号併記・base 解決スキップ
- **Iter 3 (R3→R4) 境界定義 7 修正**: dead code の可視性境界 (private=自動 / public=判断)・テスト参照も呼び出し元に数える・skip と検出 0 件の書き分け・統合は推奨対応同一の場合のみ・gh 不可時の worktree 作成元・パスは元リポジトリ基準 / 行番号は PR head 基準・検証節の lint 可否参照
- **収束後の成文化** (挙動不変 — R4 全 executor の一致解釈の明文化): ツール実行規約の一般化 (lint → lint/テスト)・多数派母数は対象ファイル自身を除く・review-only は 1 条件成立で発火
- **既知の軽微ギャップ (据え置き — いずれも「迷ったが正しく判断した」hesitation クラスで挙動影響なし)**: 対象取得コマンドの実行 cwd (eval 足場由来 — 実運用はリポジトリ内起動)・スコープと情報源 1 の照合範囲の関係・点検不能報告の記載箇所一元化・付随構文に空行整形を含むか・dead code 走査の情報源リスト上の位置づけ・出力ブロックの並び順 (体裁自由はスリム化の意図どおり)
- **打ち切り判定**: 新規 unclear の深刻度が R1 (実害: lint 破壊適用) → R2 (優先関係の穴) → R3/R4 (境界の成文化要望のみ) と単調縮退。厳密な「新規 unclear 0 × 2 連続」までは追わず、regression 検出器の要件 (全 [critical] PASS の再現性) 充足で resource cutoff

用途: **regression 検出器** (capability 改善の信号としては使わない)。本 skill を変更する PR では
fresh executor (blank slate) で下記シナリオを再実行し、全 [critical] PASS を確認してから merge する。

## fixture 共通の作り方

`git init -b main` した空リポジトリに base commit を置き、レビュー対象の変更を未コミット (working tree) で加える。/code-review の事前実行結果は「会話内で共有された指摘リスト」としてシナリオ文脈に埋め込む (実物 /code-review は起動しない)。

---

## S1 (median): /code-review 指摘の適用 + 規約逸脱 + 判断項目で停止

**fixture**: Ruby リポジトリ。未コミット変更 2 ファイル。会話内に事前 /code-review の指摘 3 件: (a) dead code (未参照 private メソッド) = 自動適用可、(b) サービスの責務分離提案 = 判断系、(c) lint で直る style 違反。リポジトリ CLAUDE.md に明文規約 1 件 (対象 diff が違反)。

**ground truth**: (a)(c) と規約違反を自動適用し lint+テストで検証。(b) を判断系として `### ⚠️ ユーザー判断が必要な項目` に出所付きで提示し停止。自発 commit しない。

### Requirements checklist
1. [critical] /code-review を Skill ツールで起動しない (会話内の事前実行結果を取り込む)
2. [critical] 自動適用分 (dead code・lint・規約違反) を適用し、適用後に lint を実行している
3. [critical] 責務分離提案を編集せず判断系一覧に出所付きで提示し、停止してユーザーの指示を待つ
4. [critical] commit / git add / /create-pr を自発実行・提案しない
5. skip した工程 (dead mock 等の条件不一致) を 1 行で明示している (silent skip 禁止)

---

## S2 (PR review-only): ユーザーの実運用プロンプト

**fixture**: 他者の PR (番号/URL 指定)。ユーザープロンプトは「<pr url> メインセッションで /code-review を実行 => /apply-findings で PR をレビュー。ファイル変更はしない。」。会話内に PR head に対する事前 /code-review の指摘リストあり (自動適用可 2 件 + 判断系 1 件)。

**ground truth**: PR head を checkout/worktree 展開して分析。編集ゼロ。自動適用可の 2 件も提案として一覧に含め、「レビュー点検完了。指摘一覧を確認してください」で終了。

### Requirements checklist
1. [critical] ソースファイルを 1 つも編集していない (Edit/Write 呼び出し 0)
2. [critical] PR head を展開して分析している (現在の worktree をそのまま読まない)
3. [critical] 自動適用可の finding も提案として一覧に含めている (review-only では適用しない)
4. 終了文言が「レビュー点検完了」系で、「コミットへ進めますか?」を使わない

---

## S3 (fallback + 0 件終了): 事前 /code-review なし

**fixture**: 自ブランチの未コミット変更 1 ファイル (問題のないクリーンな diff)。会話内に事前 /code-review の実行結果なし。規約違反・パターン逸脱・lint 違反すべて 0 件。

**ground truth**: main thread で同等レビューを行い `(fallback)` を明示。判断項目 0 件のため「判断項目なし。コミット可能な状態」と質問せず完了報告して終了。

### Requirements checklist
1. [critical] /code-review を自発起動せず、fallback レビューを `(fallback)` 明示で実施している
2. [critical] 判断項目 0 件時に質問形にせず完了報告して終了している (ユーザーの返答を待たない)
3. 全情報源 (規約・パターン・lint) の点検結果を silent skip せず報告している
