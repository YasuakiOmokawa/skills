# Clean Architecture 早見表 (Quick Reference)

reviewer はこのファイルを SSOT として使う。

## 本質 (2 原則)

1. **依存性は内側 (上位レベル) にのみ向ける** — 外側のレイヤーは内側に依存してよい、逆は禁止
2. **制御の流れと依存方向は分離してコントロール** — インターフェースで依存を逆転できる

```
外側 → 内側のみ許可:
Frameworks/Drivers → Interface Adapters → Application Business → Enterprise Business
```

## 早見判定基準

| # | 観点 | ✅ | ⚠️ | ❌ |
|---|---|---|---|---|
| 1 | 依存方向 | 内側レイヤーが外側を参照しない | framework convenience への依存が境界内に閉じ、業務規則へ影響しない | Model/Service が Controller/View/外部 SDK を直接参照 |
| 2 | レイヤー分離 | 各レイヤー責務が明確に分離 | query・表示整形の詳細が残るが、業務判断は所有しない | Controller に複雑クエリ / Model にプレゼンテーション |
| 3 | 循環依存 | 一方向 | AR association の双方向 (Rails 標準) | Service 間の相互呼び出し / Model ビジネス論理の循環 |

## 反例検索 Grep ヒント

| 観点 | 検索パターン | ファイル |
|---|---|---|
| 依存方向違反 | `ActionController` / `render` / `redirect` / `params\[` | app/models/, app/services/ |
| 外部 SDK 直参照 | `SendGrid` / `Aws::` / `Twilio` / `aws-sdk` / `sendgrid` | app/models/, app/services/ |
| レイヤー混在 | `\.where\(` / `\.joins\(` / `\.includes\(` | app/controllers/ |
| Model にプレゼン | `\.to_json` / `format` / `ActionView::Helpers` | app/models/ |

## Rails 例外 (許容される違反)

- ActiveRecord を Domain Model として使うのは Rails Way → ✅
- `Rails.logger` を Model 内で使うのは ⚠️ レベル (許容)
- `has_many` / `belongs_to` による双方向 association は ⚠️ レベル (Rails 標準)

## 推奨修正の雛形 (短文テンプレ)

| 違反種 | 推奨修正テンプレ |
|---|---|
| 依存方向違反 | `<file>:<line> で <外側 SDK> を直接参照。<Service or Adapter> 経由に分離` |
| レイヤー混在 | `<file>:<line> の <where/joins> を <scope or Service> に移動` |
| 循環依存 | `<service A> と <service B> を共通インターフェース <I> 経由に変更` |
