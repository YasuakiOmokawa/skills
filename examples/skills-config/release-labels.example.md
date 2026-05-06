# リリースラベル設定（example）

## このファイルの使い方

このファイルを `~/.claude/skills-config/release-labels.md` にコピーし、自社の値で書き換えてください。`/setup-omokawa-skills` で対話生成も可能です。

omokawa-skills の `/create-pr` コマンドがこのファイルを Read してラベル定義を取得します。

## productivity_labels

ユーザーが使うラベル。実環境のラベル名に合わせて編集する：

- `1.Feature development`: ユーザー向け機能の追加・改善（例: 通知機能追加、画面新設、API公開）
- `2.Bugfix & Maintenance`: バグ修正、リファクタリング、ライブラリ更新（例: N+1 解消、責務分割）
- `3.Tech investment`: 共通基盤開発（例: 共通モジュール、CI 改善、計測基盤）
- `4.Quality improvement`: テスト追加、品質向上のためのリファクタ（例: 既存コードへの spec 追加）
- `5.Others`: Bot 生成 PR や上記に当てはまらないもの

## ai_contribution_labels

PR の AI 貢献度を示すラベル。4段階推奨：

- `ai-contribution-level:0`: AI 生成コードが 10% 未満
- `ai-contribution-level:1`: AI 生成コードが 10-40%
- `ai-contribution-level:2`: AI 生成コードが 40-80%
- `ai-contribution-level:3`: AI 生成コードが 80% 以上

## release_level_labels

リリース時の影響度ラベル。4段階推奨：

- `ReleaseLevel-1`: 表示のみの変更、パッチアップデート
- `ReleaseLevel-2`: 後方互換性のある変更、根幹機能に影響なし
- `ReleaseLevel-3`: 後方互換性のある変更、根幹機能に影響あり
- `ReleaseLevel-4`: 不可逆な変更、スキーマ変更、メジャーアップデート

## core_features

プロジェクトの根幹機能。`ReleaseLevel-3` 以上の判定に使用。**自社プロダクトの主要ドメインを列挙する**：

- 認証・認可
- 決済処理
- データ永続化
- 外部公開 API
- （プロダクト固有の主要フロー）

このリストが空の場合、`/create-pr` は対象リポジトリの `CLAUDE.md` / `README.md` 冒頭から推定します。

## 注意

- ラベル名は GitHub Issues / GitLab Issues に**実在するラベル**と一致させること（一致しないと PR 作成時にエラー）
- ラベルが存在しない組織なら、`/create-pr` 実行時に「ラベル付与をスキップしてドラフトPRを作成」と動作させる
