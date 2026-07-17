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

## 複数主種別・主軸超過時の主軸確定 (Step 2 詳細)

inline 表で完結できるのは Step 1.5 の機械抽出が単一主種別のときのみ。複数主種別が抽出された場合 (例: controller + service の直列実装で api_change + service_change) や主軸候補が tier 軸数を超える場合は、inline 表の 1 行をそのまま使わず、以下の deterministic classifier とドロップ規則で主軸を確定する。選定理由を分析ファイル `### 検討観点` に 1 文ずつ明記する。

**主軸 / 副作用軸の deterministic classifier**: 変更種別 → デフォルト観点軸表の該当 type 行に現れた controlled label は **主軸**、Step B 汎用候補軸 (`flag_removal` / `non_invasive` / `dep_loc` / `layer` / `contract` 等) と `observability` は **副作用軸**。複数主種別共存時は各 type の最も中心的な 1 label を 1 主軸として採用 (= 副軸格上げ禁止)。

**主軸候補が tier 軸数を超える場合の deterministic ドロップ**: (1) plan の不変条件からセルが空 / 自明になる軸を先にドロップ (例: 「auth 不変・誰でも閲覧可」と明示 → `permission` をドロップ)。**存在するが不変の横断機能** (既存認可など) をドロップした場合は、非影響確認に regression 1 行を必ず残す、(2) plan 本文で明示された関心 (後方互換 / データ量等) に対応する軸は優先的に残す、(3) なお超過するなら表の行順 (上位種別優先) で決める。**tie-break で主軸をドロップした場合も、規則 (1) と同様にドロップされた関心 (401/404 の権限判定等) を非影響確認に regression 1 行として補完する** (規則 (1) は「plan の不変条件で空セル化」、規則 (3) は「主軸数超過」を根拠にする違いはあるが、いずれも主軸から外した cross-cutting な関心を非影響確認で拾う扱いは共通)。table-listed label は概念的に cross-cutting に見えても主軸 (例: `compat`) であり副軸格上げ禁止。

**Cross-cutting behaviors の label**: retry / timeout / circuit-breaker などの cross-cutting 挙動が複数 change-type で出現する場合、変更種別表の特定行に閉じ込めず Step B 汎用候補軸として扱う (例: api_change の同期エンドポイントで「リトライ 3 回」なら `idempotency` を Step B 汎用候補軸として副作用軸採用)。

observability を含める場合の実効上限は **6 軸** (主軸 5 + observability 1)。主種別が 3 種類以上の場合は **副作用軸を 1 つに絞る** (合計が上限を超えるのを避けるため)。
