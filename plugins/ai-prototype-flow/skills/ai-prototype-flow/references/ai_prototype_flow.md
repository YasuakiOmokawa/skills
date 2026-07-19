# AI プロトタイプ駆動開発フロー

## 案件初期化: PRD 凍結スナップショット (gdocs 正本の案件)

PRD の正本が Google Docs の案件で、案件開始時とフェーズ2 入り時 (凍結の基準時点) に実行する。
再入時の差分は「スナップショット vs 現在」の diff で抽出するため、これが無いと
変更前 PRD を後から再構築する羽目になる (実案件での手戻りの前例あり):

1. プランファイルが無ければ作成し (命名は SKILL.md「用語の既定」に従う。
   gdocs 正本案件の既定 = 案件ディレクトリ直下の `plan_<案件名>.md`)、冒頭を
   次のテンプレートに揃える (見出し行の直後に記録する。URL は doc ID と `tab=`
   までに正規化し `#heading=...` は落とす。
   `?tab=t.<tabID>` はスナップショット範囲の指定を兼ねる):

   ```
   # plan: <案件名>
   PRD gdocs: <URL>
   スナップショット範囲: タブ単体 (t.<tabID>)。子タブ包含: 未確認。経路: curl tab=
   ## 進捗
   ```

   全文を凍結する場合は `スナップショット範囲: 全文 (経路: rclone backend copyid)`
   と書く (全タブ包含済みのため「子タブ包含」句は書かない)。見出しの `<案件名>` はディレクトリ名と同一で
   よい (説明句の付与は任意)
2. エクスポートする。URL にタブ指定が無ければ
   `rclone backend copyid drive: <docID> <案件ディレクトリ>/ --drive-export-formats md`
   で全文を取る。タブ指定があれば指定タブを取る:
   `curl -sL -H "Authorization: Bearer <token>" "https://docs.google.com/feeds/download/documents/export/Export?id=<docID>&exportFormat=markdown&tab=t.<tabID>"`
   - token は rclone が保持する OAuth access_token (`rclone config dump` の drive
     セクション) を使い、コマンド置換で curl のヘッダに直接渡す。token 単体を
     表示・ファイル・環境変数に出す中間ステップを作らない (secret 衛生。
     `rclone.conf` の直接読取や dump の単独実行も同じ理由で不可 — 2026-07-11 実測)。
     401 は `rclone about drive:` を一度実行して refresh 後に再取得、403
     rateLimitExceeded は時間をおいて再試行するか rclone 経路へ切替える
   - この「rclone token を curl に転用する」統合コマンド自体が、実行環境の
     権限レイヤ (auto mode classifier 等) に credential 転用として deny されうる —
     2026-07-19 実測 (subagent への委譲もプロンプト文面によらず deny)。ガード回避を
     目的とする説明はコマンドにも委譲プロンプトにも書かない — deny は回避せず、
     以下の縮退で受ける。
     deny されたら同コマンドを再試行せず、次の順で縮退する (事前に deny が判明して
     いる場合も同じ縮退を発動する — 確認のための再実行はしない。各段は前段が
     使えない・不成立のとき発動。縮退を発動したら理由と日付を進捗欄に 1 行記帳。
     取得前に縮退先が確定している場合、プランの記録は確定後の経路・範囲で書く):
     (1) ユーザーが settings に許可済みの wrapper スクリプトがあればそれを実行する
     (許可ルールは事前のユーザー同意なので対話不能でも使える)。無ければ、
     対話可能ならユーザーに `!` プレフィックスでの自己実行を依頼する。
     この段で成功しても記録する経路は `curl tab=` のまま (実行主体は経路に
     含めない)
     (2) (1) が不可・不成立 (委譲実行等の対話不能を含む) なら rclone 全文経路へ
     切替え、スナップショット範囲が全文へ変わる旨と他タブ・子タブ混入の注意を
     報告に残す (対話可能なら切替前に範囲変更を確認する)
     (3) rclone 経路も不可ならスナップショット未取得として明示停止し報告する
     (完了扱いにしない)
   - **`tab=` が返すのは指定タブ単体のみで、子タブは含まれない** (2026-07-11 実測:
     画像除去後で親タブ単体 24KB・子タブ込み区間 121KB。検証に使った doc での参考値で
     あり閾値ではない)。子タブ欠落の判定はサイズではなく「見出しに対して本文が
     実在するか」で行う。
     (人間: 凍結範囲はタブ単体か、子タブ込み (子タブの tab ID を URL から列挙して
     もらい個別取得して連結) かを 1 回確認 — 確認できない委譲実行等ではタブ単体を
     既定とし、子タブ欠落の可能性を報告に残す)
   - 採用した経路と範囲 (タブ単体 / 子タブ列挙 / 全文) はプランファイルの
     `スナップショット範囲:` 行に記録する (書式は手順 1 のテンプレート)。
     再入時の再取得は必ず同じ経路・同じ範囲で行う (経路や範囲が混在すると、
     範囲差がそのまま偽の diff になる)。`tab=` は非公開パラメータ — 壊れたら
     全文エクスポートへ切替え、凍結範囲をユーザーに確認し直す
