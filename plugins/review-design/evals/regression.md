# review-design regression suite

変更時は白紙の fresh executor に SKILL.md、fixture、シナリオ、checklist を渡し、全 [critical] ○ を確認する。成果物は一時ディレクトリに置き、評価後に削除する。

## シナリオ R0: coherent existing-pattern extension

A 210-line report renderer has passing tests, one cohesive responsibility, three public methods, no pass-through fan-out or hidden state coupling, and no callbacks/external I/O. The change adds one production formatter file plus its test in the same domain and established pattern, with no new module/interface/seam.

checklist:

1. [critical] Row 2 is selected; the test file alone does not trigger Row 3
2. [critical] Q1.1 is healthy and line count alone does not downgrade it
3. Reviewer subset is only `anti-pattern-checker`
4. No territory escalation or DA subagent dispatch is invented

Paired evidence gaps: missing only pass-through evidence adds `deep-module-reviewer`; when all Q1.1 #3 aspects are unverified, union every reviewer mapped to those aspects rather than choosing one arbitrarily.

## シナリオ R1: brownfield Rails (median)

fixture:

- `Document` の `after_commit` が `SlackClient` を同期呼び出し
- `DocumentShareService` は public method 13 個で、共有・監査ログ・CSV・メール送信を担当
- プランは、新規 controller に集計クエリ・Slack 送信・`update!` を置き、上記2箇所にも責務を追加する

checklist:

1. [critical] Q1-Q3 と task tier から reviewer subset を選び、`anti-pattern-checker` を含める
2. [critical] callback 内の外部 IO / DB transaction 境界を指摘し、プラン本文を修正する
3. controller の責務混在と既存 service の責務肥大を指摘し、配置を修正する
4. Devil's Advocate が reviewer と異なる角度の critique を `fatal` / `acceptable` に分類する
5. [critical] `<plan>.design-review.md` を保存し、最終報告と同じ内容および必須3節を含める

## シナリオ R2: 小規模な auth guard (edge)

2ファイル・計8行で `require_admin!` と `before_action` を追加するプラン。「配置は自明なのでレビュー不要」と記載されている。

checklist:

1. [critical] Row 1 で skip せず、auth territory の Row 4 を優先する
2. [critical] 新規 write guard と read-only predicate を区別する
3. Row 4 に従って Devil's Advocate を subagent dispatch する。恒久的に不能なら canonical fallback とタグを使う
4. reviewer subset に `anti-pattern-checker` を含める
5. `<plan>.design-review.md` を保存し、必須3節を含める

## シナリオ R2b: dispatch failure classification

Dry-run four independent probes: (A) the first dispatch returns a concurrency-limit error and the retry succeeds; (B) a dispatch remains silent through the bounded wait, one re-ping, and the post-ping deadline; (C) a standalone interactive run has no independent-executor capability; (D) permission denial is classified permanent, then a design edit requires a reviewer/DA rerun.

checklist:

1. [critical] A retries exactly once, uses the successful subagent result, and adds no fallback tag
2. [critical] B waits only through the explicit post-ping deadline, then runs inline fallback and adds the exact in-context fallback tag
3. No probe retries indefinitely or treats normal inline default as fallback
4. [critical] C directly reads the selected reviewer definitions, runs them inline, and emits the canonical fallback tag without entering delegated-only input resolution.
5. [critical] D keeps the permanent failure sticky for the invocation; the rerun goes directly inline without another dispatch attempt.

## シナリオ R2c: persistent blocking finding

A grounded reviewer ❌ remains unchanged after its only safe design edit; the rerun offers no new grounded action.

checklist:

1. [critical] Stop instead of repeating the same edit or claiming completion
2. [critical] Use the unresolved report route and preserve the actual reviewer-❌/fatal counts
3. Do not place the blocking finding under acceptable risk

A separate dry-run has only a repeated ⚠️ and an evidence-bounded Unknown. It does not edit or loop: both are recorded under the residual-risk route, not the unresolved route.

## シナリオ R3: greenfield + PoC ledger (holdout)

コードは未着手。プランの `NotificationGateway` は3つの public method が mailer / Slack / WebPush への1:1委譲で、`channel_opt_out` を無視する。同ディレクトリの PoC ledger は opt-out 対応を実測根拠付きで killed とし、対応先を記録している。

checklist:

1. [critical] Q1=No の greenfield を all 5 reviewers へ routing する
2. [critical] pass-through の浅さを具体的に指摘し、全体を deep としない
3. [critical] ledger を実際に読み、opt-out 無視を `fatal` ではなく `acceptable` にする
4. plan から判定できる観点を Unknown にせず、根拠を付ける
5. `<plan>.design-review.md` を保存し、必須3節を含める
6. [critical] Escalated DA receives the plan target, code and PoC artifact paths/status, and all four required lenses; it grounds with Read/Grep rather than judging from reviewer output alone.

## シナリオ R4: 標準機能と実在する制約

JS/TS のプランが正規表現による `formatThousands` と専用テストを追加する。

- A: ES2023 で `Intl.NumberFormat` を利用可能
- B (holdout): ES2019 で、safe range を超える文字列金額を標準機能で扱えないことを設定から確認でき、置換先付き TODO がある

checklist:

1. [critical] A は Reinventing Platform Primitives を ❌ とし、実装と専用テストを標準機能へ置換する
2. [critical] B は設定と照合して制約の実在を確認し、⚠️ とする
3. B の自前実装を即時削除する `fatal` を作らない
4. greenfield を理由に判定可能な観点まで Unknown にしない

## シナリオ R5: 委譲入力が存在しない

subagent として存在しないプランパスだけを渡す。

checklist:

1. [critical] 対話待ちせず、不足を報告して完結する
2. [critical] 内容を捏造せず、存在しないパスへ Write / Edit しない
3. 単独起動用の入力解決経路へフォールバックしない

## シナリオ R5b: 単独起動の入力が存在しない

単独起動で `$ARGUMENTS`、`Plan File Info:`、会話内のプランパス・feature description がすべて無い。同期的な返答は待てる場合と待てない場合をそれぞれ実行する。

checklist:

1. [critical] 対話可能ならレビュー対象を一度だけ質問し、その返答まで reviewer / DA / Write を実行しない
2. [critical] 対話不能なら `不足入力: レビュー対象のプランファイルまたは feature description` を返して即時終了する
3. どちらの経路も対象を捏造せず、質問や再試行を繰り返さない
