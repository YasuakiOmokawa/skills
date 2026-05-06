# 環境設定（example）

## このファイルの使い方

このファイルを `docs/agents/environments.md` にコピーし、自社の値で書き換えてください。`/setup-omokawa-skills` で対話生成も可能です。

omokawa-skills の `/create-pr` コマンドがこのファイルを Read して、Revert 手順に列挙する環境名を取得します。

## rollback_targets

`production` / `sandbox` / `staging` に追加して列挙する **integration 環境名**：

- dev1
- dev2
- qa-stage

migration が含まれる PR の Revert 手順に「これらの環境すべてで `db:migrate:down` を実行」と展開されます。

## integration 環境がない組織

このファイルを作らないか、`rollback_targets` を空リストにしてください。`/create-pr` は `production` / `sandbox` / `staging` のみで Revert 手順を組み立てます。

## 注意

- 環境名は実環境にアクセス可能な名前と一致させる（typo すると revert 手順が機能しない）
- 環境名は通常**機密ではない**ため、リポジトリにコミットして問題なし
