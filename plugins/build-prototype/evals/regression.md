# build-prototype regression suite

skill 変更 PR では、白紙の fresh executor (general-purpose subagent) に SKILL.md パスとシナリオ + checklist を渡して再実行し、全 [critical] ○ を確認してから merge する。検証環境の約束: 他スキル起動 (/create-pr, /review-design 等) は「起動宣言 + 想定結果 1 行」で代替可。

## fixture (実行ごとに独立構築し、終了後に削除)

- `repo/`: remote 未設定の小さな git repo (main + initial commit)。README に慣習を明記 (bin/ 1 機能 1 実行ファイル / snake_case / `tests/run_tests.sh` smoke)。見本 `bin/list_notes.sh` と `tests/run_tests.sh` (現状 PASS) を同梱
- `case/plan_<案件名>.md`: 冒頭メタ (やりたいこと / 実装対象リポジトリ = repo の絶対パス / PRD: なし) + 星取表 + (B1 のみ) `## 申し送り (PoC → プロトタイプ)` 節
- `case/poc/`: 慣習に反する荒い PoC スクリプト (キャメルケース・ハードコードパス)
- `notes/`: サンプルメモ 3 ファイル

## シナリオ B1: 中央値 (申し送りあり)

依頼文: 「<案件名> の PoC ができたので、プロトタイプにして」(案件ディレクトリと notes のパスを提示。repo は remote 未設定であることを実環境の制約として伝える)

checklist:
1. [critical] `## 申し送り (PoC → プロトタイプ)` 節を読んで開始し、追加質問なしで進行
2. [critical] 対象リポジトリの慣習を実ファイルで確認し、従う対象を宣言
3. [critical] 開発基準ブランチから新ブランチを切り、PoC のコピーでなく慣習準拠の書き直しとして実装 (キャメルケース・ハードコードパス残存なし)
4. `bash tests/run_tests.sh` が新スクリプトを含めて PASS
5. [critical] `## 申し送り (プロトタイプ → DD)` 節 (見出し完全一致) を末尾に追記し、所在 / 従った慣習 / 設計判断と根拠 (採らなかった案含む) / PoC から変えた点 / スコープ外 を含む
6. remote の無い repo で PR 作成を適切に処理 (push を試み続けず、状況を宣言して省略・代替)
7. PRD が gdocs でないためスナップショット再取得を適切にスキップ

## シナリオ B2: エッジ (申し送り節なしフォールバック)

B1 と同じ fixture 構成だが、プランファイルに申し送り節が無い (星取表と PoC メモが本文中に散在)。

checklist:
1. [critical] 節の欠如を検出し、エラー停止・過剰質問せず、PoC 成果物と会話から同じ項目 (採用方式・確定事実・やらなかったこと・実装対象リポジトリ) を自分で整理してから開始
2. [critical] 整理した内容を出所付きで明示的に宣言
3. 対象リポジトリの慣習を実ファイルで確認し、従う対象を宣言
4. [critical] 新ブランチ上で慣習準拠の書き直し実装を行い、`bash tests/run_tests.sh` が PASS
5. [critical] `## 申し送り (プロトタイプ → DD)` 節 (見出し完全一致) を末尾に追記

## 収束記録

- 2026-07-20 (v0.1.0): Iter 1・2 (B1・B2) 連続クリア — 全 [critical] ○・accuracy 100%・新規不明点 0・retries 0。修正 0 件で収束