3. 画像定義行を
   `sed -E 's/^(\[image[0-9]+\]): <data:image[^>]*>/\1: (画像データ省略)/'`
   で除去して `prd_gdoc_snapshot_<日付>.md` (日付は YYYY-MM-DD) として保存する。生エクスポートは削除する
   (画像は gdocs 側の named version で保全。2026-07-11 実測: 全文 3.6MB → 217KB、
   タブのみ 214KB → 24KB。見出し・表は崩れない)
   - rclone 共有 client_id は 2026 年中廃止予定の NOTICE が出る。認証が止まったら、
     自組織のポリシーに従って自前の OAuth クライアント (scope は drive.readonly、
     Drive API と Docs API を有効化) を用意し、client_id/secret を
     `rclone config update drive` に設定して再認証する。
     応急処置は gdocs の File > Download > Markdown 手動エクスポート
4. (人間: gdocs 側に named version を打ち Keep forever を付ける — 版は 30 日または
   新 100 版で消えうる。スナップショット取り忘れ時のフォールバック =
   版履歴から該当版をコピー → File > Download > Markdown)

## フェーズ0: 技術調査 (候補出しまで)

技術候補を比較し、リスクを列挙して、調査結果をフェーズ1 の仮説 ledger の入力に
まとめて。このフェーズはここまで — 確定は spike に譲る
(実案件で調査結果の誤り 3 点を spike が訂正した。調査は仮説の候補リストであり結論ではない)

## フェーズ1: PoC (使い捨て検証・速度優先)

prd から poc をつくりたい。/iterate-with-prototypes に従い、検証したい仮説を
「主張 / 検証方法 / kill 条件」の ledger にしてから spike して。
(使い捨て前提のため AC/MECE/finalize のフル計画装備はこのフェーズでは省略する —
作業項目ではなくスコープの注記)

/extract-figma-spec で figma design をソースコードに反映して   # 条件: Figma 再現度が検証対象の仮説に含まれる場合のみ (判定は仮説 ledger 確定後に行う)。非該当ならスキップと宣言

/qa-ui を automation で実行して   # Figma 条件とは独立に実行する (リポジトリなし等の非該当規則は別途適用)

仮説 ledger の各項目を grounded / killed / unverified で確定し、
「やらなかったこと」を列挙してプランファイルに記録して

PoC レビューは人間が行う。レビューで出た新しい要望・仮説をユーザーが伝えたら、
ledger に行を追加して同ブランチで追加 spike する (これは停止点ではなく常設ルール —
ユーザーが要望を伝えた時のみ発火する。フェーズ1 内で完結させる。
例: 入力内容のリアルタイムプレビュー)

PoC のクローズ基準は ledger 確定と同時に宣言する: 仮説 ledger の全項目が
grounded / killed で確定した時点で PoC ブランチは役割終了 — 以後コミットを足さない
(上の常設ルールの追加 spike は「新しい仮説」が出た時だけ発火する。PRD / Figma の
仕様変更は仮説ではない — 再入ルール「PRD / Figma が凍結前に動いた」で文書に受ける)。
後から技術仮説が出た場合も長寿命化した PoC ブランチを延命せず、その 1 点だけの
短命 spike を別に切る
(理由: 実案件で PoC を約 6 週間生かし続けた結果、87 コミット中 feasibility 検証は
20% のみ、残りは仕様追従・develop 追従マージ 18 回・docs 維持に流れた。
基準の事前宣言が無いと PoC は「動く仕様の鏡」に変質する)

/create-pr    # draft。タイトル先頭に [DONOTMERGE]、本文冒頭にも「merge しない参照用」と注記

## フェーズ2: 設計確定 (DD 用)

