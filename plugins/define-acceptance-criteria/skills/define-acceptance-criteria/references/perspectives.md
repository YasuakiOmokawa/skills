# 観点 Controlled Vocabulary と変更種別検出

`/define-acceptance-criteria` で使う AC 観点ラベルは、ここで定義された **controlled vocabulary** から選択する。自由形式のラベルは禁止 (mece-plan-review の `area` タグと対応させ、機械的に集約可能にするため)。

## Step A: 変更種別の機械的判定 (Step 2 の前段)

プランファイルから抽出した変更ファイルパスを以下のマッピングに照合し、変更種別候補を機械的に列挙する。LLM はその候補から最終 3-5 個を選定するだけで済む (種別推論の負荷削減)。

### パスパターン → 変更種別マッピング

| パスパターン (正規表現相当) | 変更種別 |
|---|---|
| `app/controllers/.*api.*` / `app/controllers/api/` | api_change |
| `app/controllers/` (api 以外) | controller_change |
| `app/models/` | db_or_model_change |
| `db/migrate/` / `db/schema.rb` | db_change |
| `app/services/` | service_change |
| `app/jobs/` / `app/workers/` | batch_change |
| `app/mailers/` | mail_change |
| `app/policies/` / `*Policy.rb` | auth_change |
| `config/initializers/devise` / `app/controllers/*auth*` / `*saml*` | auth_change |
| `front/templates/` / `front/pages/` / `front/components/` | ui_change |
| `front/hooks/` / `front/utils/` | frontend_logic_change |
| `*.tf` / `terraform/` | infra_change |
| `.github/workflows/` / `lefthook.yml` / `.claude/` | meta_dev_change |
| `Gemfile` / `package.json` / `yarn.lock` | dependency_change |
| `lib/` (ライブラリ整備) | library_change |
| `plugins/.*/SKILL.md` / `plugins/.*/agents/` | skill_or_prompt_change |
| `app/.*/feature_flag/` / `config/features/` | flag_change |
| `app/.*/external_api/` / 外部 API client | external_api_change |
| `app/queries/` (Query オブジェクト) | db_or_model_change |
| `app/forms/` / `app/form_objects/` | controller_change |

**未マッチ時の fallback (裁量判断を排除)**: 上表に無い `app/*/` 配下は最も近い層の既存種別へ従属させる (データ取得系 → `db_or_model_change` / 入力受付系 → `controller_change`)。`config/` 配下 (initializers 除く) や `config/routes.rb` は単独で種別を持たない supporting file とみなし、関連する主種別の副次扱いにして独自の観点軸を起こさない。

### 変更種別 → デフォルト観点軸 (controlled vocabulary)

種別を選定した後、以下の表から該当する観点軸を 3-5 個選ぶ。各軸の右列の controlled label を AC 行頭に使う。

| 変更種別 | 軸名 | controlled label (AC 行頭で使う、既定値はそのまま採用) |
|---|---|---|
| auth_change | ユーザー種別 | `user_type` |
| auth_change | 認証状態 | `auth_state` |
| auth_change | 外部 IdP | `idp` |
| auth_change | 権限境界 | `permission` |
| api_change / controller_change | リクエスト形式 | `req_form` |
| api_change / controller_change / ui_change | リクエスト文脈 | `req_context` |
| api_change / controller_change | 部分更新時の未送信キー挙動 | `unsent_keys` |
| api_change | 権限 | `permission` |
| api_change | 後方互換性 | `compat` |
| db_change / db_or_model_change | データ量 | `data_volume` |
| db_change | マイグレーション | `migration` |
| db_change | 既存データ互換 | `data_compat` |
| ui_change | デバイス | `device` |
| ui_change | ブラウザ | `browser` |
| ui_change | アクセシビリティ | `a11y` |
| batch_change | データ量 | `data_volume` |
| batch_change | 実行時間 | `runtime` |
| batch_change | 冪等性 | `idempotency` |
| flag_change | フラグ状態 | `flag_state` |
| flag_change | 段階ロールアウト | `rollout` |
| flag_change | 削除後等価性 | `flag_removal` |
| skill_or_prompt_change | 情報源 | `info_src` |
| skill_or_prompt_change | コンテキスト | `context` |
| skill_or_prompt_change | フォールバック | `fallback` |
| skill_or_prompt_change | 出力契約 | `output_contract` |
| infra_change | 環境 | `env` |
| infra_change | リソース型 | `resource` |
| infra_change | 権限 (IAM) | `permission` |
| infra_change | 削除副作用 | `lifecycle` |
| library_change | バージョン互換 | `semver` |
| library_change | 呼び出し元 | `caller` |
| library_change | ドキュメント整合 | `doc_sync` |
| library_change | 後方互換 deprecation | `deprecation` |
| meta_dev_change | ローカル vs CI | `env` |
| meta_dev_change | 他開発者影響 | `dev_impact` |
| meta_dev_change | rollback | `rollback` |
| meta_dev_change | shared config 影響範囲 | `config_scope` |
| external_api_change | API バージョン | `api_version` |
| external_api_change | 認証方式 | `auth_method` |
| external_api_change | レート制限 | `rate_limit` |
| external_api_change | 障害時縮退 | `fallback` |
| mail_change | 配信タイミング | `delivery` |
| mail_change | テンプレート | `template` |
| service_change | 呼び出し元 | `caller` |
| service_change | エラー伝播 | `error_prop` |
| **全種別 (追加候補)** | 監査ログ / メトリクス / 構造化ログ | `observability` |

