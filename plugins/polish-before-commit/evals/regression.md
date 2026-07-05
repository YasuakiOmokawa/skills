# regression eval (empirical-prompt-tuning 収束時保存)

収束記録: 2026-06-12 (v3.28.0 PR)。Iter1-3 で fresh executor が全 [critical] ○ / accuracy 100% / retries 0。
用途: **regression 検出器** (capability 改善の信号としては使わない)。本 skill を変更する PR では
fresh executor (blank slate, Task dispatch) で下記シナリオを再実行し、全 [critical] ○ を確認してから merge する。
実行方法は empirical-prompt-tuning の「Subagent invocation contract」に従う (成果物はインライン、ファイル編集禁止)。

## シナリオ: standard tier + 注入非対応 + base=main

「現在の対象 (自動取得)」節が生コマンド文字列のまま。$ARGUMENTS なし。変更 2 ファイル (app/models/user.rb + spec)、規約 hit 1 (コメント原則)、delegate/def 撤去なし、feature-dev INSTALLED、base branch は main。申し送りファイルは存在せず、各 Step の検出結果は違反 0 件とする。実行 Step 列と各 Step の確定レポート文言 (バリアント表準拠) を出させる。

### Requirements checklist
1. [critical] Step 0 (preflight) を最初に実行し `[preflight: feature-dev 導入済み]` を出力
2. [critical] Step 1 (規約の収集) を tier 判定より前に実行する
3. base=main のためフォールバック (b) で BASE_BRANCH=main を特定して diff 取得
4. [critical] Step 9 の後、commit / /create-pr へ自動で進まない。判断項目 0 件なら質問せず「判断項目なし。コミット可能な状態」と完了報告して終了し、1 件以上なら一覧を提示して「コミットへ進めますか?」でユーザーの明示指示を待つ (v0.19.0 で 0 件時の質問を廃止)
5. Step 6 は条件不一致由来のスキップとして Step 固有バリアント文言 (`[dead mock: スキップ (撤去なし)]`) を使う
6. Manual Review Items 4 分類を auto-fix 前に認識している
