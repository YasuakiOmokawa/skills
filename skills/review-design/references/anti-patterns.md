# アーキテクチャ・アンチパターン

## 概要

設計時に避けるべきパターンと、その改善方法。

## 1. Anemic Domain Model（貧血ドメインモデル）

### 症状

ドメインモデルがデータの入れ物に過ぎず、振る舞いがすべて Service に移動している。

```ruby
# ❌ Anemic: データだけのモデル
class Contract
  attr_accessor :status, :signed_at, :signer_id
end

class ContractService
  def sign(contract, signer)
    contract.status = :signed
    contract.signed_at = Time.current
    contract.signer_id = signer.id
    contract.save!
  end
end
```

### 問題点

- ビジネスルールが散在
- 不正な状態を防げない
- テストが複雑化

### 改善

```ruby
# ✅ Rich Domain Model: 振る舞いを持つ
class Contract
  def sign!(signer:)
    raise InvalidStatusError, '署名済みの契約は再署名できません' unless draft?

    self.status = :signed
    self.signed_at = Time.current
    self.signer = signer
    save!
  end

  private

  def draft?
    status == :draft
  end
end
```

## 2. Fat Controller

### 症状

Controller にビジネスロジックが集中している。

```ruby
# ❌ Fat Controller
class ContractsController < ApplicationController
  def create
    contract = Contract.new(contract_params)

    # ビジネスロジックが Controller に
    if current_user.team.contract_limit_reached?
      return render json: { error: '契約数上限' }, status: :forbidden
    end

    contract.creator = current_user
    contract.team = current_user.team

    if contract.save
      # 通知ロジックも Controller に
      contract.team.members.each do |member|
        ContractMailer.created(member, contract).deliver_later
      end
      render json: contract
    else
      render json: contract.errors, status: :unprocessable_entity
    end
  end
end
```

### 改善

```ruby
# ✅ Thin Controller
class ContractsController < ApplicationController
  def create
    result = CreateContractService.call(
      params: contract_params,
      user: current_user
    )

    if result.success?
      render json: result.contract
    else
      render json: { errors: result.errors }, status: result.status
    end
  end
end
```

## 3. God Object / God Class

### 症状

1つのクラスがあまりにも多くの責務を持っている。

```ruby
# ❌ God Class: 何でもやる
class ContractManager
  def create_contract(...); end
  def sign_contract(...); end
  def send_notification(...); end
  def generate_pdf(...); end
  def calculate_fee(...); end
  def sync_to_external_system(...); end
  def export_to_csv(...); end
  # ... 数百行のメソッド
end
```

### 改善

責務ごとにクラスを分割。

```ruby
# ✅ 責務分割
class ContractCreator; end
class ContractSigner; end
class ContractNotifier; end
class ContractPdfGenerator; end
class ContractFeeCalculator; end
```

## 4. Leaky Abstraction（抽象化の漏れ）

### 症状

Repository や Service の抽象化が不完全で、内部実装が漏れている。

```ruby
# ❌ 抽象化の漏れ: ActiveRecord の詳細が漏れている
class ContractRepository
  def find_active_contracts
    Contract.where(status: :active)  # ActiveRecord::Relation を返す
  end
end

# 呼び出し側が ActiveRecord に依存
contracts = repository.find_active_contracts
contracts.where(created_at: 1.week.ago..).order(:created_at)  # 追加クエリ
```

### 改善

```ruby
# ✅ 完全な抽象化
class ContractRepository
  def find_active_contracts(since: nil, order: :created_at)
    scope = Contract.where(status: :active)
    scope = scope.where(created_at: since..) if since
    scope.order(order).to_a  # Array を返す
  end
end
```

## 5. Circular Dependency（循環依存）

### 症状

モジュール/クラス間で相互に依存している。

```
┌─────────┐     ┌─────────┐
│ Order   │────►│ Payment │
└─────────┘     └────┬────┘
     ▲               │
     └───────────────┘
        循環依存!
```

### 改善

依存の方向を統一するか、インターフェースで分離。

```
┌─────────┐     ┌─────────────┐     ┌─────────┐
│ Order   │────►│ PaymentPort │◄────│ Payment │
└─────────┘     └─────────────┘     └─────────┘
                  (interface)
```

## 6. Shotgun Surgery

### 症状

1つの変更が多くのファイルに波及する。

```
「契約ステータスに新しい値を追加」
  → Contract.rb を変更
  → ContractService.rb を変更
  → ContractController.rb を変更
  → contract_helper.rb を変更
  → contract.js を変更
  → contract_status.yml を変更
  ... (10ファイル以上)
```

### 原因と改善

- **原因**: 関連するロジックが散在
- **改善**: 関連ロジックを1箇所に集約

```ruby
# ✅ ステータス関連を1箇所に
class ContractStatus
  STATUSES = %i[draft pending signed rejected].freeze

  def self.label(status)
    I18n.t("contract.status.#{status}")
  end

  def self.next_statuses(current)
    case current
    when :draft then [:pending, :rejected]
    when :pending then [:signed, :rejected]
    else []
    end
  end
end
```

## 7. Premature Abstraction（早すぎる抽象化）

### 症状

再利用されない抽象化、使われない拡張ポイント。

```ruby
# ❌ 早すぎる抽象化
class BaseNotificationStrategy
  def notify(user, message)
    raise NotImplementedError
  end
end

class EmailNotificationStrategy < BaseNotificationStrategy
  def notify(user, message)
    # 実際にはこれしか使わない
  end
end

class SlackNotificationStrategy < BaseNotificationStrategy
  def notify(user, message)
    # 「将来使うかも」で作ったが使われていない
  end
end
```

### 改善

**YAGNI** (You Aren't Gonna Need It) 原則に従う。

```ruby
# ✅ シンプルに
class ContractNotifier
  def notify(user, message)
    UserMailer.contract_notification(user, message).deliver_later
  end
end
# Slack 通知が本当に必要になったら抽象化する
```

## 8. Feature Envy

### 症状

メソッドが他のオブジェクトのデータに過度にアクセスしている。

```ruby
# ❌ Feature Envy: Contract のデータばかり使っている
class ContractPrinter
  def print_summary(contract)
    "#{contract.title} - #{contract.status} " \
    "(#{contract.signer.name}, #{contract.signed_at.strftime('%Y/%m/%d')})"
  end
end
```

### 改善

ロジックをデータを持つクラスに移動。

```ruby
# ✅ Contract に移動
class Contract
  def summary
    "#{title} - #{status} (#{signer.name}, #{signed_at.strftime('%Y/%m/%d')})"
  end
end
```

## チェックリスト

設計時に以下を確認:

| # | 観点 | 確認事項 |
|---|------|----------|
| 1 | Anemic Domain | モデルに振る舞いはあるか？ |
| 2 | Fat Controller | Controller は薄いか？ |
| 3 | God Object | 1クラスの責務は1つか？ |
| 4 | Leaky Abstraction | 内部実装が漏れていないか？ |
| 5 | Circular Dependency | 循環依存はないか？ |
| 6 | Shotgun Surgery | 変更が1箇所で済むか？ |
| 7 | Premature Abstraction | 本当に必要な抽象化か？ |
| 8 | Feature Envy | データを持つクラスにロジックがあるか？ |
