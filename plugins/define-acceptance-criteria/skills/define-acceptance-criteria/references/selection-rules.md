# 観点選択ルール (Step 2 詳細)

## 観点数の規則

- **下限 3 / 上限 5** (3 未満ではマトリクスが痩せすぎ、5 超では管理負荷が爆発)
- **複数種別該当時**: 各種別の controlled label から重複を除き 3-5 個に絞る (例: api_change + db_change で `permission` (両方該当) + `req_form` + `data_volume` + `data_compat` の 4 軸)

## 主種別 + 副作用軸の追加 (裁量判断)

該当種別の表 3 軸に加えて、プラン本文から派生する独自軸を 1 つ足す形は**裁量判断**。`references/perspectives.md` に既存 label がなければ汎用候補 (`dep_loc` / `layer` / `non_invasive` / `contract`) から選ぶか、新規 label を追加する。分析ファイル `### 検討観点` に「表 N 軸 + 副作用軸 1 (理由)」と明記。

## 複数主種別 + プラン文脈軸の主軸採用

主種別が複数該当 (例: api_change + service_change + db_change) し、かつプラン本文に明示的な文脈軸 (auth / authz / billing / privacy 等) がある場合、その文脈軸を**副作用軸ではなく主軸**として採用してよい。

例: プラン本文に「管理者のみ」「本人不可」等の auth 記述があるなら `permission` を主軸として 4 軸の先頭に置く。

分析ファイル `### 検討観点` に「auth 文脈強調により permission を主軸採用 (副作用軸ではない)」と明記。

## 主軸採用と副作用軸の併用可否

「主軸採用」と「副作用軸 1 つ追加」は**併用可能** (3-5 個の上限内なら)。

例: 主軸 `permission` + 副作用軸 `observability` で 5 軸構成。`### 検討観点` に「主軸 permission + 副作用軸 observability (理由: ...)」と分けて明記。

## 表に該当する変更種別がない場合

`references/perspectives.md` の「Step B」汎用候補軸から選ぶ。裁量判断であることを分析ファイルに明記。

## observability 軸の特例

全変更種別で**追加候補**として考慮可能。Critical 検出力を上げるための共通軸 (mece-plan-review の Red Team が `observability` お見合いで Critical 検出することがあるため、define-AC 段階で取り込むと精度↑)。observability は上限 5 にカウントしない (追加候補)。
