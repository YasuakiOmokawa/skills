# regression eval (empirical-prompt-tuning 収束時保存)
再実行記録: 2026-07-26 (v1.30.0 PR / Claude 5 世代ガイドライン適合)。5 reviewer に逐語複製されていた判定規律 3 件 (criticism-first / Unknown 棄権 / 出力粒度) を references/reviewer-judgment-rules.md へ集約し、reviewer-modes.md の fatal 再掲リストを削除 (escalation-rules.md の SSOT ポインタのみ残置)。greenfield / deep-module a・b・c / matrix routing / PoC 経由 grounding A を fresh executor で再実行し [critical] 15/15 ○。新共有ファイルの Read を 6/6 で確認、2026-07-06 の「記載なし事項の ❌ 断定」regression 再発なし。§9 の ❌ 経路は未再実行 (差分が判定規律と fatal 分類に閉じるため S5/S6 の全実行で代替被覆と判断)。

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

## シナリオ: 委譲実行 (subagent として起動された場合)

収束記録: 2026-07-07。baseline (Iter1) で委譲実行時の入力解決順位不明・Step3再実行時のstep番号ズレ・プラン不在時のStep4/6分岐未規定・`${CLAUDE_PLUGIN_ROOT}`解決規則不在を観測し、SKILL.md に `## 委譲実行` 節を新設して解消。Iter2・Iter3・hold-out (計5 fresh executor) で checklist 全 [critical] ○ / accuracy 100% を維持。tool_uses/duration はラウンドにより ±10%/±15% を外れる回があったが (Scenario B の duration が Iter3 で +27%)、機能面 (checklist 合否) には影響なし。3 イテレーション連続で新規不明点 0 には至らず (テーマは毎回異なる軽微なドキュメント精度指摘のロングテール) 発散と判定し、追加の構造修正は打ち切った。詳細は本節の記述を参照 (Gotchas への転記は未実施 — 判定規則側に inline 反映済みのため)。

### シナリオ A: プランファイルあり (Task 経由の委譲)

`Task(subagent_type="general-purpose")` で起動され、既存プランファイル (greenfield 新規機能、配置・パターン判定が争点) のパスを渡されて委譲実行する。

Requirements checklist:
1. [critical] Q1-Q3 の判定に基づき reviewer subset が決定され、選定された reviewer 名が最終報告に明記されている
2. [critical] Devil's Advocate (Step 5) が Step 3 の reviewer 指摘と異なる角度の指摘を出し、対話待ちで停止せず Step 6 まで完遂している
3. `<plan>.design-review.md` が Write され、内容が最終報告と一致している
4. 最終メッセージに保存先パスが明記されている
5. Step 4 の指摘反映方法が SKILL.md の規定 (プランを直接 Edit し要約貼り付けをしない) に沿っている、または致命指摘が無かった旨が明記されている

### シナリオ B: プランファイル不在 (feature description のみ)

`Task(subagent_type="general-purpose")` で起動され、プランファイルを作成していない自由文の feature description (auth territory 相当) のみでレビューを依頼される。

Requirements checklist:
1. [critical] 自由文の feature description から Q1-Q3 を判定し、reviewer subset を決定してレビュー内容をチャット応答内に提示している
2. [critical] プランファイルが存在しないため `<plan>.design-review.md` への Write を試みておらず、保存を skip した旨を最終メッセージで明示している
3. Devil's Advocate (Step 5) が実行され、fatal / acceptable の判定が最終報告に含まれている
4. 質問待ちで停止せず、レビュー結果を返して完結している
5. territory 該当を認識し、reviewer subset・DA モードの選定にそれが反映されている

### シナリオ C (hold-out): 指定されたプランファイルパスが存在しない

`Task(subagent_type="general-purpose")` で起動され、プランファイルパスを渡されるが実体が存在しない (作成前に消えた、パス誤りなど)。

Requirements checklist:
1. [critical] パスが存在しないことを検知し、内容を捏造せず、質問して待つ状態にせず、その旨を最終メッセージで明示して完結している
2. [critical] 存在しないファイルパスへの Write/Edit を試みてエラーになっていない
3. 最終メッセージが「プランファイルが見つからない」事実を明示しており、内容を推測で埋めた気配がない
4. 委譲実行特有の入力解決順位 (Plan File Info / 会話履歴を参照しない) を踏まえた挙動になっている

## シナリオ: PoC 経由 grounding (Step 0 / Step 5.2)

