# Orchestrated モード (polish-before-commit)

## 発動条件

ファイル存在からの推測では判定しない。呼び出し側（将来のオーケストレータ）が `Task` 起動プロンプトで「orchestrated モードで実行。escalation は `<path>` に記帳して続行せよ」のように明示指示した場合のみ発動する。指示が無い単独起動では本ファイルを参照せず、SKILL.md 本文の現行動作（判断項目 1 件以上でユーザーの明示指示を待つ）のまま進む。

## escalation ledger 形式

ファイル名: `<プラン名>.escalation-ledger.md`。1 行 = 1 項目、追記のみ（既存行は書き換えない）。

| 番号 | 出所 | 深刻度 (Critical/Major/Minor) | 内容 | 根拠 | 推奨アクション |
|---|---|---|---|---|---|

- 「番号」は記帳前に ledger を Read し、既存の最終番号 +1 から採番する (ファイルが無ければ 1 から)。

## polish-before-commit 固有の記帳規則

Orchestrated モード時、以下の 2 箇所は SKILL.md 本文の「ユーザーの明示指示を待つ」「ユーザー承認後に編集」を「escalation ledger に記帳して続行する」に読み替える。

1. **Manual Review Items #4 (dead mock の部分削除)**: 削除せず、書換え候補（残す identifier / 削除する identifier）を「保留」として escalation ledger に記帳する。深刻度は Minor 固定（実装の欠陥ではなく spec 整理判断のため）。
2. **Step 9 (判断申し送りの集約)**: 判断項目が 1 件以上でもユーザーの返答を待たず、Step 9 の一覧（申し送り + Manual Review Items）を escalation ledger にそれぞれ 1 行ずつ記帳したうえで、完了報告して終了する。深刻度は各項目の出所側（review-code-quality 申し送りは quality-ledger 側の深刻度を引き継ぐ、polish 検出の Manual Review Items は Minor 固定）に従う。

いずれの場合も申し送りファイル (`quality-review-handoff.md`) のクリア (Step 9 手順 6) は Orchestrated モードの有無に関わらず実施する（ledger へ転記済みのため stale として残す必要がない）。

## 記帳例

```
| 5 | polish-before-commit | Minor | spec/models/user_spec.rb:88 の receive_messages(a:, b:) 部分削除 (a: のみ) | Manual Review Items #4 | b: を残す書換え案で承認後に編集 |
| 6 | polish-before-commit | Major | app/services/billing_service.rb:42 の認可チェック配置 | Step 9 集約 (review-code-quality 申し送り由来) | before_action :authorize へ統一 |
```
