# regression eval (empirical-prompt-tuning 収束時保存)

収束記録: 2026-06-12 (v3.28.0 PR)。Iter1-3 で fresh executor が全 [critical] ○ / accuracy 100% / retries 0。
用途: **regression 検出器** (capability 改善の信号としては使わない)。本 skill を変更する PR では
fresh executor (blank slate, Task dispatch) で下記シナリオを再実行し、全 [critical] ○ を確認してから merge する。
実行方法は empirical-prompt-tuning の「Subagent invocation contract」に従う (成果物はインライン、ファイル編集禁止)。

## シナリオ: deep tier / billing リスク領域 / 注入エラー fallback

冒頭の自動取得節に `unknown revision 'origin/develop...HEAD'` エラーが見えている。$ARGUMENTS なし。変更 4 ファイル (plan.rb の plan_code 値追加 + billing_service.rb + spec 2 本)。手順を列挙させ、(a) diff リカバリ (b) tier と実行モード (c) business-impact-analyzer 起動 (d) auto-apply 判定軸を明答させる。

### Requirements checklist
1. [critical] フォールバック (b): default branch を特定して origin/<base>...HEAD に読み替えて再実行 (origin/develop のまま再実行しない)
2. [critical] billing リスク領域のため tier = deep (4 agent 並列) + business-impact-analyzer 必須
3. plan_code (domain model attribute) 更新のため business-impact の skip 条件に非該当
4. auto-apply は readability 軸のみ。リスク領域のため needs-judgment 側に倒す
5. 申し送り先 `$(git rev-parse --git-common-dir)/quality-review-handoff-$(git branch --show-current | tr '/' '-').md` → /polish-before-commit が受け取る contract を認識

---

以下は v1.19.0 (Orchestrated モード / quality ledger) 追加分。収束記録: 2026-07-05。fresh executor で Iter1-3 全 [critical] ○ / retries 0 (Iter1 で採番規則・語彙揺れ等の仕様ギャップを検出し修正後に再収束)。

## シナリオ: Orchestrated モードで quality ledger に記帳し収束判定する (Step 4)

Task 起動プロンプトに「orchestrated モードで実行。escalation は `plan.escalation-ledger.md` に記帳して続行せよ」の明示指示あり。Step 4 の振り分け結果: (1) readability のネスト深さ超過 1 件 (early return 化で解消、局所・意味保存) → auto-apply-safe で適用・検証 pass、(2) coupling の内容結合 (`instance_variable_set`) 1 件 → needs-judgment、(3) business-impact の認可 chain 該当 1 件 → needs-judgment。quality ledger への記帳内容と、収束判定を答えさせる。

### Requirements checklist
1. [critical] 3 件全てを quality ledger に記帳する (申し送りファイルのみで終わらせない)
2. [critical] (1) は深刻度 Major (readability 構造的問題閾値超過) / 状態 `適用済み`、(2)(3) は深刻度 Critical (内容結合 / 認可 chain は Critical 条件に該当) / 状態 `escalated` として記帳する
3. quality ledger の記帳行が `| 番号 | 出所 | 深刻度 | 状態 | 内容 |` の列構成に従う
4. 3 件とも Critical/Major が `適用済み` または `escalated` のため、収束判定は「収束」と答える

---

以下は「委譲実行 (subagent として起動された場合)」節 — nested Task 判定を own-tool-list 方式に変更、Step 1 既定スコープの 0-diff 境界条件、`${CLAUDE_PLUGIN_ROOT}` 解決 — 対応分。収束記録: 2026-07-07。baseline では「subagent = nested だから Task 不可」という文字列推測での誤判定を想定したが再現せず、代わりに Step 1 の「未コミット+staged が 0 件かつブランチ全体差分が非 0 件」という既定スコープの境界条件が未定義であることを検出し、SKILL.md Step 1 と「委譲実行」節に既定 (0 件ならブランチ全体) を明文化した。以降 fresh executor 2 ラウンド連続で当該テーマの新規不明点 0 件を確認し、hold-out シナリオ (Orchestrated モード宣言 + working tree clean + base branch 省略の組み合わせ) でも accuracy 低下なしで収束を維持した。

## シナリオ: 委譲実行時の nested Task 判定 + base branch 明示 (median)

Task で review-code-quality の実行を委譲されたエージェントとして起動される。入力に「対象リポジトリ (feature ブランチをチェックアウト済み)」と「base branch: main」が明示される。スコープ確定後の対象ファイルは 3 ファイル (deep tier 相当)。