PRD の正本が gdocs の案件は、フェーズ2 入り時点のスナップショットを冒頭の
「案件初期化」節の手順で取る (案件初期化時に取得済みでも、フェーズ2 入りが凍結の
基準時点なので日付違いで取り直す。以後の再入 diff はこの版を「変更前」とする)

PoC の仮説 ledger (grounded/killed) と「やらなかったこと」各項目 → 対応先
(ADR / AC / 後続チケット) のマッピング表を作って、本実装設計の入力にして

固めた prd と PoC の学びを参考に本実装を設計。既存コードベースの慣習に従うよう設計して /grill-with-docs
/review-design

カレントブランチから新しくきって、設計書を /express-intent-in-code のガイドラインに
したがって実装。コミットは指示があるまで実施しない

/simplify
/vercel-react-best-practices
/vercel-composition-patterns
! npx react-doctor@latest --verbose --diff   # 指摘があれば修正してから /polish-before-commit へ (指摘は polish の集約対象)
/review-code-quality
/express-intent-in-code
/polish-before-commit
コードコメントと、今回の実装で変更・新規作成した md ファイルに /dry-ssot-text → /purge-private-vocab → /cognitive-rhythm-writing

/create-pr    # draft。DD 確定用

## フェーズ2.5: DD 作成 → タスク分解

DD テンプレート (`~/.claude/skills-config/ai-prototype-flow/dd_template.md` —
セットアップスクリプトで配置。未配置なら「テンプレートなしで作成」と宣言して進める)
とプロトタイプ PR に従い、DD 作成
参考: `~/.claude/skills-config/ai-prototype-flow/dd_reference.md` (完成 DD の実例。未配置ならスキップ)

DD に /dry-ssot-text → /purge-private-vocab → /cognitive-rhythm-writing   # レビュー依頼前に plan 造語を除染

(人間: DD レビュー → LGTM)

/map-user-stories で US / タスクに分解    # 出荷が複数 PR に跨るときのみ。1 タスク ≒ 1 vertical slice ≒ 1 PR
/create-jira-issues で Jira へ一括登録    # チケット運用するなら

## フェーズ3: 出荷実装 (2.5 で分解したタスクごとに 1 周まわす)

全スライスの進捗は progress-ledger (`<prd>.progress-ledger.md`) に追記して追跡する。
スライスの状態は 未着手 / 実装中 / QA中 / PR済 / 完了 の 5 値。/create-pr を終えた
時点では PR済 と記帳し、完了 はマージ確認後に更新する。
フル装備 (AC→MECE→finalize) は重篤度の高いスライスに限る。
重篤度の判定は /define-acceptance-criteria のリスク領域基準を流用する
(auth / billing / payment / DB migration / security config を含むスライスは規模によらずフル装備)。軽微なスライスは
AC/MECE/finalize を省略し、DD 該当タスクを転記した簡易プラン → 実装 →
/review-plan-diff → /qa-ui → 品質パス (下の /simplify から「コードコメントと
md ファイルに…照合」の行までのブロック) → /create-pr の fast path でよい
(この列挙が fast path の全工程。列挙に無い行 — 出荷用プラン作成行や
/finalize-plan 直後のプラン照合行 — は実施しない)

DD と該当タスクをもとに出荷用プランファイルをつくって /grill-with-docs
/define-acceptance-criteria
/mece-plan-review
/finalize-plan
/dry-ssot-text → /purge-private-vocab → /cognitive-rhythm-writing

プランファイルを /express-intent-in-code のガイドラインで実装。コミットは指示まで禁止
/review-plan-diff
/qa-ui

/simplify
/vercel-react-best-practices
/vercel-composition-patterns
! npx react-doctor@latest --verbose --diff   # 指摘があれば修正してから /polish-before-commit へ (指摘は polish の集約対象)
/review-code-quality
/express-intent-in-code
/polish-before-commit
コードコメントと、今回の実装で変更・新規作成した md ファイルに /dry-ssot-text → /purge-private-vocab → /cognitive-rhythm-writing

/create-pr    # 正式な出荷 PR (ready for review)

## 再入ルール (フロー外イベントの戻り道)

直列に 1 回流れる案件は存在しない。実案件で工数を食ったのは以下の
イベントで、いずれもフローの欠陥ではなく外部イベント。起きたら定義済みの場所に戻る。

