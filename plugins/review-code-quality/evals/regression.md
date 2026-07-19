# regression eval (empirical-prompt-tuning 収束時保存)

用途: **regression 検出器** (capability 改善の信号としては使わない)。本 skill を変更する PR では
fresh executor (blank slate) で下記シナリオを再実行し、全 [critical] PASS を確認してから merge する。
実行方法は empirical-prompt-tuning の「Subagent invocation contract」に従う (成果物はインライン、
編集してよいのは fixture のみで skill 本文は触らない)。

**新契約の要点 (旧版 = readability/auto-apply 依存版との差分)**: readability-analyzer と auto-apply 機構を撤去。
分析軸は cohesion / coupling (常時) + business-impact (domain attribute 変更時のみ)。🔴/🟠 は**全件 needs-judgment
として申し送り**、本 skill はソースを変更しない。readability レベルの改善・correctness (計算誤り/ロジックバグ) は
組み込み `/code-review` の担当。

## fixture 共通の作り方

`git init` した空リポジトリに、シナリオ別の impl を配置し `git add` + コミット (base) してから、
レビュー対象の変更を**未コミット (working tree)** で加える。base branch は `main`。executor には
「未コミット+staged を対象に review-code-quality を実行」相当の入口を与える。Ruby 検証コマンド
(rubocop/rspec) は本契約では走らない (auto-apply 撤去のため) ので bundler/rails_helper は不要。

---

## S1 (median): cohesion/coupling 検出 + 全件申し送り

**fixture**: Rails 風 Ruby リポジトリ。`app/services/order_report_service.rb` (注文レポート生成 service) に
未コミット変更 66 行。仕込み欠陥:
- **feature envy** (cohesion): `LineItem#subtotal` に相当する計算を service 側で `line.quantity * line.unit_price` と再計算する (振る舞いを LineItem に寄せるべき)
- **train wreck / デメテル違反** (coupling): `order.customer.address.prefecture` を 3 箇所で参照
- **暗号命名 + マジックナンバー** (本 skill 対象外 = /code-review 領域): メソッド `calc_d(o, f)`、税率リテラル `* 0.08`
- `spec/services/order_report_service_spec.rb` は存在するが新ロジックの context 追加なし (spec 未更新)
- domain model attribute の変更なし (business-impact は skip 想定)

**ground truth**: 対象 2 ファイル以下 (impl 1 + 未更新 spec は非 count) → standard / main thread 順次。
business-impact は attribute 変更なしで skip 報告。coupling でデメテル違反 ≥1 件 (🟠)、cohesion で
feature envy ≥1 件。暗号命名・マジックナンバーは readability/correctness 領域なので本 skill では指摘せず
(触れる場合も「範囲外・/code-review 委譲」と明示)。🔴/🟠 は全件申し送り、ソース無変更。

### Requirements checklist (7)
1. [critical] cohesion と coupling の両観点を分析している (片方で終わっていない)
2. [critical] coupling で最低 1 件検出している (デメテル違反 `order.customer.address.prefecture`)
3. [critical] 申し送りファイルが規定パス `$(git rev-parse --path-format=absolute --git-common-dir)/quality-review-handoff-<branch>.md` に overwrite で書かれ、🔴/🟠 を finding 行フォーマットで含む
4. business-impact は domain attribute 変更なしで skip 報告し、統合レポートに skip を残す
5. tier 判定が standard (impl 1 + 未更新 spec は非 count) で main thread 順次
6. 暗号命名 `calc_d` / マジックナンバー `0.08` を本 skill の指摘に混ぜていない (readability/correctness は /code-review 委譲。言及する場合も「範囲外」と明示)
7. ソースファイルを Edit で変更していない (全件申し送り + ファイル無変更)

---

## S2 (business-impact edge): domain attribute 拡張 + 未更新 caller 特定

**fixture**: Rails 風 Ruby リポジトリ。`app/models/plan.rb` の `status` enum に `suspended` を追加し、
`active?` を `status.in?(%w[active suspended])` に意味拡張する未コミット変更。caller 3 箇所:
- `app/services/billing_service.rb`: `active?` gate を新 semantics に合わせて**更新済み**
- `app/jobs/renewal_job.rb`: `active?` を条件に `Invoice.create!` + `RenewalMailer.deliver` を起動するが**未更新** (suspended でも invoice 発行 + mail 送信されるようになる)
- `app/models/user.rb`: `plan.active?` を entitlement (機能有効化) に使うが**未更新** (suspended ユーザに機能が付く)

**ground truth**: business-impact-analyzer 起動 (`status` の semantics 変更 = domain attribute 変更)。
renewal_job = 新規 record 作成 (`Invoice.create!`) + 外部送信 (mailer) → Major (business-impact.md 判定表 (b))。
user.rb = entitlement/認可 gate → Critical 候補 (認可 chain)。未更新 caller ≥1 を特定し業務影響を言及。
全件申し送り (business-impact は常に needs-judgment)。

