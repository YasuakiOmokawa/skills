# Anti-Patterns 早見表 (Quick Reference)

reviewer 起動時はこのファイルのみ Read する。判定で迷ったら `anti-patterns.md` 本体を Read する。

| # | アンチパターン | 一行症状 | Grep ヒント | 改善方向 |
|---|---|---|---|---|
| 1 | Anemic Domain Model | モデルが getter/setter のみで振る舞いがない | `\.status\s*=` / `\.update!\(` in services | 状態遷移メソッドを Model へ |
| 2 | Fat Controller | Controller にビジネスロジックが集中 | `\.where\(` / `\.save` / `if.*\.present?` in controllers | Service に抽出 |
| 3 | God Object | 1クラスが多くの責務を抱える | クラス行数 / `def ` 数 | 責務単位で分割 |
| 4 | Leaky Abstraction | Repository が `ActiveRecord::Relation` を漏らす | `ActiveRecord::Relation` in services / `service.*\.where\(` | Array / DTO を返す |
| 5 | Circular Dependency | A↔B の相互参照 | A→B と B→A の `require` / `import` | 共通インターフェースで分離 |
| 6 | Shotgun Surgery | 1 変更が多ファイルに波及 | 概念名 (例: `:active`) の散在ファイル数 | 関連ロジックを 1 箇所に集約 |
| 7 | Premature Abstraction | 使われない抽象化 / 1 実装しかない interface | `NotImplementedError` / `class.*<.*Base` | YAGNI、削除して具体実装に戻す |
| 8 | Feature Envy | 他オブジェクトのデータを 5 回以上連続参照 | `target\.` の同一メソッド内出現回数 | ロジックをデータ持ち主のクラスへ |

## 早見判定基準 (3 値表)

各観点について、以下の閾値で判定する。詳細な例は `anti-patterns.md` を参照。

| # | ✅ | ⚠️ | ❌ |
|---|---|---|---|
| 1 Anemic | Model に状態遷移・バリデーション・計算あり | Service が 1-2 箇所で属性直接操作 | Service が 3 箇所以上で属性操作 or Model に getter のみ |
| 2 Fat Controller | アクション 5 行以下 | アクション 6-15 行 | アクション 16 行以上 or ビジネスルール直書き |
| 3 God Object | publicメソッド 10 以下・行数 200 以下 | public 11-20 / 行数 201-400 / 責務「〜と〜」 | public 21+ / 行数 401+ / 責務 3 つ以上 |
| 4 Leaky Abstraction | Service/Repo が抽象化済み、追加 chain なし | AR::Relation 漏れ + 追加 chain 1 箇所 | 追加 chain 2 箇所以上 or 内部知識漏れ |
| 5 Circular Dep | 一方向 | 間接的循環 (A→B→C→A) で実害なし | 直接循環 (A↔B) |
| 6 Shotgun | 1-2 ファイルで完結 | 3-5 ファイル / 同一ディレクトリ | 6 ファイル以上 or レイヤー跨ぎ |
| 7 Premature | 抽象化に 2+ 実装 or 拡張予定明確 | 1 実装だがテストモック有用 | 1 実装かつテスト用途なし |
| 8 Feature Envy | 同一メソッド内アクセス 2 回以下 | 3-4 回 | 5 回以上 or getter 連鎖 |

## 詳細を Read する条件 (観測可能トリガー)

以下のいずれかに該当する場合のみ `anti-patterns.md` 本体を Read する:

- Grep ヒット数が ⚠️ と ❌ の境界 ±1 にある (例: Fat Controller のアクションが 15-17 行)
- 検出対象が ActiveRecord callback / association / scope を含む (Rails 固有の例外確認が必要)
- ユーザーへの出力に改善コード例を含める必要がある (推奨修正の雛形が必要)
- 判定が ⚠️ で具体例の参照なしには ✅ か ❌ かを決定できない場合
