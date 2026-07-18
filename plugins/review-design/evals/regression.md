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

## シナリオ: 委譲実行 (subagent として起動された場合)

収束記録: 2026-07-07。baseline (Iter1) で委譲実行時の入力解決順位不明・Step3再実行時のstep番号ズレ・プラン不在時のStep4/6分岐未規定・`${CLAUDE_PLUGIN_ROOT}`解決規則不在を観測し、SKILL.md に `## 委譲実行` 節を新設して解消。Iter2・Iter3・hold-out (計5 fresh executor) で checklist 全 [critical] ○ / accuracy 100% を維持。tool_uses/duration はラウンドにより ±10%/±15% を外れる回があったが (Scenario B の duration が Iter3 で +27%)、機能面 (checklist 合否) には影響なし。3 イテレーション連続で新規不明点 0 には至らず (テーマは毎回異なる軽微なドキュメント精度指摘のロングテール) 発散と判定し、追加の構造修正は打ち切った。詳細は本 skill の Gotchas を参照。

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
