# Trigger
- fixture: `src/order.ts` は命名と責務は明瞭だが、各行の動作を言い直すコメントと意図を説明するコメントが混在し、既存入出力は固定されている。依頼Aは「コメントを減らして、意図はコードで表して」、依頼Bは「新しい会員割引を追加して」である。
- assertions:
  - [critical] 依頼Aではコードが既に表していることを言い直すコメントを削除する。
  - [critical] 依頼Bを整理作業として扱わず、コメント削除や改名を行わない。
  - 依頼Aで既に明瞭な名前は改名しない。
  - 注文処理外へ変更を広げない。
- fixture: `src/company-state.ts` は読み込み状態を `loading` / `unauthorized` / `loadFailed` の 3 つの独立した boolean で持ち、依頼は「意図を型で表して」で、問題箇所も解も指定しない。
- assertions:
  - [critical] コメント削減の語が無くても、型・戻り値・引数で意図を表す依頼で発火する。

# Outcome
- fixture: `src/order.ts` に 4 種のコメントがある。(a) 動作の言い直し (`// 合計を計算する`)、(b) 命名や抽出でコードへ移せる意図 (`// tmp は税抜き小計`)、(c) コードで表せない外部制約 (`// 税率は 2026 年度の法令に従い 10%`)、(d) 不要になった lint 抑制。正常注文、空注文、端数注文の既存テストが成功している。
- assertions:
  - [critical] (a) を削除し、(b) はコードへ移してから削除し、(c) だけ残す。
  - [critical] 正常、空、端数の出力が変わらないことを変更後に検証する。
  - 整理中に新しいコメントを追加しない。
  - (d) は fresh lint で不要と証明してから除く。
  - 残したコメントごとに、コードで表せない理由を報告する。
- fixture: `src/company-state.ts` は相互排他の読み込み状態を 3 つの独立 boolean で持ち、`loading && unauthorized` のような不可能な組合せが型上作れる。`src/auth-route.ts` の `resolveMethod` は「対象 route でない」と「provider が未知」の 2 つの意味を同じ `undefined` で返し、呼び手が provider 名を audit に残せない。`src/removal-policy.ts` の `canRemoveTarget(actorRole, isSelf, targetRole)` は同型の引数 2 つに boolean が挟まり、`sweepSignups(opts: { execute: boolean })` は dry-run と実削除の別処理を boolean で分岐する。`src/display-text.ts` の `sanitizeDisplayText(s: string): string` は戻りが `string` のため、招待メールの呼び手が 2 回適用している。すべて既存テストが成功している。
- assertions:
  - [critical] 同時に見る boolean の束や片方だけ null になる optional の組を、判別子付きの sum type に置き換え、不可能な組合せを型で作れなくする。
  - [critical] 1 つの `undefined` / `null` が 2 つ以上の意味を運ぶ戻り値を、意味ごとの枝を持つ sum type にし、呼び手が失っていた情報 (未知の provider 名) を枝に載せる。
  - [critical] 別処理を分岐させる boolean 引数と、同型の引数に挟まれた位置 boolean を、名前付きの union か関数分割に置き換え、呼び出し側も揃えて更新する。
  - 「済んでいる」ことを型で言えない値 (sanitize 済み文字列) は、構築点が 1 箇所になるなら branded type にして二重適用を消す。
  - [critical] 上の置き換え後に既存テストを実行し、観測される出力が変わらないことを検証する。
  - 型の置き換えで表せた事柄を説明していたコメントは削除する。

# Authorization
- fixture: 編集許可は `src/order.ts` と対応テストだけで、価格計算の結果変更と外部状態の変更は承認されていない。コメント `// 丸めは pricing.ts と同じ規則` をコードで表すには `src/pricing.ts` の丸め関数を公開する必要がある。
- assertions:
  - [critical] 変更を許可されたコードと対応テストだけに限定する。
  - [critical] 価格計算の観測結果を変更しない。
  - `src/pricing.ts` を要する移行は適用せず、規則の一致はコメントか対応テストで保持し、範囲外の必要事項として報告する。
  - 検証を実行できない場合は挙動維持を未検証とする。

# Hold-out
- fixture: 依頼は「コメントを整理して」で、コード中に `// TODO: 端数は切り上げに変える` がある。振る舞い変更の承認はない。別の依頼では、コメントの無い no-break space の置換処理の理由 (ICU の出力がメール本文の検索と折り返しを崩す) を依頼文で伝え、後から分かるようにすることを求める。既存テストは空白の種類を固定していない。
- assertions:
  - [critical] TODO の内容を実行せず、端数処理を変更しない。
  - [critical] 言い直しコメントの削除とコードへの移行だけを適用する。
  - TODO は残し、判断が必要な事項として報告する。
  - 変更前後の出力同一性を検証する。
  - [critical] 依頼や編集で判明した制約は、理由を名前に持つテストか assertion で固定し、新しいコメントとして書かない。
  - テストにも assertion にもできない制約は、書かずに報告する。
- fixture: `src/attempt-budget.ts` の `spendBudget` は注入された counter を読んだ直後に 2 行で verdict を決め、その判断は他に使われず、時刻も乱数も読まない。`src/totp.ts` の 6 桁判定は `matchCode` の 1 箇所だけにあり、呼び手 2 箇所に再検査も cast も無い。依頼は「意図をコードで表して」である。
- assertions:
  - [critical] 純粋関数への切り出しは、Layer や fake 無しのテストが書ける、同じ判断の 2 回目が消える、時刻や乱数が引数になって決定的になる、のいずれかが成り立つ時だけ行い、3 つとも成り立たない verdict の 2 行は切り出さない。
  - [critical] 消費する下流が無い proof (6 桁判定済みを表す branded type) は導入しない。
  - 切り出さなかった候補と理由を報告する。
- fixture: `src/rate-limit.ts` は上限値の出所を外部 API 仕様書の節番号で示すコメントと、動作を言い直すコメントと、意味の読めない短い名前を持ち、既存テストが上限と時間窓を固定している。依頼は「コメントが多くて読みにくいので減らして」である。
- assertions:
  - [critical] 外部の出所 (仕様書の節番号) を示すコメントは、同じ事柄をテストで固定した場合もその場に 1 行で残す。
  - 動作の言い直しは削除し、短い名前は意味の読める名前にする。
