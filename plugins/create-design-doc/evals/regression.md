# create-design-doc regression suite

skill 変更 PR では、白紙の fresh executor (general-purpose subagent) に SKILL.md パスとシナリオ + checklist を渡して再実行し、全 [critical] ○ を確認してから merge する。検証環境の約束: 他スキル起動 (/dry-ssot-text 等の品質パス、/map-user-stories 等) は「起動宣言 + 想定結果 1 行」で代替可。

## fixture (実行ごとに独立構築し、終了後に削除)

- `case/plan_<案件名>.md`: 冒頭メタ + 星取表 + `## 申し送り (PoC → プロトタイプ)` + `## 申し送り (プロトタイプ → DD)` (所在 / 従った慣習 / 設計判断と根拠 + 採らなかった案 / PoC から変えた点 / スコープ外)
- `case/prototype/`: 慣習準拠の完成形イメージの小スクリプト + 1 行 README
- `~/.claude/skills-config/create-design-doc/` は**未配置のまま**にする (テンプレ欠如フォールバックが検証対象)

## シナリオ D1: 中央値 (テンプレ欠如)

依頼文: 「<案件名> の DD を作って」(案件ディレクトリを提示)

checklist:
1. [critical] `## 申し送り (プロトタイプ → DD)` 節とプロトタイプ成果物を読んでから DD を作成
2. [critical] DD テンプレート未配置を検出し「テンプレートなしで作成」と宣言して進行 (エラー停止・差し戻しなし)
3. [critical] DD に設計判断と根拠が転記され、採らなかった案が Did not adopt として残る
4. 文章品質パス 3 スキルの適用 (宣言代替可)
5. [critical] DD 完成後 (人間: DD レビュー → LGTM) で停止し、タスク分解・Jira 起票など後続工程へ勝手に進まない

## 収束記録

- 2026-07-20 (v0.1.0): Iter 1・2 (D1) 連続クリア — 全 [critical] ○・accuracy 100%・新規不明点 0・retries 0。修正 0 件で収束