### Requirements checklist (6)
1. [critical] business-impact-analyzer を起動し (status semantics 変更を domain attribute 変更と認識)、特定 caller の業務影響 (suspended で invoice 発行/mail 送信、suspended ユーザへの機能付与) に言及している
2. [critical] 未更新 caller を最低 1 件特定している (renewal_job の `Invoice.create!`+mailer、または user.rb の entitlement)
3. [critical] business-impact の finding を全件申し送り扱いにしている (auto-apply せず・ソース無変更)
4. renewal_job を「新規 record 作成 + 外部送信」→ Major、user.rb を認可/entitlement chain → Critical 候補に判定 (business-impact.md 判定表準拠)
5. 意図表明 (diff/コメントの「suspended も active 扱い」) があっても格下げせず、申し送りに `意図表明あり・要 product 確認` を付す
6. 更新済みの billing_service を誤検出の対象にしない (未更新 caller と区別できている)

---

## S3 (review-only holdout): 過学習チェック

**fixture**: S1 と同一 fixture。ユーザー指示は「レビューのみで見て。ファイルは変更しないで」。

**ground truth**: S1 と同じ検出 (cohesion/coupling)。新契約では通常モードもファイル無変更のため、
review-only の差分は冒頭で「review-only」を明示する点のみ。全件申し送り。

### Requirements checklist (6)
1. [critical] ソースファイルを 1 つも変更していない (Edit 呼び出し 0)
2. [critical] cohesion と coupling の両観点を分析している
3. [critical] 🔴/🟠 を全件申し送り (申し送りファイル書き込み、または書き込み不可なら inline 転記)
4. 冒頭で「review-only」と明示している
5. coupling でデメテル違反 ≥1 件を検出している
6. 「auto-apply を無効化する」という旧仕様の誤った説明をしていない (新契約では通常モードもファイル無変更で、review-only の意味は「全件申し送り + ファイル無変更 + 冒頭明示」だけ)

---

## S4 (orchestrated): quality ledger 記帳の新契約版 — **未収束マーク**

> **注意: 本シナリオは旧 S2 (orchestrated / quality ledger、auto-apply あり) を新契約 (auto-apply なし・全件 escalated 記帳) へ書き換えたもの。fresh executor での収束記録はまだ無い (書き換えのみ)。regression として採用する前に 1 ラウンドの収束確認が必要。**

**fixture**: S2 と同 fixture に、Task 起動プロンプトで「orchestrated モードで実行。escalation は
`plan.escalation-ledger.md` に記帳して続行せよ」を明示指示する。

**ground truth (新契約)**: 本 skill はファイルを変更しないため quality ledger 記帳は全件 `escalated`。
billing_service は更新済みで指摘なし。renewal_job (Major, 新規 record+外部送信) → escalated。
user.rb (Critical, 認可/entitlement chain) → escalated。Critical/Major が全て escalated → 収束判定「収束」。

### Requirements checklist (5)
1. [critical] 全 finding を quality ledger に記帳し、状態は全て `escalated` (`適用済み` は本 skill から記帳しない)
2. [critical] renewal_job = Major / user.rb = Critical の深刻度で記帳している (business-impact.md 判定表準拠)
3. quality ledger の行が `| 番号 | 出所 | 深刻度 | 状態 | 内容 |` の列構成に従う
4. Critical/Major が全て escalated のため収束判定を「収束」と答える
5. 申し送りファイルへの書き込みも併せて実施している (ledger のみで終わらせない)

---

## 収束記録

**2026-07-19** (readability 軸切除 + 公式 `/code-review` 委譲、v1.29.0)。empirical-prompt-tuning ループを
以下の順で実施し、各ラウンド S1 (median) / S2 (edge) を fresh executor (blank slate) で走らせ
**全 [critical] PASS / accuracy 100% / retry 0**:

- **baseline** (切除前): S1/S2 100%
- **切除後 iter1**: S1/S2 100%、unclear 6 件 (territory override の billing/payment 認定境界・base 解決の三段 fallback・申し送り件数の数え方・Critical 判定表の細分・spec 基盤不在分岐・dispatch 軸の直交、いずれも裁量で正解を埋めたが判定表に未固定)
- **判定分岐 5 点固定後 iter2**: S1/S2 100%、unclear 2 件 (dispatch 軸の直交宣言・handoff パスの相対/絶対)
- **micro-fix 2 点** (dispatch 直交宣言 + handoff パス絶対化) 適用
- **holdout S3** (review-only、S1 同 fixture): 100%、過学習なし (fixture を流用しても review-only の要件を満たし、通常モードとの差分 = 冒頭明示のみ、を取り違えなかった)

旧版 (auto-apply あり) の unclear の 1 クラス「🔴/🟠 に auto-apply-safe が 0 件だったときの状態記帳・
サマリー行 (自動適用 N / revert M / 申し送り K) の解釈揺れ」は、auto-apply 機構の撤去により
**構造的に消滅**した (全件申し送り = 状態が `escalated` に一本化され、解釈の分岐が無くなった)。

S4 (orchestrated) は新契約へ書き換え済みだが fresh executor 収束記録はまだ無い (上記「未収束マーク」)。
`python3 scripts/validate_skills.py` pass。
