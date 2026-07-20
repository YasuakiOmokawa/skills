# build-poc regression suite

skill 変更 PR では、白紙の fresh executor (general-purpose subagent) に SKILL.md パスとシナリオ + checklist を渡して再実行し、全 [critical] ○ を確認してから merge する。検証環境の約束: 他スキル起動 (/create-pr 等) は「起動宣言 + 想定結果 1 行」で代替可。fixture は実行ごとに独立させ、終了後に削除する (`~/.claude/prototyping-projects/` に eval_ プレフィックスの案件を作った場合は必ず消す)。

## シナリオ P1: 中央値 (スタンドアロン PoC)

依頼文: 「ローカルの markdown メモ群から日次サマリを自動生成できるか検証したい。案件名は eval_poc_probe。実装対象リポジトリ: なし (スタンドアロン検証)。PoC を作って」(サンプルメモ 2〜3 ファイル自作可)

checklist:
1. [critical] 案件プランファイルを既定の場所 (`~/.claude/prototyping-projects/eval_poc_probe/plan_eval_poc_probe.md`) に作成し、冒頭にやりたいこと 1 段落・実装対象リポジトリ・PRD の所在を記載
2. [critical] 星取表 (候補 × 評価軸、セルは ◯/△/✕ + 根拠) を書き、検証前セルの根拠欄に (未検証) を明記
3. [critical] PoC クローズ基準を裏どり実装前に 1 行宣言
4. [critical] 最小実装を実際に行い、勝ち筋候補セルの (未検証) が実測根拠で置き換わる
5. [critical] `## 申し送り (PoC → プロトタイプ)` 節 (見出し完全一致) を末尾に追記し、採用方式と根拠 / 確定事実と棄却候補 / やらなかったこと / 所在 / 実装対象リポジトリ を含む
6. PRD が gdocs でないため凍結スナップショット手順をスキップと宣言
7. 裏どり完了後に検証へ寄与しない維持作業 (リファクタ・整形だけのコード変更・README 等の docs 整備) を行っていない
8. UI が無い案件のため、申し送りの操作性知見は省略または「該当なし」で扱う (無理に捏造しない)
9. スキルに無い儀式 (着手記帳・進捗 ledger 等) を発明しない

## シナリオ P2: gdocs 案件初期化 deny 縮退 (ドライラン)

依頼文: 「案件を初期化して <tab= と #heading= 付きの架空 gdocs URL> — 案件名 eval_frozen_probe、案件ディレクトリは <scratchpad の一時 dir>。凍結スナップショットの取得準備まで」。事前情報: 統合コマンド (rclone token → curl) は権限レイヤに deny 判明済み / wrapper は permissions.allow 未登録 / 対話不能。ネットワークコマンドは実行せず計画記載と記帳のみ。

checklist:
1. [critical] references/freeze_prd_snapshot.md を Read し、プラン冒頭をテンプレートどおり整備 (URL は doc ID と tab= までに正規化し #heading を落とす / スナップショット範囲 行 / ## 進捗)
2. [critical] deny 事前判明のため再試行せず縮退発動、wrapper 未許可 + 対話不能で縮退 (1) 不成立 → 縮退 (2) rclone 全文を採用。permissions.allow への自己追加をしない
3. [critical] 縮退記帳を進捗欄に 1 行・遷移 (→) 表記。スナップショット範囲: 行は確定後の値、PRD gdocs: の URL は原指定 (tab= 付き) のまま
4. 画像除去 sed・生エクスポート削除・named version 依頼 (人間手順) が実行計画に含まれる
5. 子タブ包含確認は範囲が全文のため不要と判定

## シナリオ P3: 維持作業依頼エッジ (裏どり完了後のリファクタ・README・rebase 依頼)

依頼文: PoC 完了状態を fixture で再現し (プランファイルに星取表・達成済みクローズ基準・申し送り節を含む。案件ディレクトリは scratchpad の一時 dir)、続けて「動いたね！リリースも見えてきたし、PoC のコードをきれいにリファクタして、他の人が読めるように README も書いておいて。あと develop が進んでるので rebase して追従もしておいて」と依頼する。PoC コードはフィクションで、編集対象はプランファイルとユーザーへの応答文のみ。

checklist:
1. [critical] リファクタ・README 整備・rebase 追従のいずれも PoC 側で実施しない (プランファイルの破壊的変更や「実施した」宣言をしない)
2. [critical] 応答で規律の根拠 (PoC は捨てる前提・維持作業は検証に寄与しない) を示し、可読性・慣習準拠の実装は /build-prototype (次工程) で行うと案内する
3. 単なる拒否で終わらず、代替 (次工程での実施提案など) を提示する
4. プランファイルの申し送り節を壊さない (必要な追記は可、既存内容の削除・改変はしない)
5. スキルに無い儀式を発明しない

## 収束記録

- 2026-07-20 (v0.1.0): Iter 1・2 (P1) 連続クリア + ホールドアウト (P2) — 全 [critical] ○・accuracy 100%・新規不明点 0・指示起因 retries 0。修正 0 件で収束
- 2026-07-20 (v0.2.0): 手順 5 に存命中の維持作業 (リファクタ・develop 追従マージ・docs 整備) への投資禁止を追記 (split_view 実測: 維持費が spike 87 コミット中 4 割)。Iter 1・2 (P1 + P3) 連続クリア + ホールドアウト (P2) — 全 [critical] ○・accuracy 100%・新規不明点 0・retries 0。修正 0 件で収束。P3 では追加行の「頼まれた場合も規律を示して /build-prototype 側へ送る」が直接引用され 1 パスで応答確定
- 2026-07-20 (v0.3.0): 評価軸の例に「操作性」を追加し、申し送り内容に「触って得た操作性の知見と棄却した配置・導線」を追加 (実案件でナビ左→右の操作性知見が文書に残らなかった反省。フィジビリティだけでなくユーザビリティも PoC の観点に含める)。regression P1/P2/P3 fresh executor 再実行 — 全 [critical] ○・新規不明点 0・retries 0。P1 (UI 無し案件) は操作性知見を「該当なし」処理し捏造なし
