# 決定手続き (Step 0〜9) とアンチパターン (SSOT)

SKILL.md の Workflow が要約、ここが手順詳細・アンチパターン・コミット境界の SSOT。

## 入口の二経路

- **経路1 (事後変換)**: 既存 working code 1 点の昇格。以下 Step 0〜9 に従う。
- **経路2 (生成時)**: いま書いているコードへの適用。[generation-recipe.md](generation-recipe.md) が SSOT。新規に書く行だけに適用し、既存行の改名はしない — 対象が既存コードに及ぶなら経路1 の Step 0 判定へ回す。

## Step 0 適用判定 (経路1)

- 対象が (a) working code で (b) 今回の変更対象 (blast radius 内) か確認。drive-by 改名は**中止** (Surgical Changes)。
- 改名は意味を変えうる。着手前に対象の回帰テスト/characterization test の有無を確認し、無ければ T9 で先に用意して**振る舞いを固定**する。
- 対象が引数で明示されていなければ、まず作業ディレクトリの `quality-review-handoff.md` (`$(git rev-parse --git-dir)/quality-review-handoff.md`。`/review-code-quality` の申し送りファイル) を探し、naming / 凝集 finding があればそれを対象として読み込む。**読み込むだけでクリアはしない** (クリアは `/polish-before-commit` の責務)。申し送りファイルが無い、または該当 finding が無い場合にのみユーザーに確認する (branch 名や推測で決め打ちしない)。
- **委譲実行 (subagent として起動された場合)**: AskUserQuestion が利用可能ツールに無い実行文脈では、上記の確認で止めず「handoff 無しのため変換対象なし」を最終メッセージで宣言し、確認を待たず終了する (単独起動でユーザーに確認できる場合は上記のとおり確認する)。

## Step 1 現在段の診断

- 対象名を命名梯子 ([naming-ladder.md](naming-ladder.md)) のどこか判定。機構語リスト (`bbox` `xhtml` `data` `info` `tmp` `retval` `manager` `util` `handle` `process` `dto` `vo` `impl`) で段0 を、用途が読めるかで段1/段3 を切り分ける。
- **1 段ずつ上げる。飛び級 (段0 → 目的名直行) 禁止** — 機構違いの別案で発散する。

## Step 2 caller 観測 (呼び出し文脈の平叙文化)

- 全 caller を grep し「戻り値を次に**何に使うか**」を 1 動詞句で言語化する。
- 複数 caller が**別目的**なら 1 メソッド 2 役のサイン。改名でなく機構/目的の分離 (T2) を先に行う。
- caller を読まずに目的名をでっち上げない (押印用途を `signature` と決め打ちする退行を防ぐ)。実 caller・ユビキタス言語を**fact として**確認する。
- **「同一概念 (中立な目的名 1 本で済む) か 2 役 (分割) か」の判定軸は戻り値の形ではない**。戻り値の射影が同一形でも、両 call site で**真に読める単一目的名を選べるか**で決める。どの名前を選んでも片方の call site で名前が嘘になる (例: 監査記録と請求書表示) なら 2 役 = 分割。形が同じことに引きずられて中立名 1 本にまとめると、両用途のどちらの目的も鮮明に表明できず段1 (what 名) に逆戻りする。分割後、両 public が共有する同一射影は private 機構メソッドへ集約する (下記 Step 7 の rule-of-three 例外参照)。

## Step 3 Honest 化と構造の発見

- 目的名へ直行せず、いったん「何を・何から・何を経由して」を全部出した長い正直名へ改名。
- `and`/`with` が複数 = 責務複数 (T2 関数抽出)、消せない機構語 = ドメイン型欠落 (T5 値オブジェクト/T6 sum type) と読む。
- 長さは構造を直して縮める (語を削らない)。

## Step 4 嘘の除去 (段2)

- 名前に出ていない副作用・前提・除外 (空行除外/座標系反転/キャッシュ) を列挙。
- 名前へ昇格 (`…_excluding_empty`) するか別メソッドへ追い出して名前 = 契約を成立させる。
- **振り分け基準**: 除外/前提が**自明な内部不変条件** (例: 署名位置でないものを弾く) なら述語メソッド側へ、**呼び手が知るべき契約** (例: 空集合を返しうる・特定条件で除外する) なら名前 or 戻り型へ。過長名を避けつつ契約は名前に残す。
- ここを飛ばすと why コメント依存が温存される。

## Step 5 目的名への昇格 (段3) + 名前で担えない why の構造化

- caller 用途を核にドメイン役割名へ。
- 名前 1 つで担えない不変条件・状態・全称的約束は T5(型)/T6(sum type)/T7(戻り型)/T9(テスト・property) へ昇格。
- **判定軸**: 「コメントで補っている不変条件を 1 つでも型/構造/テストへ移せたか」。

## Step 5.5 段4 ドメイン抽象への到達 (既定の到達目標)

> 詳細・探索 Step A–H・ゲート・据え置き記録の全文は [domain-abstraction.md](domain-abstraction.md) が SSOT。ここは操作の要約。