収束記録: 2026-07-07。Step 0 に「プラン本文が PoC の仮説 ledger やマッピング表を別ファイルで参照している場合はそれも Read する」、Step 5.2 に「PoC 仮説 ledger・マッピング表も grounding 材料に含め、対応済み・意図的 deferral の論点は fatal 化しない」を追加した回の検証。baseline (Iter1) で median (対応先チケット明記の deferral) + greenfield edge (PoC 材料なし) の 2 シナリオが即座に全 [critical] ○ / accuracy 100%。fresh executor 2 巡目 (Iter2) + hold-out (対応先チケットの無い「killed」ケースへの一般化確認) でも同様に全 [critical] ○ を維持し、2 round 連続で本テーマに関する新規不明点 0 のため即時収束、プロンプト修正は不要だった (baseline から文言変更なしで収束)。escalation-rules.md の ❌ カウント単位・Task complexity tier の Row 2/3 境界・Step 4 の actionable ⚠️ 判定基準に関する不明点も複数観測されたが、いずれも今回の Step 0 / Step 5.2 差分とは無関係な既存箇所であり、同日の別 PR (委譲実行) の eval で「発散、追加修正打ち切り」と既に判定済みの領域と重複するため、本ラウンドの修正対象には含めていない (Gotchas への 1 件追記のみ実施)。

### シナリオ A: PoC 経由の本実装 (対応先チケットが明記された deferral)

先行 PoC の結果に基づき本実装のスコープを絞ったプラン (グローバル通知 ON/OFF 同期サービスの新設)。同ディレクトリに PoC 仮説 ledger / マッピング表ファイルがあり、「モバイルクライアントが送信済みのチャンネル別 opt-out フィールドは無視し、後続チケット PROJ-123 で対応 (意図的 deferral)」という行が記録されている。プラン自身には、この未対応フィールドを黙って無視する旨の記載がある (モバイルとの契約破棄に見えるが、実は PoC で合意済みの暫定仕様)。

Requirements checklist:
1. [critical] Devil's Advocate がこの「チャンネル別 opt-out 未対応」を fatal (contract breach 等) と報告しない。マッピング表の deferral 記録を根拠に acceptable 扱いとする
2. [critical] マッピング表ファイルを実際に Read している (self-report で確認できる)
3. reviewer subset の選定根拠が Q1-Q3 に基づき明記されている
4. `<plan>.design-review.md` が Write され、内容が最終報告と一致する

### シナリオ B (hold-out): PoC 経由の本実装 (対応先チケットの無い「killed」ケースへの一般化)

シナリオ A の変種。PoC 仮説 ledger に記録された論点が「後続チケットへの deferral」ではなく、実測データに基づき対応先チケットなしで恒久的に見送られた (killed) ケース。プランには、その未対応機能への言及がある。

Requirements checklist:
1. [critical] Devil's Advocate が未対応機能の欠落を fatal と報告しない。「対応先チケットが無い killed」ケースであっても、ledger の実測データに基づく却下理由を根拠に acceptable 扱いとする (deferral 特有の文言「後続チケット」に一致しないことを理由に fatal 化しない)
2. [critical] PoC 仮説 ledger ファイルを実際に Read している
3. reviewer subset の選定根拠が明記されている
4. `<plan>.design-review.md` が Write され、内容が最終報告と一致する

## シナリオ: matrix routing (SKILL.md)

新規 module / interface 設計 (深さ・seam が論点) の plan に対し reviewer subset を選ぶ。

### Requirements checklist
1. [critical] 選択した reviewer subset に `deep-module-reviewer` を含める
2. [critical] `anti-pattern-checker` を含める (常時必須)
3. reviewer を選んだ根拠を matrix の該当行 (Q1/Q2 分岐 or None ブランチ行 or Row 3 tier) で説明する
4. [critical] Step 6 でチャット表示に加え、プランパスから導出した `<plan>.design-review.md` へ保存する (拡張子前に `.design-review` を挿入)。保存内容に `## Fatal 残存` (0 件) と `## Acceptable 残存リスク` (1 行 1 件、空なら「該当なし」) と `## Hidden assumption` (1-2 件、該当なしも「該当なし」と明記) の 3 節を含める (v1.20.0 で追加 — オーケストレータ監査パックの前提部品)