- **PRD / Figma が確定後に動いた**: 差分設計 (差分の D 分類 + 決定の K 記録。
  dd_prd_delta 型) を作ってフェーズ2 に再入する。実装済みブランチへの取り込みは
  この差分設計を正とする。PRD 改訂 23 件・Figma 確定遅れによる再作業 4 点の前例あり
  (差分設計の実例: `~/.claude/skills-config/ai-prototype-flow/dd_prd_delta.md` —
  セットアップスクリプトで配置。未配置ならスキップ)。
  フェーズ2 再入時の読み替え: 冒頭の「PoC 仮説 ledger のマッピング表」ステップは
  差分設計で置換し、「カレントブランチから新しくきって」は適用せず取り込み先
  ブランチへ直接実装する。フェーズ2 冒頭のスナップショット取得行は、再入 diff 用に
  取得した現時点エクスポートで代替する (同じものを二度取得しない)。
  他のステップはそのまま実行する。取り込み先ブランチに
  既存の draft PR があれば /create-pr は新規 PR を作らず追記コミットとする
  (既存 PR の有無は開始時の不足入力確認に含める)。差分設計の保存先は案件
  ディレクトリ直下の `dd_prd_delta.md` (再入が複数回なら `dd_prd_delta_<日付>.md`。
  この命名以外を使わない — 過去の実案件で 2 回目が `design_fix_apply.md` と揺れ、
  再入の追跡が壊れた)。PRD 正本が gdocs の案件の差分抽出は、フェーズ2 冒頭の
  凍結スナップショットと現時点エクスポート (取得手順・経路・範囲は凍結時と同じ)
  の `diff -u` を D 分類の入力にする (gdocs 正本は上書きしない)。現時点
  エクスポートは一時ファイルにせず `prd_gdoc_snapshot_<日付>.md` として案件
  ディレクトリに保存する (diff の再現と監査の証跡。次回再入の凍結版にもなる)
- **PRD / Figma が凍結前 (フェーズ2 入り前) に動いた**: コードには当てない。
  変更は文書 (仮説 ledger への注記か差分メモ) にだけ記録し、コードへの適用は
  フェーズ2 以降の本実装で 1 回だけ行う。技術リスクを伴う変更のみ仮説として
  短命 spike で検証してよい (理由: 実案件の実測で、凍結後の Figma 変更は
  本実装への +141 行の小 PR で済んだ一方、凍結前の同種変更は PoC 追従 14 コミット +
  連動 docs 13 コミットを消費し三重払い — PoC 追従 + DD 更新 + 本実装で再実装 —
  になった)
- **実装中に未知のサブ問題が浮上した** (例: 外部由来データに必須属性が欠けた項目):
  その 1 点だけフェーズ1 (spike + 仮説 ledger) に戻す。検討して却下した方式は
  削除せず「方式 B に置換済み。検討記録として残す」と冒頭に明記した文書で保存する
- **品質の対症 (可読性リファクタ等) が要る**: 「構造の作り直しが必要か、地図
  (ドキュメント) の欠如か」を先に切り分け、独立の設計文書 + /define-acceptance-criteria
  で AC 化してから直す (実案件の前例あり)
- **文書の正本管理**: 正本は `<name>.latest.md` に固定し、旧版側は以後編集しない。
  残す場合は旧版の冒頭に「旧版。正本は <実ファイル名>.latest.md」と
  実ファイル名へ展開して明記する
  (正本と旧版の更新時刻が逆転し、どちらが正か確定できない事故が実際に起きた)。
  取り違えで新しい内容が旧版側にだけ入っていた場合は、先にその内容を `.latest` へ
  統合してから旧版に注記する (どちらの版の本文も失わせない)

再入を完了したら `<prd>.progress-ledger.md` の `## 再入ログ` 節に
`- <日付> 再入(<イベント>)→フェーズ<N> 完了: <要点 1 句> / 参照: <差分設計等のファイル名>`
を 1 行追記する。戻り先フェーズを持たない運用ルール項目 (正本管理等) は
`→フェーズ<N> 完了` を `→<項目名> 適用` (例: `→正本管理 適用`) と読み替え、
参照欄には差分設計ファイルの代わりに適用先ファイル名を書く
(複数ならカンマ区切りで列挙)。台帳・節が無ければその場で作る。記帳先をここ以外 (プランファイル・
主文書) に分散させず、記帳は差分設計ファイルを保存するのと同じ作業項目で行う
(実案件では再入 2 回がいずれも未記帳だった。事後の善意任せでは残らない)。
