# Domain-Driven Design (DDD) 戦術パターン

## 概要

ビジネスの複雑さをコードで表現するための設計パターン集。

```
┌─────────────────────────────────────────────────────────────┐
│                      Bounded Context                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                   Aggregate                           │  │
│  │  ┌─────────────────┐  ┌─────────────────────────┐    │  │
│  │  │ Aggregate Root  │  │    Entity               │    │  │
│  │  │   (Entity)      │──│  (内部エンティティ)     │    │  │
│  │  └────────┬────────┘  └─────────────────────────┘    │  │
│  │           │                                           │  │
│  │  ┌────────┴────────┐  ┌─────────────────────────┐    │  │
│  │  │  Value Object   │  │    Value Object         │    │  │
│  │  │  (属性を表現)   │  │  (属性を表現)           │    │  │
│  │  └─────────────────┘  └─────────────────────────┘    │  │
│  └───────────────────────────────────────────────────────┘  │
│                           │                                 │
│                           ▼ 発行                            │
│                   ┌───────────────┐                         │
│                   │ Domain Event  │                         │
│                   └───────────────┘                         │
│                                                             │
│  ┌───────────────────┐  ┌─────────────────────────────┐    │
│  │  Domain Service   │  │       Repository            │    │
│  │ (複数Aggregateの  │  │ (Aggregateの永続化)         │    │
│  │  協調ロジック)    │  │                             │    │
│  └───────────────────┘  └─────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Entity vs Value Object

### 判断基準

| 観点 | Entity | Value Object |
|------|--------|--------------|
| **同一性** | ID で識別 | 属性の組み合わせで識別 |
| **ライフサイクル** | 変化しても同一 | 変化したら別物 |
| **可変性** | 状態変更可能 | イミュータブル |
| **例** | User, Contract, Order | Money, Address, DateRange |

### 判断フロー

```
Q: このオブジェクトを「同じもの」と判断する基準は？

A1: 一意のID（「ユーザーID: 123」）
    → Entity

A2: 属性の組み合わせ（「1000円」「東京都渋谷区...」）
    → Value Object
```

### Ruby での実装例

**Entity**:
```ruby
# app/models/contract.rb
class Contract
  attr_reader :id, :title, :status, :amount

  def initialize(id:, title:, status:, amount:)
    @id = id
    @title = title
    @status = status
    @amount = amount
  end

  # 同一性はIDで判断
  def ==(other)
    other.is_a?(Contract) && id == other.id
  end
  alias eql? ==

  def hash
    id.hash
  end

  # 状態を変更するメソッド
  def sign!
    raise InvalidStatusError unless status == :draft
    @status = :signed
  end
end
```

**Value Object**:
```ruby
# app/models/money.rb
class Money
  attr_reader :amount, :currency

  def initialize(amount:, currency: :jpy)
    raise ArgumentError, 'amount must be non-negative' if amount.negative?
    @amount = amount.freeze
    @currency = currency.freeze
    freeze  # イミュータブル
  end

  # 同一性は属性で判断
  def ==(other)
    other.is_a?(Money) &&
      amount == other.amount &&
      currency == other.currency
  end
  alias eql? ==

  def hash
    [amount, currency].hash
  end

  # 新しいインスタンスを返す（イミュータブル）
  def add(other)
    raise CurrencyMismatchError unless currency == other.currency
    Money.new(amount: amount + other.amount, currency: currency)
  end
end
```

### TypeScript での実装例

**Entity**:
```typescript
// front/domain/contract.ts
export class Contract {
  readonly id: string;
  private _status: ContractStatus;

  constructor(id: string, status: ContractStatus) {
    this.id = id;
    this._status = status;
  }

  get status(): ContractStatus {
    return this._status;
  }

  sign(): void {
    if (this._status !== 'draft') {
      throw new InvalidStatusError();
    }
    this._status = 'signed';
  }

  equals(other: Contract): boolean {
    return this.id === other.id;
  }
}
```

**Value Object**:
```typescript
// front/domain/money.ts
export class Money {
  private constructor(
    readonly amount: number,
    readonly currency: Currency,
  ) {
    Object.freeze(this);
  }

  static create(amount: number, currency: Currency = 'JPY'): Money {
    if (amount < 0) {
      throw new Error('amount must be non-negative');
    }
    return new Money(amount, currency);
  }

  add(other: Money): Money {
    if (this.currency !== other.currency) {
      throw new CurrencyMismatchError();
    }
    return Money.create(this.amount + other.amount, this.currency);
  }