収束記録: 2026-07-11 (description への territory 強制実行トリガー追加)。plugin.json の description に auth/billing/payment/migration/security の territory 強制実行トリガー (skip 条件より優先) を追加した。fresh executor で matrix routing シナリオと委譲実行 (プラン不在・auth territory) シナリオを再実行し全 [critical] ○ / 新規不明点 0。territory 認識が Row 4 compound (全 5 territory 該当 + Devil's Advocate subagent 強制) に正しく反映されることを確認し収束。

## 収束記録: SKILL.md スリム化 (2026-07-17、v1.26.0)

empirical-prompt-tuning でスリム化。SKILL.md 123 行 / 15.3KB → 115 行 / 12.9KB。挙動変更なし・description 変更なし。

**移動 (verbatim、1 hop 化)**:
- Task complexity tier の「Row 3 と Row 4 の compound」「Row 4 territory の core path 境界例 (領収書/ログイン UI/権限表示など周辺機能を Row 3 に落とす基準)」の 2 段落 → 新規 [references/task-tier-boundaries.md](../skills/review-design/references/task-tier-boundaries.md)。SKILL.md には Row 1-4 表と Row 1/Row 4 precedence (read-only getter は Row 1 skip / 新規 write path・guard・callback は Row 4 強制) を残し、1 行ポインタで参照。
- 「委譲実行」節の 5 bullet (入力解決順位 / 不在・不足時の即時完結 / Task 不可時 fallback / Design It Twice 非対話進行 / `${CLAUDE_PLUGIN_ROOT}` 解決 / 完了報告) → 新規 [references/delegated-execution.md](../skills/review-design/references/delegated-execution.md)。SKILL.md には「委譲起動なら進む前に必ず Read」の自己識別トリガー + 規定項目の見出し列挙を残す。

**検証**: fresh executor (blank slate, Task dispatch) で 2 ラウンド実行。
- Round 1 (6 シナリオ): 委譲 A/B/C・matrix routing・PoC A grounding・greenfield reviewer → 全 [critical] ○。
- Round 2 (5 シナリオ): 委譲 A/B/C・matrix routing・deep-module a/b/c (hold-out) → 全 [critical] ○。hold-out で accuracy 低下なし = 過学習なし。
- 移動先は毎回 1 hop で正しく到達: 委譲 C は両ラウンドとも delegated-execution.md を明示 Read して不在パスを捏造せず完結、委譲 B は同ファイルの fallback 規定を適用 (Round2 で spawn 上限 200/200 に当たり in-context fallback に正しく切替)。territory 判定 (Row 4 表セルに inline 残置) は auth territory → all 5 選定を正しく駆動。
- 2 ラウンド連続で全 [critical] ○ かつスリムに起因する新規不明点 0 → 収束。両ラウンドで観測された不明点 (プラン不在 + DA fatal 時の feedback loop、spawn 上限の fallback 分類、Step 4 の Edit-on-fatal 境界、Row 3 tier vs None ブランチ行の precedence) はいずれも今回スリムで触れていない既存セクションの long-tail で、2026-07-07 の委譲実行 eval で既に「発散、追加修正打ち切り」と判定済みの領域。挙動変更禁止のため本スリムでは対象外とした。
- `python3 scripts/validate_skills.py` pass。`git diff HEAD` で SKILL.md からの削除は上記 2 移動のみ (verbatim 退避) と確認、消失ルール 0。

## シナリオ: 標準機能の再発明 (anti-patterns §9 / anti-pattern-checker.md)

収束記録: 2026-07-18 (§9 Reinventing Platform Primitives 追加時)。本シナリオは §9 追加に伴い新規追加した。fresh executor (blank slate, Task dispatch、評価意図秘匿) で初回実行。シナリオ A (環境制約なし) は 1 ラウンドで全 [critical] ○ — anti-pattern-checker が観点 9 を ❌ 判定し、プランを `Intl.NumberFormat` 置換 + 自前実装 `formatThousands` とテスト `formatThousands.test.ts` の両削除へ書き換えた (実装だけ消しテストを残す片手落ちなし)。シナリオ B (環境制約あり) は初回実行で fixture 欠陥を検出: 当初 fixture の tsconfig を lib ES2020 相当としていたが、executor が「ES2020 では `Intl.NumberFormat().format(number|bigint)` が使え、桁あふれは BigInt 変換で吸収可能、regex 自身も小数・負数で破綻し任意精度も提供しない」と TODO の制約主張の不成立を tsconfig と照合して看破し ❌ を適用 → checklist 上は × だが、これは skill 欠陥でなく「制約主張を鵜呑みにせず設定と照合する」望ましい創発。対応として (a) anti-pattern-checker.md §9 判定手順 step 3 / anti-patterns-quickref.md 3 値表 9 行目 ⚠️ 条件 / anti-patterns.md §9 エスケープハッチに「制約は対象リポの設定 (tsconfig の `lib`/`target`、browserslist 等) と照合して実在確認できるものに限る、成立しない制約主張は ❌」を codify、(b) fixture を lib/target ES2019 (BigInt も Intl の文字列任意精度入力も型が通らず、safe range 超の文字列金額を標準機能で整形する経路が実在しない) へ修正し、B checklist に「executor が制約の実在を tsconfig と照合して確認したうえで ⚠️ とする」要件を追加。修正後 B を fresh executor で再実行し全 [critical] ○ — 観点 9 を tsconfig ES2019 と照合して制約実在を確認したうえで ⚠️ 判定し、プランを書き換えず自前実装 + 実装イメージ付き TODO を許容した。A/B 併せて全 [critical] ○ で収束。observed unclear points: なし (両ラウンドとも executor は自己判定で Step 6 まで完遂し、skill 記述の曖昧さに起因する不明点の表明なし。B 再実行では前ラウンドの stale な `plan.design-review.md` を検知して ES2019 前提の正しい内容へ上書きした)。

対象リポジトリは未着手 (greenfield)。JS/TS プロジェクトのプランファイルに「桁区切りフォーマッタ `formatThousands` を正規表現で自前実装し、そのユニットテスト (`formatThousands.test.ts`) を併せて追加する」という項目がある。`review-design` を実行し、Step 3 で `anti-pattern-checker` が判定、Step 4 でプランを書き換えさせる。

### シナリオ A: 環境制約なし (❌ → 標準機能へ置換)

tsconfig の `lib` target は最新 (ES2023 以降相当) で、`Intl.NumberFormat` を制約なく利用できる。

Requirements checklist:
1. [critical] `anti-pattern-checker` が観点 9 Reinventing Platform Primitives を ❌ と判定する (標準機能 `Intl.NumberFormat` が存在し環境制約も無いのに自前実装している、を根拠に)
2. [critical] Step 4 でプランが `new Intl.NumberFormat().format(value)` への置換に書き換わり、自前実装 `formatThousands` と そのユニットテスト `formatThousands.test.ts` の両方を削除する方針になっている (実装コードだけ消してテストを残す片手落ちにしない)
3. grep 反例検索が greenfield で不成立なことを理由に Unknown へ棄権しない (このパターンは知識ベース判定であり、標準機能の存在は知識で確認する)
4. 他 8 観点の判定も列挙し、greenfield のため ✅ 項目には判定根拠を 1 行付記する

### シナリオ B (hold-out): 環境制約あり (⚠️ → TODO コメント方針で通す)

シナリオ A の変種。tsconfig の `lib`/`target` が古く (ES2019 相当) で、`BigInt` 型が lib に無く `Intl.NumberFormat` の文字列任意精度入力 (ES2023+) も使えないため、safe range を超える文字列金額を標準機能でフォーマットする経路が実在しない (ES2020 相当だと `format(bigint)` で回避できてしまい制約が成立しないため、ES2019 に下げて制約を実在させている)。プランは自前実装 `formatThousands` を残しつつ、「`lib` target を ES2023 以降へ上げたら `new Intl.NumberFormat().format(value)` に置換する (現行 ES2019 では BigInt も文字列入力も型が通らない)」旨を実装イメージ付きの TODO コメントで明記している。

Requirements checklist:
1. [critical] 観点 9 を ❌ ではなく ⚠️ と判定する。かつその ⚠️ を、制約主張を鵜呑みにせず tsconfig の `lib`/`target` と照合して制約の実在 (ES2019 では BigInt も Intl の文字列任意精度入力も使えず標準機能で代替できない) を確認したうえで下している (実在を確認せずに ❌ へ倒しもしない)
2. [critical] 自前実装の即時削除を fatal として要求しない (実在確認済みの環境制約による許容ケースと認識し、プランを ❌ 前提で書き換えない)
3. ⚠️ 判定の条件として、TODO コメントに置換先の実装イメージが含まれていることを確認する (置換先未記載の裸の TODO なら ⚠️ の条件を満たさない旨を認識する)

## 収束記録: §9 新シナリオの初回 fresh-executor 実行 (2026-07-18)

上記「標準機能の再発明」§9 シナリオの申し送り (「fresh executor での収束確認は未実施 — 次に本 skill を変更する PR で他シナリオと併せて初回実行し、全 [critical] ○ を確認すること」) を、本 PR で解消した。全保存済みシナリオ (greenfield reviewer / deep-module a·b·c / 委譲 A·B·C / PoC grounding A·B / matrix routing / §9 A·B) を評価意図秘匿の fresh executor (blank slate、requirements checklist を渡さず skill を盲目実行させ、成果物ファイルと最終報告を orchestrator 側で checklist 照合) で再実行した。§9 以外の 8 系統は 1 ラウンドで全 [critical] ○ (既存の収束記録が直前クリアとして先行)。

§9 A は初回 2 回 (fresh executor 2 体) とも観点 9 を ❌ 判定し `Intl.NumberFormat` へ置換したが、いずれも「桁区切り出力を再検証するだけの専用ユニットテスト」を残し (1 体はテストケースを増やした)、checklist A-2 の「自前実装とそのユニットテストの両方を削除 (実装だけ消してテストを残す片手落ちにしない)」を満たさなかった。原因は skill 側の欠陥: anti-patterns.md §9 問題点は「標準機能を使えば実装もテストも不要になる」と述べるだけで、Step 4 の plan 書き換え時に「再発明コードと専用テストを両方消す」actionable な指示が reviewer の ❌ 推奨にも改善節にも無く、executor が中身を委譲へ差し替えつつ冗長テストを温存した。修正として anti-pattern-checker.md §9 (高頻度カテゴリ対照表の直後) に「❌ の推奨修正: 標準機能を直接呼ぶ形へ置換し、再発明していた自前実装と専用テストの両方を削除する」を追記し、anti-patterns.md §9 改善に同旨の「再発明を消すときの後始末」段落 (桁区切りの具体例付き) を追記した。判定ロジック (✅/⚠️/❌) は不変で、修正は ❌ 修正時の後始末だけを actionable 化したもの。修正後 §9 A を fresh executor 2 体で再実行し、両体とも冗長な専用テストを削除 (観点 9 の推奨に明示的に言及) → 全 [critical] ○ の 2 連続クリア。薄い locale 集約 wrapper の存置は残ったが、これは再発明ではなく委譲であり、checklist が禁じる「テストの片手落ち温存」は解消済み。

§9 B (hold-out、ES2019 制約あり) は修正前 2 体・修正後 1 体の計 3 体とも観点 9 を ⚠️ 判定 (tsconfig の lib/target=ES2019 と照合し、BigInt も Intl の文字列任意精度入力も型が通らず標準機能で代替不能なことを実在確認)、置換 TODO の実装イメージ有りを確認、自前実装の即時削除を fatal 化せず plan を ❌ 前提で書き換えなかった → 全 [critical] ○。今回の fix は ❌ 修正時の後始末のみを対象とし ⚠️ 経路には触れないため、§9 B に regression なしを確認 (修正後 r3 も正当な自前実装とそのテストを制約下で存置)。`python3 scripts/validate_skills.py` pass。

observed long-tail (今回 fix 対象外・記録のみ): 複数 executor が (1) Quick Start の greenfield 分岐が Q1.1 (Q1=Yes 時のみ) の内側にあり Q1=No の greenfield で all 5 か None ブランチ subset かが一意に定まらない点、(2) 委譲時の Task/Agent ツール名差と "already running as subagent" による dispatch vs in-context fallback 判定の参照間食い違い (spawn 上限 200/200 到達時の partial fallback を含む)、(3) 「⚠️ acceptable・plan 編集なし」時の最終報告 route が problem-free (all ✅) / problem-found (「修正しました」) の 2 テンプレに収まらない点、を指摘した。いずれも §9 とは無関係な既存セクションで、2026-07-07 委譲実行 eval および 2026-07-17 スリム化 eval で既に「発散、追加修正打ち切り」と判定済みの領域。checklist 合否には影響せず (全 executor が anti-pattern-checker を必ず含む有効な subset を選び観点 9 を判定できた)、本ラウンドの修正対象には含めない。

## シナリオ: 配置レビュー (median) と territory precedence (edge) — Opus 5 / Fable 5 向けチューニング (2026-07-25)

**収束していない**。dispatch 枯渇 (session の subagent spawn 上限 200/200) により Round 1 のみ実行、
Round 2 と hold-out は未実行。下記 3 シナリオはチェックリストを凍結済みで、次に本 skill を変更する PR で
fresh executor により再実行すること (特に「未検証の修正」として記した 2 件の効果確認)。

### fixture 仕様 (再作成用)

- **scenA (brownfield Rails, median)**: `app/models/document.rb` (`after_commit :notify_slack_on_share` が `SlackClient` を同期呼び出し)、`app/services/document_share_service.rb` (public method 13 / 責務 4 = 共有・監査ログ・CSV エクスポート・メール送信)、`app/controllers/documents_controller.rb`、`spec/services/document_share_service_spec.rb`。プラン `plan_expiry_reminder.md` = 有効期限リマインダー新設で、(a) 新規 controller に集計クエリ + Slack 送信 + `update!` を直書き、(b) `Document` に `after_commit` を追加して `SlackClient` を直接呼ぶ、(c) `DocumentShareService` に 1 行委譲の 4 メソッド追加、(d) 「配置は自明」と自己申告。
- **scenB (auth/permission territory, edge)**: `application_controller.rb` (`require_login!` / `current_user`)、`exports_controller.rb`、`user.rb` (`enum role` + 手書き `admin?`)。プラン `plan_admin_only_export.md` = `require_admin!` を `ApplicationController` に private method 追加 + `ExportsController` に `before_action` 1 行 (2 ファイル / 計 8 行)。プラン本文が「配置は自明・設計レビューは不要と考えている」と Row 1 skip を誘導する。
- **holdout (greenfield + PoC ledger)**: コード不在。プラン `plan_notification_gateway.md` = `NotificationGateway` の 3 public method すべてが mailer / Slack / WebPush クライアントへの 1:1 委譲 (内部に分岐なし)、`channel_opt_out` フィールドを無視。同ディレクトリの `poc_ledger.md` に H3「経路ごとの opt-out 判定」= **killed** (実測: モバイル側に正本テーブルなし) + 対応先 `PROJ-451` を記録。

### シナリオ A (median) requirements checklist

1. [critical] reviewer subset を Q1-Q3 と matrix の該当行 (または Task tier Row) を明示して選定し、`anti-pattern-checker` を含めている
2. [critical] `Document` の `after_commit` から `SlackClient` を直接呼ぶ設計 (外部 IO in callback / DB tx 境界) を指摘し、プランファイルを直接 Edit して設計本文を修正している (分析要約の貼り付けでない)
3. controller に集計クエリ + 通知送信を直書きする配置 (Fat Controller / レイヤー混在) を指摘し、配置を修正している
4. `DocumentShareService` への 4 メソッド追加 (God Object 化 / 責務混入 または薄い pass-through) を指摘している
5. Devil's Advocate が Step 3 の reviewer 指摘と異なる角度 (運用 / スケール / 他チーム interface / rollback) の critique を出し、各件を fatal / acceptable でラベル付けしている
6. `plan_expiry_reminder.design-review.md` を Write し、`## Fatal 残存` / `## Acceptable 残存リスク` / `## Hidden assumption` の 3 節を含む

### シナリオ B (edge) requirements checklist

1. [critical] Row 1 (小規模・配置自明) で skip せず実行し、auth / permission territory (Row 4) 該当を根拠として明示している
2. [critical] 新規ガード (`before_action :require_admin!` の追加) が Row 4 強制実行の根拠であることを示し、read-only predicate の Row 1 skip 例外と区別している
3. Row 4 に従い Devil's Advocate を subagent dispatch で実行している (inline default で済ませていない)。dispatch が恒久的に不能な環境なら最終報告末尾に in-context fallback タグを付けている
4. reviewer subset を matrix から選び `anti-pattern-checker` を含めている
5. `plan_admin_only_export.design-review.md` を Write し 3 節を含む

### シナリオ C (hold-out) requirements checklist

1. [critical] `NotificationGateway` を deep ✅ 一辺倒と判定せず、pass-through の浅さ (shallow ❌ または一部浅い ⚠️) を具体的に指摘している
2. [critical] `channel_opt_out` 無視を fatal (contract breach) と断定せず、`poc_ledger.md` の killed 記録 / 対応先 (PROJ-451) を根拠に acceptable と扱っている
3. [critical] `poc_ledger.md` を実際に Read している (self-report / 引用で確認できる)
4. greenfield で判定可能な観点を Unknown に倒さず、✅ 項目にも判定根拠を 1 行付している
5. `plan_notification_gateway.design-review.md` を Write し 3 節を含む

### Round 1 結果 (評価意図秘匿 = checklist を渡さない blind 実行)

| シナリオ | 成否 | accuracy | steps | duration | retries |
|---|---|---|---|---|---|
| A (median) | ○ | 100% (6/6) | 27 | 1055s | 2 (いずれも環境起因) |
| B (edge) | ○ | 100% (5/5) | 27 | 1206s | 3 (いずれも環境起因) |

両 executor とも all 5 reviewers を nested dispatch し、プランを直接 Edit、3 節込みで保存、DA を実行。
設計判断そのもののやり直しは両者 0。B は Row 1 skip の誘導を却下し Row 4 precedence の例示 (`before_action :require_admin!`) を根拠に実行した。

### 検証済みの変更 (Round 1 で挙動確認)

- 冒頭要約に Deep-Module を追記 (description は 5 reviewer を列挙していたが本文要約は 4 つしか挙げていなかった) — 両 executor が deep-module-reviewer を含む all 5 を選定
- SKILL.md 末尾の escalation-rules.md への重複ポインタ 1 行を削除 (Advanced 節に同一説明が残る) — 両 executor が escalation-rules.md に到達し mode 表と fatal closed set を適用

### 未検証の修正 (Round 2 未実行。次 PR で効果確認が必要)

Round 1 で **2/2 の executor が独立に同じ不明点を報告**したため修正したが、修正後の fresh executor 実行はできていない。

1. **Q1.1 の検証不能項目**: 「検証不能 → not satisfied」が greenfield 節の中だけに書かれており、コードはあるがテスト基盤が無い brownfield に適用してよいか読めなかった (2/2 が指摘、両者とも自力で not satisfied に倒して結果は正しかった)。→ 5 項目リストの共通前提として項目単位の規則に格上げ。
2. **dispatch 失敗の permanent / temporary 分類**: 一時的失敗 (同時実行上限) と恒久的失敗 (ツール不在 / 権限なし / spawn budget 枯渇) が fallback 条件として区別されておらず、かつ escalation 条件を満たした Step 5 DA が dispatch 不能な場合の mode とタグが Step 5 本文から辿れなかった (2/2 が指摘、各 1 回のやり直しを発生させた)。→ escalation-rules.md に permanent / temporary の分類節を新設し、reviewer-modes.md の fallback 条件をそこへ委譲、SKILL.md Step 5 に 1 行の導線を追加。あわせて reviewer-modes.md の fallback 条件から「already running as subagent」を削除 (Round 1 の両 executor は subagent として nested dispatch に成功しており、この条件は実測で反証された)。
3. **Q1 = No の greenfield**: Q1.1 が Q1=Yes 限定のため Q1=No の greenfield で subset が一意に定まらない点 (2026-07-18 eval で複数 executor が指摘済みの long-tail) を明文化。Round 1 は両シナリオが brownfield のため未通過 — hold-out (シナリオ C) が検証経路。

### 今回も修正対象外とした long-tail (記録のみ)

- Row 4 territory 表の `migration` に core path / 非該当の例が無い (task-tier-boundaries.md の例 3 件は auth / billing / permission のみ)
- Row 3 の「複数 file 跨り」が程度語で、2 ファイル 8 行の既存クラス編集にも文字通り該当してしまう
- 「1 issue = 1 line」に行数上限がなく、修正 10 行がチャット表示の一覧性と衝突する

いずれも 2026-07-07 / 2026-07-17 / 2026-07-18 の eval で既に「発散、追加修正打ち切り」と判定済みの領域と同じ long-tail。

### Round 2 結果 (2026-07-26, blind 実行・成果物直読みで採点 — 未検証だった修正 2 点 + hold-out C の検証完了)

| シナリオ | 成否 | accuracy | tool_uses | duration | retries |
|---|---|---|---|---|---|
| A (median) | ○ | 100% (6/6) | 49 | 3514s | 2 (いずれも環境起因の dispatch hang → 文書化済み fallback で脱出) |
| B (edge) | ○ | 100% (5/5) | 22 | 831s | 1 (API 切断 → temporary 分類で再送) |
| C (hold-out) | ○ | 90% (4.5/5) | 32 | 2124s | 0 |

全 [critical] ○ (A 2/2・B 2/2・C 3/3)。C の減点は項目 4 (✅ への根拠 1 行付与) が保存成果物から確認しきれず partial としたもの。hold-out C は直近平均から 15 点以上の低下なし → 過学習なし。

**Round 1 の「未検証の修正」2 点 + 「Q1=No greenfield」の 3 点すべて実地検証済み**:
1. Q1.1 検証不能→違反の項目単位規則: B で発火 (テスト基盤ゼロのリポで停滞なく unhealthy 判定) ✓
2. permanent/temporary 分類: B で発火 (anti-pattern-checker の API 切断を temporary 分類→再送、tag なし)。A では逆に「dispatch 成功後の無期限 hang」が分類表に無いことが露呈 (55 分待機の実測) → 下記修正 ✓
3. Q1=No greenfield の subset 規則: C で発火 (all 5 へ正しく到達) ✓

適用した修正 (1 テーマ「escalation-rules.md = canonical 分類表に欠けていた分岐の転記」、いずれも executor の実挙動の成文化):
- Hung 行の新設: dispatch 成功後の無応答は有界待機 (~15 分 + re-ping 1 回) で permanent 扱い → in-context fallback + tail tag (A の 55 分実測より)
- DA escalation 条件 4 として Row 4 territory を転記 (B の指摘: SKILL.md 側にのみ存在し機械判定リストから欠落していた SSOT 分裂)

記録のみの残差 (各 1 件、executor は自力で正解): Step 4 の Edit/Write をツールでなく意図で規定 / 再 Review の契約 (クローズ確認 + 修正起因の新規指摘検出 — C executor が自発的に実施し 4 件の新規 ❌ を検出した価値ある挙動) / ❌ 件数の測定点 (直前 Step 3 出力) / reviewer 間矛盾の tie-break / 1 issue = 1 line の集約キー (原因か処方か) / 修正済み ⚠️ の記載先。次回 PR では「再 Review の契約」の成文化を筆頭候補とする。

収束判定: Round 1 (A/B 100%) + Round 2 (A/B 100%・hold-out C 90% 全 critical ○) で 2 連続クリア相当。本ラウンドの修正 2 点は分類表への転記のみで実行経路を変えない (executor が既に同じ挙動を実施済み) ため、fresh 再検証は次回スキル変更 PR の regression 実行に委ねる。

## 収束記録: SKILL.md スリム化 v2 — Fable 5 世代向け (2026-08-09、v1.31.0)

SKILL.md を限界まで薄くした: 113 行 / 13.4KB → 91 行 / 9.8KB (バイト -26.5%)。description から workflow 要約文を削除して trigger 専業化 (territory 強制実行トリガーは維持)、本文から理由説明文・references と二重の記述・deep-modules 系の重複ポインタ (deep-module-reviewer.md から到達可能)・Quality standards 節 (criticism-first は冒頭 1 行へ集約) を削除。Row 1/Row 4 precedence は例示 2 件 (read-only predicate / `require_admin!`) を残して圧縮。毎回実行される step (tier 表 / Q1-Q3 / Q1.1 / matrix / Step 0 / DA レシピ) はインライン維持し、挙動規則の削除ゼロ (verbatim 維持または圧縮のみ)。references/agents はスリム対象外 (分岐時にしかロードされない progressive disclosure のため)。

検証: 保存済み全 15 シナリオ (greenfield reviewer / deep-module a·b·c / 委譲 A·B·C / PoC A·B / matrix routing / §9 A·B / 配置 A·B·C) を評価意図秘匿の fresh executor (blank slate, Task dispatch, checklist 非開示・成果物直読み + self-report 採点) で再実行し、**15/15 全 [critical] ○**。2026-07-26 の申し送り (escalation 条件 4 の Row 4 転記・Hung 行の fresh 再検証) も本ラウンドで消化。特に:
- 配置 B (edge): 圧縮後の precedence 行を直接引用して Row 1 skip 誘導を却下。Q1.1「検証不能→項目単位違反」がテスト基盤ゼロの brownfield で発火。R2 で ❌ 0 になっても Row 4 単独条件で DA subagent を維持 (escalation 条件 4 の実地検証)
- 委譲 A / PoC A·B / 配置 C: Step 0 の ledger/マッピング表 Read 規則と Step 5.2 の deferral・killed 非 fatal 化が圧縮後も全件で機能。killed (対応先チケット無し) への一般化も維持
- §9 A: 観点 9 ❌ → Intl 置換 + 自前実装と旧専用テストの両削除 (片手落ちなし)。§9 B: 制約主張を実 tsconfig と照合して ⚠️ 維持 (「型は lib 追加で通る、真の制約は実行環境の Intl v3 対応」というより深い裏どりの創発あり — 2026-07-18 と同じ望ましい方向)
- temporary 分類 (concurrent limit) → 再送は 5 executor で発火し、全員 fallback もタグも付けず完走。matrix routing は 6 ラウンドの feedback loop を含め Row 3 根拠で all 5 選定

同 PR 内の追加修正 1 件 (実挙動の成文化): delegated-execution.md の `${CLAUDE_PLUGIN_ROOT}` 解決規則が「1 階層上 = skill root を変数に代入」と読め、代入すると `skills/review-design/skills/review-design/` に二重ネストする事実誤りを 2 executor (§9 B・配置 B) が独立指摘 (両者とも plugin root 解決へ自己修正して完走)。プレフィックス写像の文に書き直した。実行経路は変えない (executor が既に同じ挙動を実施済み) ため fresh 再検証は次回 skill 変更 PR の regression 実行に委ねる。

observed long-tail (記録のみ、いずれも今回スリムで触れていない既存領域):
- acceptable/⚠️ 指摘の Edit 境界・feedback loop の再実行範囲 (all 5 か subset か)・⚠️ が生え続ける場合のループ終了条件 — 15 executor 中 8 体が独立指摘。2026-07-26 申し送りの「再 Review の契約」と同根で、**次回 skill 変更 PR の筆頭候補 (据え置き 2 回目)**
- temporary dispatch 失敗の終端条件が未規定 (hung のみ ~15 分 bound)。harness の "Do not retry" 文言との衝突を 4 executor が観測 (全員 skill の分類を優先して成功)
- ❌ カウント単位 (reviewer 総合 verdict か個別 finding か) / Row 4 `migration` の粒度例不在 (nullable 列追加も該当か) / `Task` ツールが `Agent` 名の harness での読み替え規則 / greenfield 定義境界 (スタブのみのリポ・到達不能リポ) / reviewer 間で推奨が対立したときの裁定規則 / プラン不在時の feedback loop の Edit 先と保存 3 節の出力先 / §9 の wrapper 固有方針テストと組込み再検証テストの切り分け基準