- 段4 は**可能な限り到達する既定目標**。段3 に達したら必ず段4 を試みる。「段3 で足りる」を据え置きの既定にしない。
- **ドメイン語の探索手続きを実行**: 概念を 1 文化 (探索キー生成) → codebase grep (sibling 型/enum/API フィールド/DB カラム/i18n キー) → user-facing 文言 → 仕様/ADR/テスト記述/PR タイトル。実在語が見つかれば**新造せず snap** (経路A)。
- **名前が見つからない時は構造を直す (経路B)**: 段3 でも 1 つの明確なイメージを作る語が書けない・機構語が消せない・primitive が群れている (同一パラメータ集合/名前が型を狭める) なら、それは設計のサイン (Ousterhout Hard-to-Pick-Name)。辞書引きでなく分割 (T2)/型抽出 (T5)/sum type (T6) で欠落した型を出してから名前を付ける。
- **genuine-vs-invented ゲート**で合否: 原則 2 つ以上の独立ソース (または 1 つの権威的ソース) で出現・sentence test を通る・型抽出は uniform な複数使用箇所がある → PASS。どこにも出ない・CS 語彙偽装 (`Manager`/`Handler`/`Data`)・既存概念の新 synonym → FAIL (造語)。迷えば下位段に留める。
- **据え置きは根拠を残す (根拠ある fallback)**: ゲートが通る語が出なければ段3 で止めてよいが、**探索ログ** (概念の 1 文・試した候補語・探索したソースと結果・失敗したゲート基準) を出力に必ず記録する。探索せずに段3 で安住しない。
- **Surgical Changes 維持**: 改名/型抽出は対象 1 点のみ。新型を同 pass で全 call site へ波及させない (広域変更禁止)。

## Step 6 コメントの蒸留と純化

- 各 why コメントを keep-vs-promote 決定表 ([comment-keep-vs-promote.md](comment-keep-vs-promote.md)) で名前/型/定数/述語へ振り分け、畳めたものを削除。
- 残すのは真の why 4 類型 (外部仕様/トレードオフ根拠数値/危険・順序依存/将来予定 FIXME) のみ。
- **順序厳守**: 名前/構造変換 → 表明できた why を削除 → 真の why のみ残置 (先にコメントを消さない)。
- 新名を caller に差し戻して音読し、why コメントなしで意図が通ることを成功条件とする。

## Step 7 過剰昇格の歯止め (T10)

- 意図を足さないラッパ・1 ケース多態・造語目的名・過長名 (`save_user_because_legacy_api_requires_sync`) を Inline/据え置きで畳む。
- 昇格は rule of three を待ち 2 例目で。why は核 1 ドメイン語に圧縮し根拠は ADR/コメントへ分担。

## Step 8 fresh-eyes 検証

- after の名前/シグネチャ**だけ** (コメント・plan 無し) を見て目的を言い当てられるか検証。
- 非自明な対象は [agents/intent-reader.md](../agents/intent-reader.md) を Task で起動 (bias-free な readability test)。自明な単一改名は cold self-read で代替。Task (Agent) ツールが利用可能ツール一覧に無い場合のみ cold self-read に切り替え、その旨を出力に明記する。非自明/自明の判定に迷う場合は bias-free 検証を優先し Task 起動側に倒す。
- 推論された目的が caller 観測の目的 (Step 2) と食い違えば名前を再調整。

## Step 9 検証と粒度・出力

- 各変換適用後に lint/test を必ず通す:
  - Ruby: `bundle exec rubocop` + `bundle exec rspec`
  - TypeScript: `yarn eslint <file> --fix` + `yarn prettier --check <file>`
  - 他言語: プロジェクトのテストランナー/リンタ。判定できなければ「手動検証が必要」と明記。
- grep で全 caller/spec/コメント参照の改名漏れを洗う。
- **広域 gsub/sed は使わず対象限定 Edit** (`()` や行頭インデントにマッチする置換はコードを黙って壊す)。
- 出力は SKILL.md の出力フォーマットに従う (指摘リストでなく変換成果物)。

## コミット境界の切り方

改名→分割→型化→コメント削除を**1 コミットに混ぜない**。安全な機械的改名から順に、段ごとにコミット境界を切り、各境界で振る舞い不変 (テスト緑) を確認する。レビュアーが「振る舞いは不変」を 1 コミット単位で検証できる。

```
commit 1: rename bbox_xhtml → signature_anchor_boxes (機械的改名・テスト緑)
commit 2: extract word_boxes_in_pdf_coords (関数抽出・テスト緑)
commit 3: introduce SignatureAnchor type (型化・テスト緑)
commit 4: promote/delete comments (コメント蒸留・テスト緑)
```

## アンチパターン (全文)

| やりがちな誤り | 正しい挙動 |
|---|---|
| **why コメント撲滅の誤読** — 外部制約・根拠数値・危険警告・将来予定まで消す | ゴールは撲滅でなく純化。昇格可能性をテストしてから消す。4 類型は残す |
| **what 止まりで満足** — `bbox_xhtml → word_coordinate_data` で止め目的に届かない (ユーザー退行の正体) | caller 用途を動詞句にして役割名まで必ず上げる |
| **目的を全部名前に詰めた過長名** — `save_user_because_legacy_api_requires_sync` | why は核 1 ドメイン語に圧縮、根拠・制約はコメント/ADR に分担 |
| **Extract/型化/多態の乱発** — 1-2 行ラッパ・1 ケース空 subclass・2 引数の毎回 Struct 化で間接層だけ増やす | rule of three を待つ。新しい概念/why を足す時だけ抽出を残す |
| **機構語の全消去で grep 不能化** — `bbox`/`xhtml` を完全に消しパースのバグを追えなくする | 機構語は public 名から外し private メソッド/構築経路に残す |
| **caller を読まない目的名のでっち上げ** — 用途を観測せず「それっぽい why 名」を付ける | 必ず実 caller・ユビキタス言語を fact として確認 |
| **広域 gsub/sed での機械的改名** — `()` や行頭インデントにマッチしコードを黙って壊す | 対象限定 Edit + 適用直後の lint/build 検証 |
| **順序ミスでの意図喪失** — 名前改善前に why コメントを先に消す | 順序は「名前/構造変換 → 表明できた why を削除 → 真の why のみ残置」 |
| **diff スコープ侵犯** — 依頼外の隣接メソッドまで改名し diff を膨張 | 対象は指定された 1 点に絞り深く適用する |
