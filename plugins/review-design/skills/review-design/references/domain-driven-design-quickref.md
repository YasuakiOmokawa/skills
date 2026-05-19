# DDD 戦術パターン 早見表 (Quick Reference)

reviewer 起動時はこのファイルのみ Read する。判定で迷ったら `domain-driven-design.md` 本体を Read する。

**Rails 前提**: ActiveRecord モデルを Domain Model として使うのは正当。PORO 分離が常に正しいわけではない。

## Entity vs Value Object 早見表

| 観点 | Entity | Value Object |
|---|---|---|
| 同一性 | ID で識別 | 属性の組み合わせで識別 |
| 可変性 | 状態変更可能 | イミュータブル |
| 例 | User / Contract / Order | Money / Address / DateRange |

判断: 「同じもの」と判断する基準が「一意の ID」なら Entity、「属性の組み合わせ」なら Value Object。

## Aggregate 設計の原則 (4 つ)

1. 外部からは Aggregate Root のみ参照
2. Aggregate 内の整合性は Root が保証
3. トランザクション境界 = Aggregate 境界
4. Aggregate 間の参照は ID のみ (オブジェクト参照禁止)

## 早見判定基準

| # | 観点 | ✅ | ⚠️ | ❌ |
|---|---|---|---|---|
| 1 | Entity vs VO | Entity は ID で識別、VO 的概念は適切に扱う | VO にすべき概念がプリミティブのまま (例: 金額が Integer のみ) | ID で識別すべきものに ID なし / VO が可変 (setter 公開) |
| 2 | Aggregate 境界 | 外部から Root のみ参照、Aggregate 間は ID 参照 | 内部 Entity 直アクセス 1-2 箇所 (読み取りのみ) | 内部 Entity を外部から create/update/delete |
| 3 | Domain Event | 副作用が明示管理 (Service 呼出 or `after_commit` の Job キックのみ) | `after_commit` で Job キック (Rails 許容) | `before/after_save` で外部 API / メール / 3 つ以上の副作用連鎖 |
| 4 | Domain Service | 単一 Entity 振る舞いは Entity に / 複数協調は Service | 単一 Entity ロジックが Service にあるがテスト性で正当 | Model 内で他 Model を直接 create/update / Service が全ロジック持ち Model 空 (Anemic) |

## 反例検索 Grep ヒント

| 観点 | 検索パターン | ファイル |
|---|---|---|
| VO 化漏れ | `_amount` / `_price` (Integer のまま) | app/models/ |
| 日付範囲未集約 | `_at.*_at` 同一 Model | app/models/ |
| Aggregate 境界違反 | `OrderItem\.find` / `OrderItem\.update` / `OrderItem\.create` | app/ 全体 |
| コールバック過多 | `after_save` / `after_commit` / `after_create` の数 | app/models/ |
| コールバック内副作用 | `Mailer` / `perform_later` in `after_*` | app/models/ |
| Model 間越境 | `OtherModel\.create` / `OtherModel\.update` | app/models/対象.rb |

## Rails 例外 (許容される)

- ActiveRecord の `has_many` association で内部 Entity にアクセス → ✅
- `after_commit` で非同期 Job をキック → ⚠️ (一般的パターン)

## 推奨修正の雛形 (短文テンプレ)

| 違反種 | 推奨修正テンプレ |
|---|---|
| VO 化漏れ | `<concept> を Value Object クラス <Money/Address/...> に抽出` |
| Aggregate 境界違反 | `<file>:<line> で内部 Entity を直接操作。<Root>#<method> 経由に変更` |
| コールバック過多 | `<model>:<line> の <after_save 副作用> を Service から明示呼び出しに移行 (Domain Event パターン候補)` |
| Model 間越境 | `<model>:<line> で他 Model を直接 create/update。Domain Service に分離` |

## 詳細を Read する条件 (観測可能トリガー)

以下のいずれかに該当する場合のみ `domain-driven-design.md` 本体を Read する:

- ユーザーへの出力に Entity / Value Object の具体実装例 (Ruby / TypeScript) を含める必要がある
- 設計判断が Rails ActiveRecord アプローチ 1 (AR-as-Entity) と 2 (PORO + 永続化分離) の境界にある
- ユーザーへの出力に Aggregate / Domain Service / Domain Event の Ruby 実装パターンを含める必要がある
