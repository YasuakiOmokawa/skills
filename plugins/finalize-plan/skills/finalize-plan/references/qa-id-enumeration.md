# QA-ID enumerate 仕様 (Step 1.7)

## 背景

manual-qa-planner と auto-qa-planner は当初それぞれ独立に AC を分類していたため、同じ分類処理が 2 回走り、両 planner の分類結果が食い違うリスクもあった。main agent が事前に 1 回だけ enumerate して両 planner に共通入力として渡す形に変更している。

## ID 採番ルール

`${AC_CONTENT}` の各 `- [ ]` 項目を以下の prefix で連番付与する:

```
正常系:       QA-H-01, QA-H-02, ...  (Happy path)
異常系:       QA-E-01, QA-E-02, ...  (Error)
エッジケース: QA-D-01, QA-D-02, ...  (eDge case)
非影響確認:   QA-R-01, QA-R-02, ...  (Regression)
[MECE追加]:   QA-M-01, QA-M-02, ...  (Mece)
```

## 0 件カテゴリの扱い

該当 AC が 0 件のカテゴリは **QA-ID を発行しない** (例: 非影響確認 0 件なら QA-R-* は生成しない)。ただし Step 3 出力テンプレでは対象 AC 行に `非影響0` のように件数だけは必ず表記する。「カテゴリごと省略」は読み手が「忘れた」のか「該当ゼロ」のか区別できないため禁止。

## 生成例 (${ENUMERATED_QA_AC})

```
- QA-H-01 (正常系): req_form: 本人が PATCH /api/users/123 → 200 OK
- QA-H-02 (正常系): permission: 管理者が PATCH /api/users/123 → 200 OK
- QA-E-01 (異常系): req_form: 本文なしで PATCH → 400 Bad Request
- QA-D-01 (エッジ): permission [境界値: 未ログイン]: PATCH /api/users/:id → 401
- QA-R-01 (非影響): /api/health が変更前と同じ挙動
- QA-M-01 ([MECE追加]): observability: 監査ログに変更前後の差分が記録される
```

両 planner には「自前で再分類しない、main agent の分類結果を信頼」と明示する。

## Step 1.7 失敗時の fallback

- **AC セクションが空 / 全項目分類不能** → AskUserQuestion で「AC が分類できません。`/define-acceptance-criteria` を再実行するか、AC を手動で正常系/異常系/エッジ/非影響/[MECE追加] にラベル付けしてください」と確認する
- **一部 AC のみ不明** → 不明項目を `QA-X-NN` で enumerate し、両 planner に「QA-X-* は分類不能、推測してフォロー + Self-report 明示」と注釈付与する
