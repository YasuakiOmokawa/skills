# Clean Architecture

## 本質（2つの原則）

### 原則1: 依存性は上位レベル（内側）にのみ向ける

```
┌─────────────────────────────────────────────────────┐
│  Frameworks & Drivers                               │
│  (Web, UI, DB, Devices, External Interfaces)       │
│  ┌─────────────────────────────────────────────┐   │
│  │  Interface Adapters                          │   │
│  │  (Controllers, Gateways, Presenters)        │   │
│  │  ┌─────────────────────────────────────┐    │   │
│  │  │  Application Business Rules          │    │   │
│  │  │  (Use Cases)                         │    │   │
│  │  │  ┌─────────────────────────────┐    │    │   │
│  │  │  │  Enterprise Business Rules  │    │    │   │
│  │  │  │  (Entities)                 │    │    │   │
│  │  │  └─────────────────────────────┘    │    │   │
│  │  └─────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
                    ↑
            依存の方向（外→内のみ）
```

**ルール**:
- 外側のレイヤーは内側に依存してよい
- 内側のレイヤーは外側を知らない
- ドメイン層（Entities）はフレームワーク、DB、UI を一切知らない

### 原則2: 制御の流れと依存方向は分離してコントロール

実行時の制御フローと、コンパイル時の依存方向は一致しなくてよい。
**インターフェース**を使って依存を逆転させる。

```
【制御の流れ】
Controller → UseCase → Repository → Database
    →          →          →          →

【依存の方向（インターフェースで逆転）】
Controller → UseCase ← RepositoryInterface
                              ↑
                      RepositoryImpl → Database
```

## よくある誤解

| 誤解 | 事実 |
|------|------|
| 4層構造が必須 | 参考例に過ぎない。2層でも10層でもよい |
| MVC/MVVMを否定 | 共存可能。Clean Architecture は依存の向きのルール |
| 一方向の制御フローが必須 | 制御と依存は別。双方向の制御も可能 |
| Repository パターン必須 | 依存逆転の一例。他の方法もある |
| 全てのプロジェクトに適用 | 規模・複雑さに応じて判断 |

## フラクタル構造

Clean Architecture のルールは**あらゆるレベル**で適用可能:

```
【システム間】
サービスA → サービスB（API経由）
    ↓
依存はビジネスロジック（内側）に向ける

【コンポーネント間】
UIコンポーネント → ビジネスロジック → データアクセス
    ↓
依存は内側に向ける

【クラス間】
Controller → UseCase → Entity
    ↓
依存は内側に向ける

【関数間】
ハンドラ関数 → 純粋関数（ビジネスロジック）
    ↓
依存は内側に向ける
```

## 違反パターンと修正

### パターン1: ドメインがフレームワークに依存

```typescript
// ❌ 違反: ドメインが外側（DB）に依存
// domain/user.ts
import { db } from '@/lib/drizzle'

export class User {
  async save() {
    await db.insert(users).values(this)
  }
}

// ✅ 修正: 依存逆転
// domain/user.ts
export interface UserRepository {
  save(user: User): Promise<void>
}

export class User {
  constructor(private repo: UserRepository) {}
  async save() {
    await this.repo.save(this)
  }
}

// infrastructure/drizzle-user-repository.ts
import { db } from '@/lib/drizzle'
import { UserRepository, User } from '@/domain/user'

export class DrizzleUserRepository implements UserRepository {
  async save(user: User) {
    await db.insert(users).values(user)
  }
}
```

### パターン2: UseCase が UI に依存

```typescript
// ❌ 違反: UseCase が外側（UI形式）に依存
// usecases/create-order.ts
import { toast } from 'sonner'

export const createOrder = async (data) => {
  const order = await orderRepo.create(data)
  toast.success('注文を作成しました')  // UI に依存
  return order
}

// ✅ 修正: UseCase は結果を返すだけ
// usecases/create-order.ts
export const createOrder = async (data) => {
  return await orderRepo.create(data)
}

// ui/order-form.tsx
import { createOrder } from '@/usecases/create-order'
import { toast } from 'sonner'

const handleSubmit = async (data) => {
  const order = await createOrder(data)
  toast.success('注文を作成しました')  // UI 層で通知
}
```

### パターン3: 循環依存

```typescript
// ❌ 違反: 循環依存
// services/user-service.ts
import { OrderService } from './order-service'

// services/order-service.ts
import { UserService } from './user-service'

// ✅ 修正: 共通の抽象に依存
// domain/interfaces.ts
export interface UserInfo { id: string; name: string }
export interface OrderInfo { id: string; userId: string }

// services/user-service.ts
import { UserInfo } from '@/domain/interfaces'
// OrderService を直接 import しない

// services/order-service.ts
import { UserInfo } from '@/domain/interfaces'
// UserService を直接 import しない
```

## 適用判断

| 条件 | 推奨 |
|------|------|
| 小規模・短命なプロジェクト | シンプルな構成でOK |
| 中〜大規模プロジェクト | Clean Architecture 適用を検討 |
| 外部依存（DB, API）が多い | 依存逆転を適用 |
| テスタビリティ重視 | 依存逆転を適用 |
| チーム開発 | レイヤー分離を明確に |

## プロジェクト例

### Effect-TS プロジェクト（このプロジェクト）

```
app/
├── domain/           # Enterprise Business Rules（内側）
│   └── *.ts          # Brand型、Data.case
├── services/         # Application Business Rules
│   └── *-service.ts  # Effect.Service
├── lib/              # Interface Adapters
│   ├── actions.ts    # Server Actions
│   └── data.ts       # Data fetching
└── (pages)/          # Frameworks & Drivers（外側）
    └── *.tsx         # Next.js pages

# 依存の方向
pages → actions → services → domain
  ↑                            ↑
外側                          内側
```

### Rails プロジェクト

```
app/
├── models/           # Enterprise Business Rules + ORM
├── services/         # Application Business Rules
├── controllers/      # Interface Adapters
└── views/            # Frameworks & Drivers

# 注意: Rails は ActiveRecord で DB と密結合
# 完全な Clean Architecture は難しいが、
# Service 層で依存の向きを意識する
```

## チェックリスト

- [ ] ドメイン層がフレームワークを import していないか？
- [ ] ドメイン層が DB ライブラリを import していないか？
- [ ] ドメイン層が UI ライブラリを import していないか？
- [ ] UseCase が直接 UI を操作していないか？
- [ ] 循環依存が発生していないか？
- [ ] インターフェースで依存逆転すべき箇所はないか？
