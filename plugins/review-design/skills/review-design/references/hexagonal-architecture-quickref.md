# Hexagonal Architecture 早見表 (Quick Reference)

reviewer 起動時はこのファイルのみ Read する。判定で迷ったら `hexagonal-architecture.md` 本体を Read する。

## 本質

ビジネスロジックを中心に置き、外部の技術的関心事 (DB / API / UI) から分離する。**Port (インターフェース) と Adapter (実装) を使い分ける**。

- **Primary Port (Driving)**: アプリが**提供する**機能 = Use Case / Application Service
- **Primary Adapter**: Primary Port を呼び出す側 = Controller / CLI Handler
- **Secondary Port (Driven)**: アプリが**必要とする**機能 = Repository Interface / External Service Interface
- **Secondary Adapter**: Secondary Port を実装する側 = Repository Impl / API Client

## 採用判断 (まずここを確認)

| 状況 | 判断 |
|---|---|
| 外部 API + テストでモック必要 | 採用推奨 |
| 複数チャネル (Web/CLI/Batch) で同じロジック | 採用推奨 |
| 単純 CRUD + ActiveRecord | 不要 (Rails Way) |
| 外部依存 1 つ + 差し替え予定なし | 不要 (YAGNI) |

## 早見判定基準

| # | 観点 | ✅ | ⚠️ | ❌ |
|---|---|---|---|---|
| 1 | 必要性判断 | 適切な採用/不採用判断 | 微妙な判断 (将来差し替え可能性低いのに導入) | 明らかな過剰適用 or 明らかに必要なのに未適用 |
| 2 | Primary Port 設計 | Service がフレームワーク非依存 | `params` hash 直受け取りあるが内部は独立 | Service が `ActionController::Parameters` 直受け / `render` 呼び出し |
| 3 | Secondary Port 設計 | 外部 SDK が Adapter 内に閉じる | Service が外部 SDK を 1 箇所参照、Adapter 移行容易 | Model が外部 SDK 直参照 / Service 複数箇所で外部 SDK |
| 4 | Adapter 実装 | Adapter は変換のみ | 軽微な変換以外 1 箇所 | Adapter にビジネスルール / 状態遷移 / 計算ロジック |

## 反例検索 Grep ヒント

| 観点 | 検索パターン | ファイル |
|---|---|---|
| 過剰適用 | `NotImplementedError` (実装 1 つのみの interface) | app/ 全体 |
| Primary Port 違反 | `ActionController::Parameters` / `render` / `redirect` | app/services/ |
| Secondary Port 違反 | `SendGrid` / `Twilio` / `Aws::S3` / `Net::HTTP` / `Faraday` / `HTTParty` | app/models/, app/services/ |
| Adapter ロジック漏れ | `if.*status` / `raise.*Error` | app/adapters/ |

## 推奨修正の雛形 (短文テンプレ)

| 違反種 | 推奨修正テンプレ |
|---|---|
| Primary Port 違反 | `<file>:<line> の <params/render> をプリミティブ型 or DTO 引数に変更` |
| Secondary Port 未定義 | `<file>:<line> の <外部 SDK> を <app/adapters/<name>.rb> に分離` |
| Adapter ロジック漏れ | `<adapter>:<line> のビジネスルール判定を <Service or Model> に移動` |
| 過剰適用 | `<interface> は実装 1 つのみ。具体実装に統合し YAGNI` |

## 詳細を Read する条件 (観測可能トリガー)

以下のいずれかに該当する場合のみ `hexagonal-architecture.md` 本体を Read する:

- ユーザーへの出力に Port/Adapter のディレクトリ構造提案を含める必要がある
- 対象プロジェクトが TypeScript/React で、Rails 例と照合できない
- 設計判断が Clean Architecture との境界に跨る (両者の関係性を説明する必要がある)