### Requirements checklist
1. [critical] Task ツールの使用可否を、自分の利用可能ツール一覧に Task/Agent が存在するかで判定している (「委譲されて起動された = nested 実行だから使えない」という推測のみで判定していない)
2. [critical] Step 1 でスコープ確定後の対象ファイル数が 2 ファイル超 (deep tier) であり、かつ Task が利用可能な場合、実際に cohesion/coupling/readability/business-impact の 4 agent を並列起動している
3. base branch が明示指定されている場合、その値をそのまま `origin/<base>...HEAD` の比較に使い、`origin/develop` 既定へフォールバックしていない
4. 統合レポートに重大度別件数 (0 件のカテゴリも含む) と `/abs/path:line_number` 形式の指摘が含まれている
5. auto-apply-safe 条件を満たす readability 軸 finding は Edit 適用 → lint/test 検証まで実施され、それ以外 (cohesion/coupling/business-impact 全件・条件を満たさないもの) は申し送りに回されている
6. agent 起動プロンプト中の `${CLAUDE_PLUGIN_ROOT}` に相当する記述が生文字列のまま埋め込まれず、いま Read している SKILL.md の所在から導いた解決済み絶対パスになっている

## シナリオ: 委譲実行時の nested Task 判定 + base branch 省略・working tree clean (edge)

「〜見てもらえますか」のような自然文で依頼され、「委譲されたエージェント」等の定型句は無い。base branch の指定も無い。working tree は clean (未コミット+staged 0 件) で、レビュー対象は既にコミット済みの feature ブランチ全体になる。

### Requirements checklist
1. [critical] 定型句が無い自然な依頼文でも、Task/Agent ツールの利用可否を利用可能ツール一覧から判定しており、文面のトーンだけで「これは委譲実行だから Task 禁止」と即断していない
2. [critical] base branch が指定されていないため `origin/develop` に固定せず、`gh repo view --json defaultBranchRef` または `git remote show origin` の HEAD branch で実際のデフォルトブランチを解決してから diff を取得している (両方失敗する環境では Gotchas 記載のトポロジー fallback `git branch -a` + `git merge-base` を使う)
3. [critical] 未コミット+staged が 0 件のため、Step 1 の既定をブランチ全体差分にフォールバックしている (0 件のまま対象なしと判断して即終了していない)
4. Step 1 でスコープ確定後の対象ファイル数に応じた tier (lite/standard/deep) 判定が行われている
5. 統合レポートに severity 別件数と auto-apply の結果件数行 (自動適用/revert/申し送り) が含まれている
6. self-report の Trace または Discretionary fill-ins に、base branch 解決の経緯 (何を試し何が決め手になったか) が記録されている

収束記録: 2026-07-11 (description への PR レビューモードトリガー明記)。plugin.json の description に PR レビューモードのトリガー語と、business-impact 軸が Ruby/Rails 限定である旨を追記した。fresh executor で deep/billing 机上シナリオと委譲実行 median (4 agent 並列・base branch 明示) を再実行し全 [critical] ○。委譲 median 実行で「同一箇所に cohesion finding が併存する readability finding の分離評価可否」が未規定と判明したため、auto-apply.md に「併存時は needs-judgment に倒す」を明文化した (観測された安全側挙動の規定化)。

---

収束記録: 2026-07-17 (v1.28.0)。empirical-prompt-tuning でのスリム化 (SKILL.md 120 行 17181 byte → 115 行 16517 byte、-664 byte)。本文の重複を SSOT へ寄せる参照化のみで、ルールの削除・統合による希釈はしていない: (1) 委譲実行節の Task 使用可否から「深さ 5」重複説明を除き execution.md「Task 使用可否の自己判定」を SSOT と明記、(2) 対象 diff フォールバック (b) の base 特定コマンド重複を Step 1「base ブランチの確定」への参照に置換、(3) Quick start step 2 の分岐 3 行を 1 行 + execution.md 参照に集約、(4) Step 1 末尾の AskUserQuestion 確認可否重複を「委譲実行」節参照に、(5) Step 2 の Task 判定重複を own-tool-list 参照に、(6) Step 3 の「すべての結果を受信」前提 2 段落を 1 段落に統合。上記 4 シナリオ (deep/billing 注入 fallback・orchestrated ledger・委譲 median・委譲 edge/working tree clean) を fresh executor (blank slate, Task dispatch) で 2 ラウンド連続実行し、全 [critical] ○ / 全要件 ○ / retries 0 / tool_uses 2-4 (skew なし) を確認。2 連続で新規不明点 0 (観測された不明点は base 解決の terminal action・business-impact の deep 時 dispatch 判断・内容依存分岐で、いずれもスリム化した節と無関係かつ変更前から存在する既知の裁量点)。edge シナリオ (working tree clean + base 省略) でも accuracy 低下なし。description は変更なし (Iter 0 で本文カバレッジと整合を確認済み)。`python3 scripts/validate_skills.py` pass。
