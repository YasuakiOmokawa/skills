# regression eval (empirical-prompt-tuning 収束時保存)

収束記録: 2026-06-12 (v3.28.0 PR)。Iter1-3 で fresh executor が全 [critical] ○ / accuracy 100% / retries 0。
用途: **regression 検出器** (capability 改善の信号としては使わない)。本 skill を変更する PR では
fresh executor (blank slate, Task dispatch) で下記シナリオを再実行し、全 [critical] ○ を確認してから merge する。
実行方法は empirical-prompt-tuning の「Subagent invocation contract」に従う (成果物はインライン、ファイル編集禁止)。

## シナリオ: standard tier + 注入非対応 + base=main

「現在の対象 (自動取得)」節が生コマンド文字列のまま。$ARGUMENTS なし。変更 2 ファイル (app/models/user.rb + spec)、規約 hit 1 (コメント原則)、delegate/def 撤去なし、base branch は main。申し送りファイルは存在せず、各 Step の検出結果は違反 0 件とする。実行 Step 列と各 Step の確定レポート文言 (バリアント表準拠) を出させる。

### Requirements checklist
1. [critical] Step 8 (最終レビュー) で `/code-review` を起動しない (disable-model-invocation により Skill ツール起動が失敗するため)。直前の `/code-review` 実行結果の会話内取り込み、無ければ main thread 直接レビュー (`(fallback)` 明示) で実行する。feature-dev preflight (旧 Step 0) は実行しない (v0.31.0 で撤去)
2. [critical] Step 1 (規約の収集) を tier 判定より前に実行する
3. base=main のためフォールバック (b) で BASE_BRANCH=main を特定して diff 取得
4. [critical] Step 9 の後、commit / /create-pr へ自動で進まない。判断項目 0 件なら質問せず「判断項目なし。コミット可能な状態」と完了報告して終了し、1 件以上なら一覧を提示して「コミットへ進めますか?」でユーザーの明示指示を待つ (v0.19.0 で 0 件時の質問を廃止)
5. Step 6 は条件不一致由来のスキップとして Step 固有バリアント文言 (`[dead mock: スキップ (撤去なし)]`) を使う
6. Manual Review Items 4 分類を auto-fix 前に認識している

---

以下は v0.20.0 (Orchestrated モード / escalation ledger) 追加分。収束記録: 2026-07-05。fresh executor で Iter1-3 全 [critical] ○ / retries 0 (Iter1 で採番規則・語彙揺れ等の仕様ギャップを検出し修正後に再収束)。

## シナリオ: Orchestrated モードで判断項目 2件があっても停止せず完了報告する (Step 9)

Task 起動プロンプトに「orchestrated モードで実行。escalation は `plan.escalation-ledger.md` に記帳して続行せよ」の明示指示あり。Step 9 集約結果: 申し送り 1 件 (`app/services/billing_service.rb:42` の認可チェック配置、review-code-quality 由来、Major) + Manual Review Items 1 件 (`spec/models/user_spec.rb:88` の dead mock 部分削除、polish 検出、Minor)。この状態での Step 9 の最終アクションを答えさせる。

### Requirements checklist
1. [critical] ユーザーの返答を待って停止しない。判断項目 2 件を escalation ledger にそれぞれ 1 行ずつ記帳する
2. [critical] 記帳後、完了報告して終了する (「コミットへ進めますか?」の質問形にしない)
3. escalation ledger の記帳行が `| 番号 | 出所 | 深刻度 | 内容 | 根拠 | 推奨アクション |` の列構成に従い、各項目の深刻度 (Major / Minor) を保持する
4. 申し送りファイル (`quality-review-handoff-<branch>.md`) を提示後にクリアする (ledger へ転記済みのため stale として残さない)

---

以下は empirical-prompt-tuning 第3ラウンド (GREEN1-5) 追加分。収束記録: 2026-07-07 (次回 minor bump 時に version 反映予定)。fresh executor で Iter2-4 (再評価3ラウンド) 全 [critical] ○ / accuracy 100%。hold-out シナリオで escalation ledger のデフォルトパス規則が一度未定義のため checklist 1 件 (critical) 失敗 (accuracy 83.3%) を検出 → 優先順位を3段に明記する修正後、同一シナリオを新規 fixture で再実行し 6/6 (100%) に回復したことを確認済み。

## シナリオ: Orchestrated モードで escalation ledger の具体パス指定が無い場合のデフォルト解決

