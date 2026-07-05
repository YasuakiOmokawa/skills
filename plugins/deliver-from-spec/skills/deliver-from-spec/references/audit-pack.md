# `<plan>.audit-pack.md` 契約

## 置き場・命名

プランファイルと同ディレクトリ、拡張子前に `.audit-pack` を挿入する (例: `feature-xxx.md` → `feature-xxx.audit-pack.md`)。Phase 4 の出荷ゲート通過後 (Critical 0 件確認後) に生成する。Critical が残り出荷ゲートで停止した場合も、現状の可視化のために監査パックだけは生成する。

## 目的

最終監査 (同期タッチの最後の 1 回) が「これだけ読めば済む」1 ファイルにする。人間は個々の台帳ファイルを読み歩く必要がない。

## 収録内容 (6 点)

1. **3 台帳の集計行**: qa-ledger (PASS/FAIL/pending/検証不能/要人間確認/対象外 の件数)、quality-ledger (深刻度×状態の件数)、escalation-ledger (Critical/Major/Minor の件数)
2. **escalated 全行の転記**: escalation-ledger の内容をそのまま貼る (要約しない。人間が個々の判断根拠を検証できるようにするため)
3. **design-review の acceptable 残存リスク**: `<plan>.design-review.md` の内容をそのまま転記する (同ファイルの内部フォーマットは review-design 側の実装に委ねるため、抽出せず全文転記に倒す。これにより review-design 側の書式変更に監査パック生成 Bash が追従する必要がなくなる)
4. **変更サマリー (PR 一覧 + 各 1 行)**: orchestration-status.md の `2-PR*` 行から抽出する
5. **Minor 無作為抽出 n 件 (quality 台帳)**: 全件レビューの代わりに抜き取り校正する (R4 の校正目的、n は既定 2〜3件程度)
6. **トークン消費の概算**: orchestration-status.md のフェーズ遷移行数を概算の代理指標として使う (subagent 起動数の厳密カウントは薄い版のスコープ外、概算で可)

## 生成の検証済み Bash

SKILL.md 本文「監査パック生成」節を参照 (重複掲載しない)。

## design-review.md への依存

3 の内容は review-design が Step 6 の最終レポートを `<plan>.design-review.md` へ保存することに依存する (SKILL.md 冒頭の依存関係の注記を参照)。この保存が無い場合、監査パックの 3 は「design-review.md 未生成」と表示され、人間はチャット上のレビュー結果を別途参照する必要がある。
