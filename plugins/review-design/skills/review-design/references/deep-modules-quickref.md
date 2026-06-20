# Deep Module 早見表 (Quick Reference)

reviewer 起動時はこのファイルのみ Read する。判定で迷ったら `deep-modules.md` 本体を Read する。

## 本質

**深いモジュール = 小さな interface + 大きな実装。** 呼び出し側が学ぶ interface 1 単位あたりの振る舞い量 (= leverage) が大きいほど深い。interface が実装と同程度に複雑なら shallow (避ける)。

- **Interface** = 呼び出し側が正しく使うのに知る必要のある全て (型シグネチャ + 不変条件・順序制約・エラー様態・性能特性)。型だけではない。
- **Depth** = leverage。Ousterhout の「実装行数 / interface 行数」比は**使わない** (水増しを報酬にする)。
- **Seam** (Feathers) = その場を編集せず振る舞いを差し替えられる位置 = interface が置かれる場所。
- 用語は厳密に。`component` / `service` / `boundary` で代用しない。

## interface 設計時に問う 3 つ

- method 数を減らせるか
- 引数を単純化できるか
- もっと複雑さを内側に隠せるか

## 早見判定基準

| # | 観点 | ✅ | ⚠️ | ❌ |
|---|---|---|---|---|
| 1 | Shallow module 検出 | 小さな interface の背後に隠れた実質的振る舞いがある (深い) | 一部 method が pass-through だが全体は振る舞いを足す | 全/大半の method が 1:1 委譲の pass-through。interface ≈ 実装で leverage なし |
| 2 | Deletion test | 消すと複雑さが N 個の呼び出し側に再出現する | — | 消すと複雑さが消えるだけ (呼び出し側はほぼ同じコードを直接書く) = pass-through |
| 3 | Seam discipline | seam は 2+ adapter が正当化される箇所のみ。internal seam は interface に漏れない | 1 adapter だが本番 + テスト mock で 2 つ目が妥当 | 1 adapter のみ (差し替え予定なし) の seam = 不要な indirection / internal seam が interface に漏出 |
| 4 | Testability | 依存注入 + 結果返却 + 小さい表面積で interface 越しにテスト可 | 1 点で依存内部生成 or 副作用だが移行容易 | 依存を内部生成し interface 越しにテスト不可 / 表面積過大 |

## 反例検索ヒント

| 観点 | 探すもの |
|---|---|
| Shallow module | 各 public method が他オブジェクトへの 1 行 1:1 委譲だけ (`@x.foo(...)` を返すだけ)。隠す分岐/計算/状態がゼロ |
| Deletion test | module を消した場合に呼び出し側へ再出現する複雑さの量を見積もる。ゼロなら pass-through |
| Seam discipline | 注入点/抽象に対し現存 or 確実予定の adapter が 2 つ未満 (本番のみ・テスト mock も無い) / テストのためだけに internal seam を public 露出 |
| Testability | 内部での依存生成 (`new XxxGateway()` 等) / 戻り値 `void` で内部状態書き換え |

## 推奨修正の雛形 (短文テンプレ)

| 違反種 | 推奨修正テンプレ |
|---|---|
| Shallow module | `<file> は全 method が pass-through。呼び出し側へ inline、または <隠すべき方針> を内部に隠して深くする` |
| Deletion test fail | `<file> は消しても複雑さが再出現しない。中間層を除去` |
| 不要 seam | `<seam> は adapter 1 つのみ。抽象を外し具体に統合 (2 つ目が現れるまで待つ)` |
| Testability | `<file> の <内部生成依存> を引数注入に変更 / <副作用> を結果返却に変更` |

## 詳細を Read する条件 (観測可能トリガー)

以下のいずれかに該当する場合のみ `deep-modules.md` 本体を Read する:

- 依存の性質ごとに deepening 手順/テスト戦略を出し分ける必要がある (依存 4 分類)
- shallow と判定し、親が再設計のため複数 interface 案の発散生成 (Design It Twice) を要求した
- 用語 (depth / leverage / seam / adapter) の厳密定義や 深い/浅いの図を出力に含める必要がある
