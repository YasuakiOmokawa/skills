# Hexagonal Architecture (Ports & Adapters)

## 概要

アプリケーションの中心にあるビジネスロジックを、外部の技術的関心事から分離するアーキテクチャ。

```
              ┌───────────────────────────────────────┐
              │            外部システム                │
              │  (Web, CLI, Tests, Batch, Message)    │
              └──────────────┬────────────────────────┘
                             │ 呼び出す
                             ▼
┌────────────────────────────────────────────────────────────────┐
│                    Primary Adapters                            │
│  (Controllers, CLI Handlers, Event Listeners)                  │
└────────────────────────────┬───────────────────────────────────┘
                             │ 実装する
                             ▼
┌────────────────────────────────────────────────────────────────┐
│                    Primary Ports (Driving)                     │
│  (Use Cases / Application Services / Interfaces)               │
└────────────────────────────┬───────────────────────────────────┘
                             │ 呼び出す
                             ▼
┌────────────────────────────────────────────────────────────────┐
│                      Domain Layer                              │
│  (Entities, Value Objects, Domain Services)                    │
└────────────────────────────┬───────────────────────────────────┘
                             │ 定義する
                             ▼
┌────────────────────────────────────────────────────────────────┐
│                   Secondary Ports (Driven)                     │
│  (Repository Interfaces, External Service Interfaces)          │
└────────────────────────────┬───────────────────────────────────┘
                             │ 実装される
                             ▼
┌────────────────────────────────────────────────────────────────┐
│                   Secondary Adapters                           │
│  (Repository Impls, API Clients, DB Access)                    │
└────────────────────────────┬───────────────────────────────────┘
                             │ 接続する
                             ▼
              ┌───────────────────────────────────────┐
              │           外部リソース                 │
              │  (Database, APIs, File System, Queue) │
              └───────────────────────────────────────┘
```

## Port と Adapter の役割

### Primary Port（Driving Port）
- **定義**: アプリケーションが**提供する**機能のインターフェース
- **実装者**: ドメイン層 / Application Service
- **呼び出し元**: 外部（Controller, CLI, Test）

### Secondary Port（Driven Port）
- **定義**: アプリケーションが**必要とする**機能のインターフェース
- **実装者**: Infrastructure層（Adapter）
- **呼び出し元**: ドメイン層

### Adapter
- Port の具体的な実装
- 外部技術とドメインの翻訳層

## Rails での適用例

### ディレクトリ構造
```
app/
├── controllers/           # Primary Adapter
│   └── contracts_controller.rb
├── services/              # Primary Port (Use Case)
│   └── create_contract_service.rb
├── models/                # Domain Layer
│   └── contract.rb
├── repositories/          # Secondary Port + Adapter
│   ├── contract_repository.rb        # Interface (Port)
│   └── active_record_contract_repository.rb  # Adapter
└── adapters/              # Secondary Adapter
    └── sendgrid_mailer.rb
```

### コード例

**Primary Port（Use Case）**:
```ruby
# app/services/create_contract_service.rb
class CreateContractService
  def initialize(contract_repository:, mailer:)
    @contract_repository = contract_repository
    @mailer = mailer
  end

  def call(params)
    contract = Contract.new(params)
    @contract_repository.save(contract)
    @mailer.send_created_notification(contract)
    contract
  end
end
```

**Secondary Port（Repository Interface）**:
```ruby
# app/repositories/contract_repository.rb
class ContractRepository
  def save(contract)
    raise NotImplementedError
  end

  def find_by_id(id)
    raise NotImplementedError
  end
end
```

**Secondary Adapter（Repository Implementation）**:
```ruby
# app/repositories/active_record_contract_repository.rb
class ActiveRecordContractRepository < ContractRepository
  def save(contract)
    # ActiveRecord を使った保存
    ContractRecord.create!(contract.to_h)
  end

  def find_by_id(id)
    record = ContractRecord.find(id)
    Contract.from_record(record)
  end
end
```

## TypeScript/React での適用例

### ディレクトリ構造
```
front/
├── entrypoints/           # Primary Adapter (React entry)
├── hooks/                 # Secondary Adapter (API Client)
│   └── use-contract-api.ts
├── pages/                 # Primary Port (Use Case / Handler)
│   └── use-create-contract.ts
├── domain/                # Domain Layer
│   └── contract.ts
└── templates/             # Primary Adapter (UI)
    └── contract-form.template.tsx
```

### コード例

**Secondary Port（Repository Interface）**:
```typescript
// front/domain/contract-repository.ts
export interface ContractRepository {
  save(contract: Contract): Promise<Contract>;
  findById(id: string): Promise<Contract | null>;
}
```

**Secondary Adapter（API Client）**:
```typescript
// front/hooks/use-contract-api.ts
export const useContractApi = (): ContractRepository => {
  const api = useMemo(() => new ContractsApi(createApiConfig()), []);

  return {
    save: async (contract) => {
      const response = await api.create({ contract });
      return mapToContract(response);
    },
    findById: async (id) => {
      const response = await api.get({ id });
      return mapToContract(response);
    },
  };
};
```

**Primary Port（Use Case）**:
```typescript
// front/pages/use-create-contract.ts
export const useCreateContract = (repository: ContractRepository) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const create = async (params: CreateContractParams) => {
    setLoading(true);
    try {
      const contract = Contract.create(params);
      return await repository.save(contract);
    } catch (e) {
      setError(e as Error);
      throw e;
    } finally {
      setLoading(false);
    }
  };

  return { create, loading, error };
};
```

## 採用判断基準

### 採用すべき場合
| 状況 | 理由 |
|------|------|
| 外部サービスの差し替え可能性が必要 | テスト時のモック、本番での切り替え |
| 複数の入力チャネルがある | Web, CLI, Batch が同じロジックを使う |
| 長期保守が前提 | 技術スタックの変更に強い |

### 採用しない方が良い場合
| 状況 | 理由 |
|------|------|
| 単純な CRUD | 過度な抽象化になる |
| プロトタイプ / 短期プロジェクト | 開発速度が優先 |
| 外部依存が少ない | Port/Adapter のメリットが薄い |

## Clean Architecture との関係

```
Hexagonal Architecture        Clean Architecture
─────────────────────        ──────────────────
Primary Adapters      ≈      Frameworks & Drivers
Primary Ports         ≈      Interface Adapters
Domain Layer          ≈      Application + Enterprise Business
Secondary Ports       ≈      Interface Adapters
Secondary Adapters    ≈      Frameworks & Drivers
```

両者の本質は同じ: **依存性を内側に向ける**

違いは視点:
- Hexagonal: ポートを中心に「外部との接続点」を意識
- Clean: レイヤーを中心に「依存の方向」を意識
