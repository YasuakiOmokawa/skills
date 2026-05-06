# Rails 設計判断マトリクス

**Rails プロジェクトでは Rails Way を優先せよ。理論より規約。**

```
app/
├── controllers/  → リクエスト処理のみ。薄く。
├── models/       → ビジネスロジックの第一候補
├── services/     → 複数モデルにまたがる処理
├── forms/        → フォーム固有のバリデーション（ActiveRecordCompose）
├── jobs/         → 非同期処理（Sidekiq）
├── workers/      → Sidekiq Worker
└── loyalties/    → 認可（Banken）
```

| やりたいこと | 第一候補 | 条件付き代替 | 避けるべき |
|-------------|---------|-------------|-----------|
| バリデーション追加 | Model | Form Object（複合バリデーション、画面固有） | Controller |
| 複数モデル更新 | Service | Form Object（フォーム起点の場合） | Controller / Callback |
| 共通クエリ | scope | concern（複数モデル共通の場合のみ） | Service |
| コールバック | 使わない（明示的にService呼ぶ） | `after_commit`（非同期Jobキック限定） | `before_save` で外部API |
| 権限チェック | Banken loyalty | — | Controller 内 if 文 |
| JSON シリアライズ | Blueprint | — | Model 内 `to_json` |
| フィーチャーフラグ | Flipper | — | 環境変数 / ハードコーディング |
| 非同期処理 | Sidekiq Worker/Job | — | Controller 内で直接実行 |
| 外部API連携 | adapter/client クラス | — | Model / Controller 内で直接呼び出し |

Port/Adapter や Repository は**本当に必要な場合のみ**。ActiveRecord で十分なことが多い。