Task 起動プロンプトに「orchestrated モードで実行。escalation は記帳して続行せよ」の指示のみで、具体パスも計画・仕様名 (「プラン名」) も明示されていない。加えて Step 8 (最終レビュー) でバグ 1 件・その他 (品質) 指摘複数件が見つかった状態で Step 9 に到達した場合の、(a) escalation ledger ファイルパスの決定方法、(b) Step 8 の報告文言、を答えさせる。

### Requirements checklist
1. [critical] 明示パスも「プラン名」も無い場合、`references/orchestrated-mode.md` の優先順位 (1: 明示 `<path>` → 2: 呼び出し側指示中の「プラン名」→ 3: `$(git rev-parse --git-common-dir)/escalation-ledger.md`) に従い、3番目の既定値へ迷わず (ユーザーに確認を返さず) フォールバックする
2. [critical] Step 8 の報告文言が `[最終レビュー: 指摘 N 件 (内訳: バグ X / 規約違反 Y / その他 Z)]` に厳密一致し、内訳の分類基準 (バグ=実行時に誤動作する欠陥、規約違反=Step1収集の明文規約との不一致、その他=それ以外の品質指摘) どおりに数値が割り振られている
3. Step 9 集約が Step 8 の残存指摘も対象に含め、深刻度をバグ→Major、規約違反・その他→Minor で機械的に決定している
4. escalation ledger 記帳後、ユーザーの返答を待たず完了報告して終了している

---

以下は v0.24.0 (Step 9 外部診断ツール残存指摘の集約 / Step 8 起動プロンプトの既知 finding 共有) 追加分。収束記録: 2026-07-07。Iter1-2 で fresh executor 全 [critical] ○ / accuracy 100%。hold-out シナリオ (Orchestrated モード × 外部診断ツール由来の深刻度判定) で1巡目に `references/orchestrated-mode.md` の深刻度決定規則が外部診断ツールの扱いを明記しておらず、executor が既存項目からの類推で深刻度を補う必要があった (checklist 1 件 [critical] 失敗)。同ファイルに「外部診断ツール由来で既存項目と統合されなかった単独項目は Minor 固定」を明記する修正後、同一シナリオを新規 fixture で再実行し 4/4 (100%) に回復したことを確認済み。

## シナリオ: Orchestrated モードで外部診断ツール由来の残存指摘の深刻度を判定する

Task 起動プロンプトに「orchestrated モードで実行。escalation は `record.escalation-ledger.md` に記帳して続行せよ」の明示指示あり。会話内で外部診断ツール (react-doctor 等) の指摘 3 件が共有済みで、2 件は既に修正、1 件 (`src/utils/date.ts:12` の日付フォーマット共通化要否) は構造判断が要り残存。申し送りファイル・Manual Review Items・Step 8 残存指摘はいずれも 0 件で、この外部診断ツール由来の 1 件が他項目と統合されず単独計上になる。この状態での Step 9 集約時のレポート文言と escalation ledger 記帳内容 (深刻度・根拠欄) を答えさせる。

### Requirements checklist
1. [critical] 外部診断ツール由来で他項目と統合されなかった単独項目の深刻度を Minor と判定し、その根拠を `references/orchestrated-mode.md` の明示規則 (「外部診断ツール由来で既存項目と統合されなかった単独項目は Minor 固定」) から直接引用できる (既存項目からの類推によるブリッジを要しない)
2. Step 9 のレポート文言が 3 バリアント表の該当行と厳密一致し `[ユーザー判断項目: 1 件 (申し送り 0 / polish 検出 0 / 外部診断ツール 1)]` の形式で出力される
3. 修正済みの 2 件は集約リスト・escalation ledger のいずれにも記帳されない
4. escalation ledger 記帳後、ユーザーの返答を待たず完了報告して終了する

収束記録: 2026-07-11 (description への review-only モードトリガー追加)。plugin.json の description に review-only モードのトリガー語を追加した。standard tier 机上シナリオを fresh executor で 2 回実行し、1 回目は「バリアント表を持たない Step の報告体裁」が不明点として出たため、Quick start 3 に適用範囲 (Step 0/4/5/6/7/8/9 のみ対象、表の無い Step は要約 1 行) を明記する修正を行った。2 回目は全 [critical] ○ / 新規不明点 0 で収束。

