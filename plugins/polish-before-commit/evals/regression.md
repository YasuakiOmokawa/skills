# regression eval (empirical-prompt-tuning 収束時保存)

収束記録: 2026-06-12 (v3.28.0 PR)。Iter1-3 で fresh executor が全 [critical] ○ / accuracy 100% / retries 0。
用途: **regression 検出器** (capability 改善の信号としては使わない)。本 skill を変更する PR では
fresh executor (blank slate, Task dispatch) で下記シナリオを再実行し、全 [critical] ○ を確認してから merge する。
実行方法は empirical-prompt-tuning の「Subagent invocation contract」に従う (成果物はインライン、ファイル編集禁止)。

## シナリオ: standard tier + 注入非対応 + base=main

「現在の対象 (自動取得)」節が生コマンド文字列のまま。$ARGUMENTS なし。変更 2 ファイル (app/models/user.rb + spec)、規約 hit 1 (コメント原則)、delegate/def 撤去なし、feature-dev INSTALLED、base branch は main。申し送りファイルは存在せず、各 Step の検出結果は違反 0 件とする。実行 Step 列と各 Step の確定レポート文言 (バリアント表準拠) を出させる。

### Requirements checklist
1. [critical] Step 0 (preflight) を最初に実行し `[preflight: feature-dev 導入済み]` を出力
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
4. 申し送りファイル (`quality-review-handoff.md`) を提示後にクリアする (ledger へ転記済みのため stale として残さない)

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
