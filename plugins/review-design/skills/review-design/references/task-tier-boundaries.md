# Task complexity tier — Row 間の境界規則

SKILL.md "Task complexity tier" の表と Row 1/Row 4 precedence を補完する。territory (Row 4) の判定に迷ったとき、または複数 Row が同時該当するときに参照する。

## Row 3 と Row 4 の compound

両 Row が同時に該当する場合 (例: 新規 module + auth territory) は **superset を採用** — Row 3 の "all 5 reviewers default" と Row 4 の "DA subagent dispatch 強制" を**両方適用**する。reviewer 選択は all 5、DA は subagent (inline ではない)。Row 4 の存在が DA mode を inline → subagent に上書きする。

## Row 4 territory の境界例

territory は「支払実行 / 認証判定 / 権限判定 / 本番 DB 変更 / 秘密情報取扱」の **core path** を指す (= 誤りが金銭的損害・認証境界破壊・データ破損に直結する経路)。周辺・派生機能は Row 4 に含めず Row 3 として扱う: (a) 領収書 / 請求書 / invoice の入力・OCR・表示は billing 領域だが charge / refund / 決済ゲートウェイ呼び出しの core path ではない、(b) ログイン UI のレイアウト調整は auth 領域だが認証判定ロジックの変更ではない、(c) 認可される権限を UI に描画する read-only 表示は permission 領域だが認可判定の追加ではない。判定に迷ったら「この変更で誤ると金銭・認証境界に直接影響するか」を問い、間接的なら Row 3。