**ui_change の copy / 文言のみ変更時の主軸**: `device` を主軸に採る (ラベル長・文字列の変化による truncation / overflow / 折り返しが唯一の実観測点のため)。`a11y` は読み上げ名・ARIA に踏み込む変更がある時のみ、`browser` はブラウザ依存描画が絡む時のみ採用する。

**req_context (リクエスト文脈) の適用対象**: 機能と直交して全リクエストへ自動付与される条件 (マルチテナント / OEM 識別クエリ・サブドメイン・ロケール等) を持つプロダクトで、URL の生成・結合・リダイレクトに触れる変更に採用する。フレームワークが生成 URL へ自動でクエリを載せる機構 (Rails の `default_url_options` 等) があると「クエリなしパス」前提の文字列結合契約が壊れるため、直交条件が付与された状態の AC を最低 1 本置く (理由: OEM 識別クエリが URL パス断片へ混入し、後置結合した URL が 404 になる regression を、AC 化されていなかったためにコードレビュー複数パスが素通しし、実機操作で発覚した実測)。

**unsent_keys (部分更新時の未送信キー挙動) の適用対象**: 既存レコードを PATCH/POST で部分更新する変更で、参照実装 (旧 UI / 旧経路) からキーを間引いた場合に採用する。nested attributes (`*_attributes=`) や汎用 setter は未送信キーを無条件代入 (nil 上書き) することがあり既存値保持とは挙動が分かれるため、サーバ側の代入処理まで読んで確認する AC を最低 1 本置く (理由: payload を id と value に絞った結果 `document_items_attributes=` が未送信キーを無条件代入し、保存済みマイ印鑑が最終送信で消える regression を作った事例。品質レビュー 6 パスは素通りし、サーバ往復を追跡した最終レビューで検出)。

### area タグ対応 (mece-plan-review との接続)

各 controlled label は mece-plan-review の `area` タグに以下のように対応する:

| AC 観点 label | area タグ (mece-plan-review) |
|---|---|
| `auth_state` / `idp` / `user_type` / `permission` | `auth` |
| `req_form` / `compat` | `business` or `network` |
| `req_context` | `network` |
| `data_volume` / `migration` / `data_compat` / `unsent_keys` | `data` |
| `device` / `browser` / `a11y` | `ui` |
| `runtime` / `idempotency` | `performance` |
| `flag_state` / `rollout` / `flag_removal` | `business` |
| `info_src` / `context` / `output_contract` | `business` (or `その他`) |
| `fallback` / `rollback` / `lifecycle` | `infra` |
| `env` / `resource` / `config_scope` | `infra` |
| `semver` / `caller` / `doc_sync` / `deprecation` | `deps` |
| `dev_impact` | `その他` |
| `api_version` / `auth_method` / `rate_limit` | `network` |
| `delivery` / `template` | `business` |
| `error_prop` | `observability` (or `その他`) |
| `observability` | `observability` |

この対応表は mece-plan-review が JSONL findings を集約する際に同 `area` でクロスリファレンスするため、ラベル粒度を揃える目的で重要。

## Step B: 表に該当する変更種別がない場合

裁量判断として、以下の汎用候補軸から 3-5 個を選び、分析ファイルの `### 検討観点` に「裁量判断 (理由: ...)」と 1 文で明記する。汎用候補軸は controlled vocabulary に既存ラベルがなければ追加する PR を出す:

- `dep_loc` — 外部依存の所在 (Service 内 / Adapter 内 / Model 内)
- `layer` — レイヤー / チャネル
- `non_invasive` — 失敗時の非侵襲性
- `contract` — 既存契約との境界

## ラベル運用ルール (厳守)

1. **AC 行頭は controlled label**: 例 `- [ ] permission [境界値: 未ログイン]: PATCH /api/users/:id → 401`
2. **同じ skill 内で揺らさない**: 一度決めたラベルを全 AC で同一表記
3. **既定 label をそのまま使う (grandfathered)**: 上記表の `permission` / `observability` / `data_compat` / `req_form` 等は字数制約の対象外。新規追加する場合のみ「12 文字以内・名詞のみ」を目安にする (SKILL.md `Quantitative scaffolding` と同期)
4. **AC 末尾の `(仕様確定要)`**: プラン本文に欠落する仕様を AC 側で仮置きする場合のみ付与