収束記録: 2026-07-17 (v0.31.0 Step 8 を組み込み `/code-review` の effort xhigh に切替、feature-dev preflight (旧 Step 0) を撤去)。保存済み 4 シナリオを fresh executor (blank slate, 並列 4 dispatch) で再実行し、全 [critical] ○ / 新規不明点 0。シナリオ 1 の checklist 項目 1 は本切替に合わせて `/code-review` xhigh 実行 + preflight 非実行の検証に差し替えた。

---

収束記録: 2026-07-17 (v0.32.0 empirical-prompt-tuning 8 iterations で計 11 修正)。fresh executor 累計 21 dispatch (Iter 1-9、各回 3 並列)、全ラウンドで accuracy 100% を維持。累計修正は次のとおり: (1) Step 6 label SoT 一元化 + skip 文言優先順、(2) Step 4 Priority 2 fallthrough、(3) review-only overlay を条件由来 skip より優先、(4) Step 9 の polish 検出 Y 集計基準を dedup 後件数と明記、(5) dead-mock-removal.md に検出成功 3 バリアント追加、(6) Step 9 統合項目は上位深刻度側にのみカウント、(7) orchestrated 記帳の重複防止 (Step 6 既記帳分は Step 9 で再記帳しない)、(8) tier 表 deep 条件を OR 明示、(9) standard 行末尾但し書きの実行 Step 列扱い明示、(10) Step 8 args 追記の「完了済み」signal を handoff ファイル存在で判定と明示、(11) Step 3 並列化判定を 3 分岐化 (files>5 単一言語は main thread 順次) + Step 7 hit 判定の tier 独立性明示 + Step 4「違反なし」の 2 経路統合脚注。

追加シナリオ (regression suite に登録推奨):

## シナリオ: deep tier + orchestrated モード + 3 出所の同一箇所 dedup + dead mock 部分削除 (Iter 9 δ)

Task 起動プロンプト明示指示「orchestrated モードで実行。escalation は `plan-teardown.escalation-ledger.md` に記帳して続行せよ」。deep tier (6 files + delegate 撤去) の Ruby PR で、`app/services/legacy_billing.rb:88` に対して「申し送り Major + Manual Review Minor + Step 8 規約違反 Minor」の 3 出所が重なる複雑ケース。Manual Review #4 (dead mock 部分削除) を Step 6 実行時に ledger に事前記帳し、Step 9 集約時は再記帳せず bracket 集計 (X=1/Y=2/N=3) にのみ含める挙動を検証する。

### Requirements checklist
1. [critical] tier=deep (OR 規則) + 全 Step 実行
2. [critical] Step 3 が「files >5 かつ単一言語」で main thread 順次処理を選択 (3 分岐の中央条件)
3. [critical] Step 6 `[dead mock: Manual Review 1 件 (保留)]` + Step 6 時点で ledger 1 行記帳
4. [critical] `legacy_billing.rb:88` を 3 出所 dedup し上位 Major で申し送り側に 1 カウント、Y には計上しない
5. [critical] bracket 文言 `[ユーザー判断項目: 3 件 (申し送り 1 / polish 検出 2)]` に厳密一致
6. [critical] Step 9 の ledger 記帳で Step 6 既記帳 Manual Review #4 は再記帳しない
7. [critical] orchestrated モードでユーザー返答を待たず完了報告
8. Step 8 `[最終レビュー: 指摘 3 件 (内訳: バグ 1 / 規約違反 1 / その他 1)]`

## シナリオ: lite/standard 境界 + Manual Review #5 (Reference-free dead file) (Iter 9 θ)

新規追加 only ファイル (`src/spike_analytics.ts` +25/-0) で、Step 8 の dead file 指摘と Manual Review #5 が同一箇所 (`spike*` prefix + 外部参照 0) を指す standard tier ケース。Step 4 の「違反なし」を 2 経路 (違反 0 経路 / 判定不能経路) いずれでも同一文言で出す統合脚注、Step 7 の hit 判定が tier 表の hit 数と独立 (`typescript-coding.md` にコメント節なしなら hit 1 でも Step 7 skip) の 2 点を検証する。

