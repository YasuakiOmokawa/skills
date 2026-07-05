# regression eval (empirical-prompt-tuning 収束時保存)

収束記録: 2026-06-12 (v3.28.0 PR)。Iter1-3 で fresh executor が全 [critical] ○ / accuracy 100% / retries 0。
再実行記録: 2026-07-06 (v1.20.0 PR)。deep-module サブケース b が「記載なし事項の ❌ 断定 → 総合降格」で × となり、deep-module-reviewer.md へ総合ラベルの集約規則と「記載が無いは反例ではない (Unknown 行き)」を明文化して修正。修正後 deep-module a/b/c + matrix routing (Step 6 保存の checklist 4 込み) 4/4 全 [critical] ○。
用途: **regression 検出器** (capability 改善の信号としては使わない)。本 skill を変更する PR では
fresh executor (blank slate, Task dispatch) で下記シナリオを再実行し、全 [critical] ○ を確認してから merge する。
実行方法は empirical-prompt-tuning の「Subagent invocation contract」に従う (成果物はインライン、ファイル編集禁止)。

## シナリオ: greenfield reviewer (agents/anti-pattern-checker.md または ddd-reviewer.md)

コード未着手・対象リポジトリ不在 (Grep 反例検索が成立しない) の plan: OrderDiscountService 新設 (責務 1 つ / public method 1 / 外部 IO なし / 戻り値 Integer)。チェック観点ごとに判定 (✅/⚠️/❌/Unknown) を出させる。

### Requirements checklist
1. [critical] plan から forward-looking に判定できる観点を Unknown にしない (Unknown 乱発しない)
2. plan からも判定材料が得られない観点のみ `<観点>: Unknown (理由)` 形式で棄権
3. デフォルト ⚠️ 原則を維持し、greenfield のため ✅ 項目にも判定根拠を 1 行付記
4. 全観点の判定を列挙 (黙って省略しない)

## シナリオ: deep-module-reviewer (agents/deep-module-reviewer.md)

収束記録: 2026-06-21 (v1.18.0 PR、codebase-design 編入)。Iter1-5 で fresh executor が全 [critical] ○ / accuracy 100% / 過学習チェック (hold-out 部分浅い ⚠️) PASS。
3 つの提案モジュールに deep-module-reviewer を greenfield 適用する。

### シナリオ a: 浅い pass-through モジュール
全 method が他オブジェクトへの 1:1 委譲 (例: 通知 Service の各 method が `@mailer.X(...).deliver_later` だけ)。

Requirements checklist:
1. [critical] 総合を「浅い (shallow ❌)」と判定する (deep ✅ にしない)
2. [critical] deletion test を適用し、消しても複雑さが再出現しない (pass-through) と具体的に示す
3. criticism-first を維持し、Design It Twice の発散生成を default で開始しない (再設計は親へ escalation)
4. 浅さを YAGNI / 過剰抽象でなく interface の深さ (depth-as-leverage) で論じる

### シナリオ b: 深いモジュール (誤検出抑制)
小さな interface (1 method) の背後に多数の規則を隠す (例: 価格計算が税・割引・プロモ・丸めを内部に隠す)。

Requirements checklist:
1. [critical] 誤って「浅い」と判定しない (deep ✅ と認める)
2. deletion test で消すと複雑さが複数の呼び出し側に再出現すると示す
3. greenfield のため ✅ 項目にも判定根拠を 1 行付記する (1 行集約にしない)

### シナリオ c: 部分的に浅いモジュール (中間 ⚠️ への汎化 / hold-out)
pass-through method と実質ロジックを隠す method が混在 (例: `find` は委譲のみ + `dormant_candidates` は休眠規則を隠す)。

Requirements checklist:
1. [critical] 全体を「deep ✅」一辺倒と誤判定しない (pass-through の method を見落とさない)
2. [critical] pass-through の method を浅い部分として具体的に指摘する
3. greenfield のため観点ごとに判定根拠を 1 行付記する

## シナリオ: matrix routing (SKILL.md)

新規 module / interface 設計 (深さ・seam が論点) の plan に対し reviewer subset を選ぶ。

### Requirements checklist
1. [critical] 選択した reviewer subset に `deep-module-reviewer` を含める
2. [critical] `anti-pattern-checker` を含める (常時必須)
3. reviewer を選んだ根拠を matrix の該当行 (Q1/Q2 分岐 or None ブランチ行 or Row 3 tier) で説明する
4. [critical] Step 6 でチャット表示に加え、プランパスから導出した `<plan>.design-review.md` へ保存する (拡張子前に `.design-review` を挿入)。保存内容に `## Fatal 残存` (0 件) と `## Acceptable 残存リスク` (1 行 1 件、空なら「該当なし」) の 2 節を含める (v1.20.0 で追加 — オーケストレータ監査パックの前提部品)
