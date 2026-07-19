# Business Impact Analysis Reference

## なぜ「業務副作用」が独立観点として必要か

cohesion / coupling の 2 analyzer は **コード自体の品質** を評価する。一方、本 reference が対象とする「業務副作用 chain」は:

- attribute を read してさらに別の attribute を上書き永続化する **2 段階副作用** (例: `Plan#sync_freee_billing_status` 経由の機能フラグ復活)
- attribute 値を gate にする policy / before_action での **認可 bypass**

これらは spec が「変更ファイル直近」までしか保証しないため、spec green でも検出されない。コード品質 3 analyzer でも検出されない (caller 側の業務分岐は当該ファイルの責務ではないため)。

過去事例: 2026-05-20 PR#39551 で `base_license=nil` の意味多重化により失効ユーザの `plan_code='starter'` が維持され、`Plan#sync_freee_billing_status` が starter 機能フラグを毎回上書き永続化 → 有料機能フラグ復活の Critical バグを生んだ。この時、`/simplify` (3 agent) と `/review-code-quality` のコード品質 analyzer (cohesion / coupling) を通過していた (business-impact-analyzer 追加前)。

## 副作用 chain の典型パターン

### Pattern A: attribute → MasterPlan / Master* 系の find_by → 機能フラグ全上書き

```ruby
# 1 段階目: plan_code を read
freee_company.plan_code  # → 'starter'

# 2 段階目: MasterPlan を find_by して全 attributes 上書き
master_plan = MasterPlan.find_by(plan_code: freee_company.plan_code)
plan.assign_attributes(master_plan.attributes_for_sync_plan)
plan.save!
# → paper_upload, esign, chat_support, max_csv_export_count などが master の値で上書き
```

### Pattern B: attribute → policy gate

```ruby
# Pundit / before_action
before_action :require_not_subscribed_yet

def require_not_subscribed_yet
  raise BadRequestResponseError if @team.freee_company.unlicensed?
  # = plan_code.in?([nil, UNLICENSED]) を gate に使う
end
```

attribute 値の semantics が変わると、これまで gate されていたユーザが通過する/その逆が起きる。

### Pattern C: attribute → sync job / cron 起動条件

```ruby
# 定期 job の起動条件
if freee_company.unlicensed?
  return  # 失効ユーザはスキップ
end
ExternalApi.notify(...)
```

attribute 値変化で sync 漏れ / 過剰通知が発生。

## grep 戦略

domain model attribute を更新する change を見つけたら、以下の順序で caller を網羅:

1. **直接 attribute 名 grep**: `rg -n '\.plan_code\b' app/ lib/ -t ruby`
   - 注: `plan_code=` (代入) は呼び出し側でなく被呼び出し側。除外する場合は `-v '\bplan_code\s*='` を併用
2. **predicate method grep**: `rg -n '\.(unlicensed|starter|self_light|licensed)\?' app/`
   - attribute から派生した predicate (= attribute 値判定 method) の caller
3. **constants grep**: 関連定数 (`UNLICENSED` 等) の参照
4. **layer 別 filter**: 結果を以下の層に振り分けて報告
   - `app/controllers/` → controller flow
   - `app/policies/` → 認可 gate
   - `app/forms/` → form 上限
   - `app/jobs/` / `app/workers/` → 非同期処理
   - `app/services/` → ドメインロジック
   - `app/components/` / `app/views/` → UI 表示
   - `app/mailers/` → メール送信
   - `app/serializers/` → API レスポンス
   - `lib/` → cron / batch / rake

## 副作用 chain の judgment 観点

各 caller に対し以下を 1 つずつ確認:

| 観点 | 質問 | 危険サイン |
|---|---|---|
| 永続化 (a) 既存 state 上書き | この caller は他 attribute を update/save し**既存の persisted state を上書き**するか? | はい → Critical 候補 |
| 永続化 (b) 新規 record + 外部送信 | この caller は**新規 record を作成**し mail / 外部 API 送信を伴うか? | はい → Major 候補 (課金/決済ミューテーションを伴えば Critical) |
| 認可 | この caller は authorize / before_action / policy の gate に使うか? | はい → Critical 候補 |
| 外部送信 | この caller は API call / mail / notify を起動するか? | はい → Major 候補 |
| UI 制御 | この caller は button / link / form を有効化/無効化するか? | はい → Major 候補 |
| 分類軸 | この caller は CSV / PDF / 集計の分類軸に使うか? | はい → Minor 候補 |
| Read のみ | 上記いずれにも該当せず、表示用 read のみ | Good |

**意図表明での格下げ禁止**: diff やコメントに「意図的」の表明があっても重大度を下げない (意図表明は self-report であり cross-file 検証にならない)。申し送りに `意図表明あり・要 product 確認` を付す。

## 副作用 chain を避ける設計パターン

### Pattern A 対処: sentinel object / Null Object

attribute の `nil` / `false` / `[]` 等の「不在 sentinel」に **複数の semantics** (同期不可 vs 失効 vs 正常 0 件) を統合してしまうと、2 段階目の chain で意味が壊れる。Null Object pattern で型レベルで区別:

```ruby
class Freee::License::Base
  # ... 通常 license
end

class Freee::License::Base::Unsyncable < Freee::License::Base
  # 「同期不可」を表現する Null Object (失効=nil とは別型)
end

# caller 側で case 3 分岐
case license
when Unsyncable then # 維持
when nil        then plan_code = UNLICENSED  # 失効 → 倒す
else            plan_code = license.plan_code # 正常
end
```

### Pattern B 対処: gate 専用 method

attribute 値の `in?` 判定を view / controller に散在させず、model に `licensed?` / `unlicensed?` のような専用 method として集約。attribute 値の semantics 変更時に gate 全体の挙動を 1 箇所で見直せる。

### Pattern C 対処: explicit allowlist

`unless attribute.in?(WHITELIST)` のようにスキップ条件を明示し、attribute に新値が追加されたとき手前で気付けるようにする。