  equals(other: Money): boolean {
    return this.amount === other.amount && this.currency === other.currency;
  }
}
```

## Aggregate

### 概念

- **Aggregate**: 整合性を保つ必要のある Entity/Value Object の集合
- **Aggregate Root**: 外部からアクセスする唯一の入り口

```
┌───────────────────── Order Aggregate ─────────────────────┐
│                                                           │
│    ┌─────────────────┐                                   │
│    │   Order (Root)  │◄──── 外部からはここだけアクセス   │
│    └────────┬────────┘                                   │
│             │                                             │
│    ┌────────┴────────┐                                   │
│    │   OrderItem     │ ← 外部から直接アクセス禁止        │
│    │   (Entity)      │                                   │
│    └────────┬────────┘                                   │
│             │                                             │
│    ┌────────┴────────┐                                   │
│    │   Money         │                                   │
│    │ (Value Object)  │                                   │
│    └─────────────────┘                                   │
└───────────────────────────────────────────────────────────┘
```

### 設計原則

1. **外部からは Aggregate Root のみ参照**
2. **Aggregate 内の整合性は Root が保証**
3. **トランザクション境界 = Aggregate 境界**
4. **Aggregate 間の参照は ID のみ**

### Ruby での実装例

```ruby
# app/models/order.rb (Aggregate Root)
class Order
  attr_reader :id, :items, :total

  def initialize(id:)
    @id = id
    @items = []
    @total = Money.new(amount: 0)
  end

  # Aggregate Root 経由でのみ Item を追加
  def add_item(product_id:, quantity:, unit_price:)
    item = OrderItem.new(
      product_id: product_id,
      quantity: quantity,
      unit_price: unit_price
    )
    @items << item
    recalculate_total
    item
  end

  def remove_item(product_id:)
    @items.reject! { |item| item.product_id == product_id }
    recalculate_total
  end

  private

  def recalculate_total
    @total = @items.reduce(Money.new(amount: 0)) do |sum, item|
      sum.add(item.subtotal)
    end
  end
end

# app/models/order_item.rb (内部 Entity)
class OrderItem
  attr_reader :product_id, :quantity, :unit_price

  def initialize(product_id:, quantity:, unit_price:)
    @product_id = product_id
    @quantity = quantity
    @unit_price = unit_price
  end

  def subtotal
    unit_price.multiply(quantity)
  end
end
```

## Domain Event

### 概念

ドメインで発生した重要な出来事を表現するオブジェクト。

### 使い所

| 場面 | 例 |
|------|-----|
| 状態変更の通知 | ContractSigned, OrderPlaced |
| Aggregate 間の協調 | PaymentCompleted → OrderShipped |
| 監査ログ | 変更履歴の記録 |

### Ruby での実装例

```ruby
# app/events/contract_signed_event.rb
class ContractSignedEvent
  attr_reader :contract_id, :signed_at, :signer_id

  def initialize(contract_id:, signed_at:, signer_id:)
    @contract_id = contract_id
    @signed_at = signed_at
    @signer_id = signer_id
    freeze
  end
end

# 発行側
class Contract
  def sign!(signer_id:)
    @status = :signed
    @signed_at = Time.current

    # イベント発行
    DomainEvents.publish(
      ContractSignedEvent.new(
        contract_id: id,
        signed_at: @signed_at,
        signer_id: signer_id
      )
    )
  end
end
```

## Rails ActiveRecord との共存

### アプローチ 1: ActiveRecord を Domain Model として使う（シンプル）

```ruby
# 単純なドメインでは ActiveRecord モデルがそのまま Entity
class Contract < ApplicationRecord
  # ビジネスロジックを ActiveRecord モデルに書く
  def sign!(signer:)
    raise InvalidStatusError unless draft?
    update!(status: :signed, signed_at: Time.current, signer: signer)
  end
end
```

**適用場面**: CRUD 中心、複雑なビジネスルールが少ない

### アプローチ 2: ActiveRecord を永続化層として分離（複雑なドメイン向け）

```ruby
# ドメインモデル（PORO）
class Contract
  attr_reader :id, :title, :status

  def sign!
    raise InvalidStatusError unless status == :draft
    @status = :signed
  end
end

# 永続化（ActiveRecord）
class ContractRecord < ApplicationRecord
  self.table_name = 'contracts'
end

# Repository
class ContractRepository
  def find(id)
    record = ContractRecord.find(id)
    Contract.new(
      id: record.id,
      title: record.title,
      status: record.status.to_sym
    )
  end

  def save(contract)
    ContractRecord.upsert({
      id: contract.id,
      title: contract.title,
      status: contract.status.to_s
    })
  end
end
```

**適用場面**: 複雑なビジネスルール、ドメインモデルの独立性が重要

### 判断基準

| 条件 | 推奨アプローチ |
|------|---------------|
| 単純な CRUD | アプローチ 1 |
| 複雑なビジネスルール | アプローチ 2 |
| 既存の大規模コードベース | アプローチ 1（漸進的に 2 へ移行） |
| 新規プロジェクト + 複雑なドメイン | アプローチ 2 |

## Domain Service

### 概念

複数の Entity/Aggregate にまたがるロジックを配置する場所。

### 使い所

| 条件 | 配置 |
|------|------|
| 単一 Entity の振る舞い | Entity に書く |
| 複数 Entity の協調 | Domain Service |
| 外部リソースが必要 | Application Service |

### 実装例

```ruby
# app/domain_services/contract_transfer_service.rb
class ContractTransferService
  def transfer(contract:, from_team:, to_team:)
    raise UnauthorizedError unless from_team.owns?(contract)
    raise InactiveTeamError unless to_team.active?

    contract.transfer_to(to_team)
    from_team.remove_contract(contract)
    to_team.add_contract(contract)
  end
end
```
