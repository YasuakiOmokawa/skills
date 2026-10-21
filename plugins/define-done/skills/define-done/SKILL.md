---
name: define-done
description: 既存の計画を仕様とコードの根拠でレビューし、計画ごとの受け入れ基準と、その検証の対応付けまでを計画に書いて、実装に着手できる状態にする。計画を一から作るときや、計画を実装するときには使わない。
---

## 目的

既存の計画について、何をもって完了とするかを、仕様とコードに根拠付けた受け入れ基準 (AC) とその検証の対応付けとして定め、計画に書く。

## 原理

- 段の順序: 次の 4 段をこの順に行う。各段に入るときにその段の規則を読んで従い、前の段が書いた節を次の段の根拠にする。
  1. 設計境界のレビュー: [references/ground-review.md](references/ground-review.md)
  2. 受け入れ基準: [references/acceptance-criteria.md](references/acceptance-criteria.md)
  3. MECE レビュー: [references/mece-review.md](references/mece-review.md)
  4. 検証の対応付け: [references/verification-plan.md](references/verification-plan.md)
- 止めるのは 4 段目だけ: 1〜3 段の未決の判断、不足情報、範囲外、未検証は、その段の節に書いて次の段へ進む。`## MECE Review` の Gate が ready でなければ、`## Verification Plan` を書かず、Gate の理由と ready にするための不足条件を報告して止まる。既存の `## Verification Plan` の `- AC IDs:` が現在の AC-ID の集合と食い違えば stale と報告する。

## 契約

- 入力: 書き込み可能な既存の計画と、依頼・計画が名指しする仕様とコード。計画が無いか全体を読めないときは何も書かず、その欠陥を報告する。
- 出力: 計画にそれぞれ唯一の `## Ground Review`、`## Acceptance Criteria`、`## MECE Review`、`## Verification Plan`。書式は各段の規則が定める。後続は `## Acceptance Criteria` の AC-ID、`## MECE Review` の `- Gate:`、`## Verification Plan` を読む。
- 最終回答: 段ごとに、書いた節、条件と基準の対応、未決の判断、不足情報、範囲外の項目、未検証の範囲を返し、Gate と書き込みの結果を添える。

## 禁止

- 計画の 4 節以外の行、製品コード、test、設定、外部状態を変えない。見つけた不足を計画本文や製品コードへ自分で反映しない。
- 書き込みに失敗しても、別の保存先へ迂回せず、同じ書き込みを再試行しない。内容は回答で返す。
- 資料が決めていない値と未解決の前提を推測で埋めない。

## 完了条件

4 段を終えるか、4 段目で Gate を理由に止まった。再読取などで確かめていない書き込みを成功と報告しない。書き込みが失敗したら、その内容と計画の状態を報告する。
