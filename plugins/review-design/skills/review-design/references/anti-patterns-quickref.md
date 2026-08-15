# Anti-Patterns 早見表 (Quick Reference)

reviewer はこのファイルを SSOT として使う。

| # | アンチパターン | 一行症状 | Grep ヒント | 改善方向 |
|---|---|---|---|---|
| 1 | Anemic Domain Model | モデルが getter/setter のみで振る舞いがない | `\.status\s*=` / `\.update!\(` in services | 状態遷移メソッドを Model へ |
| 2 | Fat Controller | Controller にビジネスロジックが集中 | `\.where\(` / `\.save` / `if.*\.present?` in controllers | Service に抽出 |
| 3 | God Object | 1クラスが独立に変化する複数責務を抱える | 無関係な method 群・依存先 | 責務単位で分割 |
| 4 | Leaky Abstraction | Repository が `ActiveRecord::Relation` を漏らす | `ActiveRecord::Relation` in services / `service.*\.where\(` | Array / DTO を返す |
| 5 | Circular Dependency | A↔B の相互参照 | A→B と B→A の `require` / `import` | 共通インターフェースで分離 |
| 6 | Shotgun Surgery | 1 変更が多ファイルに波及 | 概念名 (例: `:active`) の散在ファイル数 | 関連ロジックを 1 箇所に集約 |
| 7 | Premature Abstraction | 使われない抽象化 / 1 実装しかない interface | `NotImplementedError` / `class.*<.*Base` | YAGNI、削除して具体実装に戻す |
| 8 | Feature Envy | 判断ロジックが他オブジェクトの内部データ操作に偏る | 同一対象への getter chain | ロジックをデータ持ち主のクラスへ |
| 9 | Reinventing Platform Primitives | 標準機能があるのに数値/日付/URL/deep copy/ID/後始末を手書き | —（grep 不可・知識ベース判定） | 組込みに置換し、自前実装とそれだけを検証する専用テストを削除 |

## 早見判定基準 (3 値表)

| # | ✅ | ⚠️ | ❌ |
|---|---|---|---|
| 1 Anemic | Model が状態遷移・不変条件・計算を所有 | Service の直接操作は調整だけで規則を持たない | 業務規則と状態遷移が Model 外へ散在 / Model はデータ入れ物だけ |
| 2 Fat Controller | 入力変換・認可・委譲に閉じる | orchestration と表示整形・query が一部混在 | ビジネス判断やデータ更新手順を Controller が所有 |
| 3 God Object | 一つの変更理由と凝集した interface | 複数の変更理由が現れ始めているが境界は分離可能 | 独立に変化する責務と依存を一つの class が所有 |
| 4 Leaky Abstraction | caller は抽象化された値だけに依存 | 内部型の漏れが境界内に封じられている | caller が内部型・query chain・永続化知識へ依存 |
| 5 Circular Dep | 依存が一方向 | 間接循環だが初期化・変更・test への影響が封じられている | 直接循環または変更順・初期化順を相互依存 |
| 6 Shotgun | 一つの責務所有者へ変更が局在 | 同一関心の協調変更が近接境界に広がる | 一つの振る舞い変更が無関係な責務・layerへ反復波及 |
| 7 Premature | 現存する差し替え先または確定した拡張を抽象化 | 外部境界の隔離・テスト差し替えに実在する価値がある | 将来仮説だけで抽象化し、差し替え・隔離価値がない |
| 8 Feature Envy | 判断を自分の状態・責務で行う | collaborator のデータ参照は調整に留まる | 判断の大半が他オブジェクトの内部データ操作・getter chain |
| 9 Reinventing Primitives | 標準機能を使用 | 環境制約（設定と照合して実在確認済み）で自前実装 + 置換先を実装イメージ付き TODO コメントで明記 | 標準機能が存在するのに黙って自前実装（設定と照合して成立しない制約主張もここ） |
