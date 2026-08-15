# gdocs PRD の凍結

案件開始時と `/build-prototype` 直前に実行する。

1. プランがなければ `<案件dir>/plan_<案件名>.md` を作り、冒頭を次に揃える。URL は doc ID と `tab=` まで残し、`#heading` を除く。取得範囲が URL と異なる場合は範囲行を正とする。

   ```markdown
   # plan: <案件名>
   PRD gdocs: <原URL>
   スナップショット範囲: タブ単体 (t.<tabID>)。子タブ包含: 未確認。経路: curl tab=
   ## 進捗
   ```

   全文なら `スナップショット範囲: 全文 (経路: rclone backend copyid)` とし、子タブ包含句は書かない。目的・実装対象リポジトリ・PRD 所在は `## 進捗` の後ろに別見出しで置く。

2. エクスポートする。

   - 全文: `rclone backend copyid drive: <docID> <案件dir>/ --drive-export-formats md`
   - タブ: `curl -sL -H "Authorization: Bearer <token>" "https://docs.google.com/feeds/download/documents/export/Export?id=<docID>&exportFormat=markdown&tab=t.<tabID>"`
   - token は rclone の OAuth access token をコマンド置換で header へ直接渡す。token 単体の表示、ファイル・環境変数への保存、`rclone.conf` 直接読取、dump 単独実行は行わない。401 は `rclone about drive:` 後に一度再取得し、403 rate limit は待機または rclone へ切り替える。

   統合コマンドが権限 deny なら再試行せず、既知の deny でも直ちに次の順で縮退する。発動理由・日付・経路/範囲の遷移を `## 進捗` に1行記録する。

   `- <日付> 縮退発動: <理由> — curl tab= → rclone 全文 (範囲: タブ単体 → 全文)`

   1. 許可済みなら `scripts/export_gdoc_tab.sh <docID> <t.tabID> <出力先>` を実行する。許可状態は実行結果で判断し、既知の未許可なら実行しない。settings を読まず、agent が許可を追加しない。未許可で対話可能ならユーザーへ `!` 実行を依頼し、対話不能なら次へ進む。成功時の経路名は `curl tab=`。
   2. rclone 全文へ切り替え、他タブを含むことを報告する。対話可能なら範囲変更を確認する。
   3. rclone も不可なら未取得として停止し、完了扱いにしない。

   経路確定と取得完了は別イベントにする。未実行なら別行を残し、この行がある限り凍結済みにしない。

   `- <日付> スナップショット未取得: <理由>。経路は確定済み (<経路>) だが取得は未実行 — 凍結は成立していない`

   `tab=` は指定タブだけを返す。子タブ包含は本文の実在で判定する。タブ単体か子タブ列挙かをユーザーへ一度確認し、対話不能ならタブ単体として欠落リスクを報告する。全文では確認不要。採用した経路・範囲を冒頭の範囲行へ反映し、再取得にも同じ経路・範囲を使う。`tab=` が壊れたら全文へ切り替えて範囲を再確認する。

3. 画像を除いて保存し、生エクスポートを削除する。

   ```bash
   sed -E 's/^(\[image[0-9]+\]): <data:image[^>]*>/\1: (画像データ省略)/'
   ```

   保存名は `prd_gdoc_snapshot_<YYYY-MM-DD>.md`。rclone の共有 client 認証が止まったら組織ポリシーに従う OAuth client (`drive.readonly`) で再認証し、応急時は Google Docs の Markdown download をユーザーへ依頼する。

4. 2回目以降は同じ経路・範囲で新版を一時取得し、画像除去後に既存版と `diff -u` する。

   - 差分なし: 一時版を削除し、`- <日付> 再凍結: 差分なし (基準据え置き)` を記録する。
   - 差分あり: 新版を基準として保存し旧版を削除する。同日名なら `_2` を付ける。プランの `## PRD 差分履歴` に `### <旧日付> → <新日付>` と変更見出し・要旨を1件1行で書き、AC/設計の再判断要否を付記する。進捗へ `- <日付> 再凍結: 差分あり — PRD 差分履歴を参照` を記録する。

5. ユーザーへ gdocs named version の作成と Keep forever を依頼する。取り忘れ時は版履歴から該当版をコピーし Markdown download する。
