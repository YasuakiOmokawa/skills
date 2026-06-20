# Deep Modules (詳細)

`deep-module-reviewer` が判定で迷ったとき、または深さ評価を出力に詳述するときに Read する。早見表は `deep-modules-quickref.md`。出典: mattpocock codebase-design (Feathers の seam / Ousterhout の Design It Twice、depth は leverage で定義)。

## 用語 (厳密に使う — 代用語禁止)

- **Module** — interface と implementation を持つもの。規模不問 (関数 / class / package / 層をまたぐ slice)。代用語 `unit` `component` `service` を使わない。
- **Interface** — 呼び出し側が正しく使うのに知る必要のある全て: 型シグネチャに加え、不変条件・順序制約・エラー様態・必要な設定・性能特性。`API` `signature` は型表面しか指さないので使わない。
- **Implementation** — module の内側のコード。**Adapter** とは区別する (小さな adapter + 大きな実装 = Postgres repo、大きな adapter + 小さな実装 = in-memory fake もありうる)。seam が論点のとき「adapter」、それ以外は「implementation」。
- **Depth** — interface あたりの振る舞い量 (= leverage)。小さな interface の背後に大きな振る舞い → **deep**。interface が実装と同程度に複雑 → **shallow**。
- **Seam** (Michael Feathers) — その場を編集せず振る舞いを差し替えられる場所 = interface が置かれる位置。どこに seam を置くかは「背後に何を入れるか」とは別の設計判断。代用語 `boundary` を使わない (DDD の bounded context と衝突)。
- **Adapter** — seam で interface を満たす具体物。役割 (どの slot を埋めるか) を指し、中身は指さない。
- **Leverage** — 呼び出し側の得: 学ぶ interface 1 単位あたりの能力。1 実装が N 個の呼び出し側と M 個のテストに効く。
- **Locality** — 保守側の得: 変更・バグ・知識・検証が 1 箇所に集まる。一度直せば全体が直る。

## 深い vs 浅い

```
深い module = 小さな interface + 大きな実装        浅い module = 大きな interface + 薄い実装 (避ける)
┌─────────────────────┐                          ┌─────────────────────────────────┐
│   Small Interface   │ ← method 少, 引数単純      │       Large Interface           │ ← method 多, 引数複雑
├─────────────────────┤                          ├─────────────────────────────────┤
│  Deep Implementation│ ← 複雑さを隠す             │  Thin Implementation            │ ← 素通り
└─────────────────────┘                          └─────────────────────────────────┘
```

## 原則

- **深さは interface の性質であって実装の性質ではない。** 深い module は内部に小さく mock 可能・差し替え可能な部品を持ってよい — それらが interface に出ないだけ。module は interface の **external seam** に加え、実装内部の **internal seam** (自身のテスト用) を持てる。
- **deletion test.** module を消したと仮定する。複雑さが消えるなら pass-through だった。複雑さが N 個の呼び出し側に再出現するなら keep に値した。
- **interface = test surface.** 呼び出し側もテストも同じ seam を越える。interface の *先* をテストしたくなるなら module の形が間違っている。
- **1 adapter = 仮定上の seam / 2 adapter = 本物。** 実際に何かが seam を越えて変動するのでなければ seam を作らない。

## テスト容易性 (深い interface はテストを自然にする)

1. **依存は作らず受け取る** — `function processOrder(order, paymentGateway)` (テスト可) / 内部で `new StripeGateway()` (テスト困難)。
2. **副作用でなく結果を返す** — `calculateDiscount(cart): Discount` (テスト可) / `applyDiscount(cart): void` で内部状態を書き換える (テスト困難)。
3. **小さい表面積** — method が少ないほどテストも少ない。引数が少ないほど setup が単純。

## deepening 手順 — 依存 4 分類

浅い module 群を安全に深くする (統合する) とき、依存の性質で分類する。分類が「深くした module を seam 越しにどうテストするか」を決める。

1. **In-process** — 純粋計算・メモリ内状態・I/O なし。常に deepen 可。module を統合し新 interface 越しに直接テスト。adapter 不要。
2. **Local-substitutable** — ローカルなテスト代替を持つ依存 (Postgres に対する PGLite、in-memory filesystem)。代替があれば deepen 可。テストでは代替をテストスイート内で動かす。seam は internal、外部 interface に port を出さない。
3. **Remote but owned (Ports & Adapters)** — 自分のサービスでネットワーク越し (マイクロサービス、内部 API)。seam に **port** (interface) を定義。深い module がロジックを持ち、transport は **adapter** として注入。テストは in-memory adapter、本番は HTTP/gRPC/queue adapter。
4. **True external (Mock)** — 自分で制御できない第三者サービス (Stripe, Twilio 等)。注入された port として受け取り、テストは mock adapter を渡す。

### seam discipline

- **1 adapter = 仮定上の seam / 2 adapter = 本物。** 少なくとも 2 つの adapter (通常 本番 + テスト) が正当化されない限り port を作らない。単一 adapter の seam はただの indirection。
- **internal seam と external seam を分ける。** 深い module は internal seam (実装内部・自身のテスト用) を持てるが、テストが使うからといって interface に露出しない。

### テスト戦略: replace, don't layer (差し替えよ、重ねるな)

- 深くした module の interface 上のテストが揃えば、浅い module 群への旧 unit test は無駄になる — 消す。
- 新しいテストは深くした module の interface に書く。**interface = test surface**。
- テストは内部状態でなく interface 越しの観測可能な結果を assert する。
- テストは内部リファクタを生き延びる — 振る舞いを記述し実装を記述しないため。実装変更でテストが変わるなら、それは interface の先をテストしている。

## Design It Twice (escalation — reviewer の default では行わない)

shallow と判定し、親が再設計のため複数 interface 案の発散生成を要求したときに使う。出典: Ousterhout「最初の案が最良であることは稀」。

### 手順

1. **問題空間を提示** — sub-agent 起動前に、選んだ候補の制約・依存 (どの分類か)・制約を具体化する粗いコードスケッチ (提案ではなく制約の地ならし) をユーザー向けに書く。読んでもらいつつ Step 2 へ。
2. **sub-agent を並列起動** — `Task(subagent_type="general-purpose")` で 3 つ以上を並列起動 (本リポの agent 呼び出し規約に従い、各 Task は本ファイルの該当節を Read して適用)。各 agent に **radically different** な interface を設計させ、別々の制約を与える:
   - agent 1: 「interface を最小化 — entry point 1〜3 個。1 つあたりの leverage 最大化」
   - agent 2: 「柔軟性を最大化 — 多くのユースケース/拡張に対応」
   - agent 3: 「最頻の呼び出し側に最適化 — default ケースを自明に」
   - agent 4 (該当時): 「seam をまたぐ依存を ports & adapters で設計」
   - 各 brief に本ファイルと CONTEXT.md の語彙を含め、アーキ語彙とドメイン語彙を一貫させる。
   - 各 agent の出力: ① interface (型/method/引数 + 不変条件・順序・エラー様態) ② 呼び出し例 ③ seam の背後に隠すもの ④ 依存戦略と adapter ⑤ trade-off (leverage が高い/薄い箇所)。
3. **提示して比較** — 各案を順に提示 → 散文で比較。**depth** (interface の leverage) / **locality** (変更が集まる場所) / **seam 配置** で対比し、最後に自分の推奨を 1 つ強く出す (要素を組み合わせる hybrid 可)。メニューでなく強い読みを返す。
