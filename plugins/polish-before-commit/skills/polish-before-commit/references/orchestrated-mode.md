# Orchestrated モード (polish-before-commit)

## 発動条件

ファイル存在からの推測では判定しない。呼び出し側（オーケストレータ）が「orchestrated モードで実行。escalation は `<path>` に記帳して続行せよ」のように明示指示した場合のみ発動する。指示の伝達経路は `Task` 起動プロンプトでも、メインコンテキストで本 skill の手順を実行する直前の明示宣言でもよい（判定するのは宣言の有無であり伝達経路ではない）。指示が無い単独起動では本ファイルを参照せず、SKILL.md 本文の現行動作（判断項目 1 件以上でユーザーの明示指示を待つ）のまま進む。

## escalation ledger 形式

ファイル名は優先順で決める: (1) 発動条件の `<path>` が明示指定されていればそれを使う。(2) 未指定だが呼び出し側の指示に計画・仕様名 (「プラン名」) が含まれていれば `<プラン名>.escalation-ledger.md` を使う。(3) いずれも無ければ対象リポジトリの `$(git rev-parse --git-common-dir)/escalation-ledger.md` を既定値として使う (プラン名が無い場合に確実に導出できる場所のため)。1 行 = 1 項目、追記のみ（既存行は書き換えない）。

| 番号 | 出所 | 深刻度 (Critical/Major/Minor) | 内容 | 根拠 | 推奨アクション |
|---|---|---|---|---|---|

- 「番号」は記帳前に ledger を Read し、既存の最終番号 +1 から採番する (ファイルが無ければ 1 から)。

## polish-before-commit 固有の記帳規則

Orchestrated モード時、以下の 2 箇所は SKILL.md 本文の「ユーザーの明示指示を待つ」「ユーザー承認後に編集」を「escalation ledger に記帳して続行する」に読み替える。

1. **Manual Review Items #4 (dead mock の部分削除)**: 削除せず、書換え候補（残す identifier / 削除する identifier）を「保留」として escalation ledger に記帳する。深刻度は Minor 固定（実装の欠陥ではなく spec 整理判断のため）。
2. **Step 9 (判断申し送りの集約)**: 判断項目が 1 件以上でもユーザーの返答を待たず、Step 9 の一覧（申し送り + Manual Review Items + Step 8 最終レビューの残存指摘 + 外部診断ツールの残存指摘）を escalation ledger にそれぞれ 1 行ずつ記帳したうえで、完了報告して終了する。深刻度は各項目の出所側で決める: review-code-quality 申し送りは quality-ledger 側の深刻度を引き継ぐ、polish 検出の Manual Review Items は Minor 固定、**外部診断ツール由来で既存項目と統合されなかった単独項目は Minor 固定**（ツールの提案であり自 skill が欠陥として確認済みの指摘ではないため。既存項目と統合された場合は統合先の出所のルールに従う）、Step 8 (最終レビュー) 由来で上記いずれにも該当しない項目は Step 8 の内訳分類 (バグ / 規約違反 / その他) から機械的に決める（バグ → Major、規約違反・その他 → Minor）。

いずれの場合も申し送りファイル (`quality-review-handoff-<branch>.md`) のクリア (Step 9 手順 6) は Orchestrated モードの有無に関わらず実施する（ledger へ転記済みのため stale として残す必要がない）。

## 記帳例

```
| 5 | polish-before-commit | Minor | spec/models/user_spec.rb:88 の receive_messages(a:, b:) 部分削除 (a: のみ) | Manual Review Items #4 | b: を残す書換え案で承認後に編集 |
| 6 | polish-before-commit | Major | app/services/billing_service.rb:42 の認可チェック配置 | Step 9 集約 (review-code-quality 申し送り由来) | before_action :authorize へ統一 |
```
