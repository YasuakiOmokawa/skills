# Clean Architecture 早見表 (Quick Reference)

reviewer 起動時はこのファイルのみ Read する。判定で迷ったら `clean-architecture.md` 本体を Read する。

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
| 1 | 依存方向 | 内側レイヤーが外側を一切参照しない | 軽微違反 1-2 箇所 (Rails.logger 等は許容) | Model/Service が Controller/View/外部 SDK を直接参照 |
| 2 | レイヤー分離 | 各レイヤー責務が明確に分離 | 1 レイヤー責務の漏れ少 (Controller の where 1 箇所等) | Controller に複雑クエリ / Model にプレゼンテーション |
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

## 詳細を Read する条件 (観測可能トリガー)

以下のいずれかに該当する場合のみ `clean-architecture.md` 本体を Read する:

- 検出対象が 3 レイヤー以上を跨ぐ (4 層構造の理解が必要)
- ユーザーへの出力に依存逆転 (DIP) の具体実装例を含める必要がある
- 対象プロジェクトが Effect-TS / 純 TypeScript (Rails 以外) で、参考例の照合が必要