### Requirements checklist
1. [critical] tier=standard (lite の hit=0 AND を満たさない)
2. [critical] Manual Review #5 を自動削除せず Step 9 集約に登録
3. [critical] Step 8 dead file 指摘を優先、独自 grep は 3 prefix 限定
4. [critical] bracket 文言 `[ユーザー判断項目: 1 件 (申し送り 0 / polish 検出 1)]` に厳密一致 (Step 8 + Manual Review #5 dedup)
5. [critical] Step 4 は新規追加 only でも `[パターン一貫性: 違反なし]` (2 経路統合脚注に依拠)
6. [critical] Step 7 は tier hit 1 でも `typescript-coding.md` にコメント節なしのため skip
7. [critical] 通常モード + 判断項目 1 件 → 「polish 完了。コミットへ進めますか?」で停止

収束記録: 2026-07-17 (v0.33.0 progressive disclosure 分割)。review-only / 他者 PR 点検 / 委譲実行の 3 低頻度モードを references/execution-modes.md へ verbatim 退避 (挙動変更なし)。全 6 シナリオを fresh executor で再実行し全 [critical] ○。保存シナリオに無い review-only 経路も ad-hoc executor 1 本で検証し、execution-modes.md への 1 hop 到達とブラケット文言・overlay 優先規則の適用を確認。既知の記述ギャップ (自ブランチ review-only の終了文言が「コミットへ進めますか?」のままになる点) は分割前からの記述で未修正 — review-only 専用シナリオの suite 追加も含め別 PR で検討。

収束記録: 2026-07-18 (Step 7 hit 母集団から comment-writing メタ規約を明示除外)。保存 6 シナリオを実フィクスチャ (git リポジトリ) 付きで fresh executor に blank slate で再実行 (Round 1: 6 並列)、全 [critical] ○ / accuracy 100%。Round 1 で 1 件の記述ギャップを検出: Step 7 の実行判定「収集規約にコメント keyword 節が含まれるか」が、Step 1 で必ず収集されるグローバル `~/.claude/rules/code-comments.md` (コメント原則節を持つ comment-writing メタ規約) を hit 母集団に含めてしまい、diff 対象言語の coding 規約 (`typescript-coding.md` 等) にコメント節が無くても Step 7 を発火させうる — fresh executor が literal reading を採ると「シナリオ: lite/standard 境界」checklist 6 (Step 7 skip) を落とす latent contradiction。既存 fix (Step 7 の hit 判定を tier hit 数から独立させた v0.32.0) は「どの規約を母集団に数えるか」を規定しておらず防げなかった。修正: SKILL.md Step 7 に「comment-writing メタ規約 (`/express-intent-in-code` が所有・例 `code-comments.md`) は hit 母集団に数えない。判定は diff に適用される coding convention のコメント原則節の有無で行い、repo `CLAUDE.md` の『コメント原則』節はこれに該当し発火させる」を 1 文追記 (先行パス所有領域を Step 7 対象外とする既存規則の自然な延長)。影響 3 経路を新規 executor で再実行 — s1 (repo CLAUDE.md コメント原則→RUN 維持)、s6 (typescript-coding.md コメント節なし + code-comments.md 除外→SKIP、新規不明点 0)、s5 (deep Ruby、ruby-coding.md コメント節なし→SKIP) いずれも全 [critical] ○ / accuracy 100%、Step 7 文言変化は非 critical で他 Step (tier/dedup/bracket/orchestrated 記帳) に無影響。inline 規則化済みのため Gotchas への重複転記はしない。残存の scaffolding 由来観測 (skill 欠陥ではない): (a) s5 の 3 出所統合項目を Step 9 ledger に「Major 側新規行として追記するか既記帳扱いにするか」はシナリオが spec 内 dead-mock を impl 側 :88 と同一箇所に抽象化した副作用で、両解釈とも全 [critical] を満たす (行数 ≠ bracket カウントの分離規定は既存)。(b) s1/s5 fixture に Gemfile/.rubocop.yml が無く `[lint: ツール未導入…]` が出る点は fixture 忠実度の問題。version bump (plugin.json / marketplace.json) は本 run のスコープ外 — 別途反映する。

改定記録: 2026-07-23 (v0.35.0 Step 8 を `/code-review` 起動から事前実行結果の取り込みへ変更 — disable-model-invocation により Skill 起動不可のため)。シナリオ 1 の checklist 項目 1 を差し替え済み。保存済み 6 シナリオを fresh executor (blank slate, 並列 6 dispatch) で再実行し、全 [critical] ○ / accuracy 100%。s5/s6 が事前実行結果の取り込み経路、s1 が事前実行なし fallback 経路 (`[最終レビュー: 指摘なし (fallback)]`) を検証。新規 unclear はいずれも既知の fixture/記帳粒度ギャップ (2026-07-18 記録の (a) と同類) で本変更由来の退行なし。
