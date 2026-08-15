# 観点選択ルール (Step 2 詳細)

## 観点数の規則

- **軸数は SKILL.md の Quantitative scaffolding 表に従う**。
- **複数種別該当時**: 各種別の controlled label から重複を除いたうえで tier 軸数まで絞る (例: api_change + db_change なら `permission` (両方該当) / `req_form` / `data_volume` / `data_compat` … の候補プールから tier 軸数だけ採る。手順は下の「複数主種別・主軸超過時の主軸確定」)

## 主種別 + 副作用軸の追加 (裁量判断)

該当種別の表 3 軸に加えて、プラン本文から派生する独自軸を 1 つ足す形は**裁量判断**。`references/perspectives.md` に既存 label がなければ汎用候補 (`dep_loc` / `layer` / `non_invasive` / `contract`) から選ぶか、新規 label を追加する。分析ファイル `### 検討観点` に「表 N 軸 + 副作用軸 1 (理由)」と明記。

## 複数主種別 + プラン文脈軸の主軸採用

主種別が複数該当 (例: api_change + service_change + db_change) し、かつプラン本文に明示的な文脈軸がある場合、その文脈軸を**副作用軸ではなく主軸**として採用してよい。対象となる文脈軸は 2 種類 — **統制関心** (auth / authz / billing / privacy 等) と**非機能関心** (性能 / 可用性 / コスト 等。例: 「遅い」が主題のプランでは `runtime` を主軸に採る)。

例: auth 記述があれば `permission` を主軸の先頭に置く。

分析ファイル `### 検討観点` に「auth 文脈強調により permission を主軸採用 (副作用軸ではない)」と明記。

## 主軸採用と副作用軸の併用可否

「主軸採用」と「副作用軸 1 つ追加」は**併用可能** (tier 軸数の上限内なら)。

例: 主軸 `permission` + 副作用軸 `observability` で 5 軸構成。`### 検討観点` に「主軸 permission + 副作用軸 observability (理由: ...)」と分けて明記。

## 表に該当する変更種別がない場合

`references/perspectives.md` の「Step B」汎用候補軸から、同節の観測可能条件に合うものを選ぶ。選定根拠を分析ファイルに明記。

## observability 軸の特例

全変更種別で Critical 検出用の追加候補にできる。observability は tier 軸数 (主軸数) にカウントしない。

## 複数主種別・主軸超過時の主軸確定 (Step 2 詳細)

inline 表で完結できるのは Step 1.5 の機械抽出が単一主種別のときのみ。複数主種別が抽出された場合 (例: controller + service の直列実装で api_change + service_change) や主軸候補の数が tier 軸数と一致しない場合は、inline 表の 1 行をそのまま使わず以下の手順で主軸を確定する。各軸の選定理由を分析ファイル `### 検討観点` に 1 文ずつ明記する。

**主軸 / 副作用軸の区別**: 変更種別 → デフォルト観点軸表の該当 type 行に現れた controlled label は **主軸**、Step B 汎用候補軸 (`flag_removal` / `non_invasive` / `dep_loc` / `layer` / `contract` 等) と `observability` は **副作用軸**。副軸を主軸に格上げしない (概念的に cross-cutting に見える table-listed label — 例: `compat` — も主軸のまま)。

**主軸の確定手順** — 軸を増やす方向・減らす方向のどちらも同じ優先度列を使う:

1. **候補プールを作る**: 該当する全 type の表行に現れた label。状況条件付き label (`req_context` / `unsent_keys`) は適用条件を満たすものだけ入れる。`migration` は schema または data migration が plan・差分で観測できる場合だけ入れる
2. **除外する**: plan の不変条件でセルが空 / 自明になる軸 (例: 「auth 不変・誰でも閲覧可」と明示 → `permission`)。**振る舞い不変のリファクタでは全軸が「不変」になるため本手順は適用せず**、plan の変更対象レイヤーが触れない横断機能だけを除外する
3. **優先度列に並べる**: type は plan が主対象として明記した順、明記が無ければ perspectives.md の変更種別表の行順。(a) 各 type から 1 本ずつ — plan 本文が明示した関心 (後方互換 / データ量 / 性能等) に対応する label を優先し、無ければ表の行順で最上位、(b) 残った候補を「plan 明示関心 → 表の行順」で続ける
4. **上から tier 軸数だけ採る**: 候補プール不足なら Step B の観測可能条件に合う軸を同節の順で補充し、理由を書く。超過なら列の下から落とす (type ごとに均等配分する必要はない)
5. **外した関心を拾う**: 手順 2 または 4 で主軸から外した「存在するが不変の横断機能」(既存認可・401/404 の権限判定等) は、非影響確認に regression 1 行を残す

**Cross-cutting behaviors の label**: retry / timeout / circuit-breaker などの cross-cutting 挙動が複数 change-type で出現する場合、変更種別表の特定行に閉じ込めず Step B 汎用候補軸として扱う (例: api_change の同期エンドポイントで「リトライ 3 回」なら `idempotency` を Step B 汎用候補軸として副作用軸採用)。

observability を含める場合の実効上限は SKILL.md の Quantitative scaffolding 表 (canonical) を参照。主種別が 3 種類以上の場合は **副作用軸を 1 つに絞る** (合計が上限を超えるのを避けるため)。
