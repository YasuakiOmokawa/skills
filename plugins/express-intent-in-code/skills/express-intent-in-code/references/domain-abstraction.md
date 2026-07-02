# 段4 ドメイン抽象への到達手続き (SSOT)

段3 (Intent/目的名) から段4 (Domain Abstraction/ユビキタス言語) へ上げる手続きの SSOT。naming-ladder.md が各段の**定義**、ここが段4 に**到達する方法**。

## 段4 は既定の到達目標 (上限ではない)

対象 1 点を**可能な限り段4 まで上げる**のがこのスキルの既定目標。段3 据え置きは「探索が空振りした証拠を残した据え置き」(後述の根拠ある据え置き) に限って許す。「段3 で意図は足りているから」を据え置きの既定にしない — それが現状の退行 (最小抵抗で段3 に安住し、本体を読まないと目的が掴めない名前を残す) の正体。

ただし**飛び級は依然禁止**。目標を高くしても段を飛ばす許可にはならない。段0→1→2→3 を登りきってから段4 の語を探す。理由: Belshee「intent 名の集合が揃って初めて欠落したドメイン概念が見える。正直化していない名前の上に抽象語を載せるのは新たな嘘」。

## 段4 到達は「改名」ではなく 2 経路ある

現場で最も誤解されるのがここ。段4 は辞書を引いて「それっぽい上位語」に**改名すること**ではない。到達経路は 2 つで、どちらも実在証拠への接地 (grounding) が前提:

| 経路 | いつ | 何をするか | 根拠 |
|---|---|---|---|
| **経路A: 実在ドメイン語へ snap (改名)** | grep/spec/UI 文言に、その概念を指す**実在の語**が既にある | その語へ改名する。自分で synonym を作らない | De-Hallucinator: LLM の生成名は実在識別子に「似た」near-miss。実在語を retrieval して snap する |
| **経路B: 欠落した型 (Whole Value) を抽出** | 概念に実在語が無いが、**primitive が群れている** (下記シルエット) | 型を抽出し、その primitive を coddling していたコードを型へ移す。型名がドメイン概念になる | Belshee Primitive Obsession / Evans make-implicit-concepts-explicit / Fowler Extract |
| **据え置き (根拠ある fallback)** | 実在語が無く、単一使用で、純粋に技術機構 | 段3 (or 正直な what 名) で止め、**探索ログを残す** | Avidan & Feitelson: 誤誘導名は無意味名より comprehension が悪い。確信ありげな誤段4 名は正直な段3 名より有害 |

T5 (値オブジェクト抽出)・T6 (sum type) は**経路B の実行手段**。technique-catalog.md の T5/T6 が move の詳細。

### 到達時の優先順位・粒度 (複数の正解があるときの一意化)

- **実在語と実在型が両方ある → 経路A (改名) を優先**。型抽出 (経路B) は Surgical Changes 上 別 pass に回す (Hash→型の全 call site 波及を同 pass でしない)。経路B を選ぶのは「primitive が群れているが実在語が無い/改名だけでは段4 に届かない」時。
- **複数候補が全て同一ドメイン語に接地して PASS → caller の 1 動詞句で tie-break**。段3 で言語化した「戻り値/副作用を次に何に使うか」に最も忠実な案を推奨にする (例: 本体主作用が「次の 1 人へ進める」なら `forward_to_next_approver`)。
- **段4 snap は public surface (メソッド/フック/型名) を主対象**。内部 local 変数の改名は別判断・別コミットにし、diff 上で「公開名を変えたか/内部参照を変えたか」を区別して示す。

### 欠落した型のシルエット (経路B の trigger)

一緒に渡り歩く primitive 群は「まだ存在しないドメイン型の影」。次のいずれかを見たら型抽出を検討 (Belshee):

- 複数メソッドが**同じパラメータ集合**を受け取る / **同じフィールド部分集合**を触る / **常に一緒に呼ばれる**
- primitive の**名前が型・値域を狭めている** (`firstName: String`, `rangeInMeters: int`, `bbox: Hash`) — 名前が「本当はこういう型だ」と告白している
- `coordinate` / `data` / `DomId` / `State` のような機構語が正直名から**どうしても消せない** — 座標の集まり・状態の集まりに型名が無いサイン

**発見の move (Belshee, 紙の上で先に)**: コードに触る前に 2 つ書き出す — (1) 見えている primitive は何か、(2) 周辺コードがその primitive に対して行っている世話 (coddling: 変換・検証・分岐) は何か。この記述が欠落概念を命名する。それから型を抽出し world を移す。

## ドメイン語の探索手続き (Step A–H)

現 skill に欠けていた「どこをどう探すか」。対象ごとに必ず実行する。grep が最高 yield・最安なので B から始め、上位ソース (C/D) ほど信頼が高い。

- **Step A — 概念を 1 文にする (探索キーの生成)**: 対象 (例 `useFieldSaveState`) の戻り値/状態が**機能の中で果たす役割**を平叙文 1 文で書く (「署名者の各項目編集が保存済みかを追跡する記録」)。名詞・動詞に下線 (Evans「modeling out loud」/ Feitelson step-1 概念選択)。各語が候補ドメイン語 = **探索キー**。まだ名前ではない。
- **Step B — codebase を grep (最優先・最安)**: 候補語と語形変化を grep。同一モジュールの sibling 型/メソッド名・enum 値・API フィールド名・DB カラム・i18n キーを当たる。実在語が見つかれば**新造せず snap** (De-Hallucinator)。ヒットを file:line で記録。
- **Step C — user-facing 文言を読む (最も信頼できる)**: その経路に触れる UI ラベル・検証/エラーメッセージ・i18n カタログ。ドメインの人間が書く/読む文言なので developer drift (Cart vs Basket) に強く、実在語の最良の出所。出現箇所を記録。
- **Step D — project の散文を探す**: PRD/仕様・設計書・ADR・テスト記述 (`it should …`/シナリオ題)・元 Issue/PR タイトル。業務がこの概念を呼ぶ語を拾う。
- **Step E — 候補表に集約**: `語 | 出所 (file:line / doc section) | 由来の bounded context`。同じ語 (order, position, field, approval) が別箇所で別概念を指しうるので**文脈をタグ付け**し、出所での意味がここでの意味と一致するか確認。
- **Step F — sentence test**: 残った候補語でコードの規則/振る舞いを 1 文書き、**ドメイン専門家が促されずにその語で言うか**を問う (Evans)。つっかえる/説明節が要るなら概念がまだ欠落 → 掘り続けるか据え置き。
- **Step G — 行き詰まりかつ human reachable なら escalate**: greenfield 等でどの artifact からも語が出ず、ユーザーに聞ける状況なら、**証拠付き候補表を提案語として提示して確認を仰ぐ** (Event Storming/Example Mapping の red-card の代替)。未確認の語を単独判断で型名に固めない。
- **Step H — grounding を出力に明記**: 採用した段4 語について出所 (file:line、行が不明なら file 名 / spec section でも可) を引用し、レビュアーが「生成でなく実在」を検証できるようにする。接地できない「ドメインっぽい語」はこの step で却下。

## genuine-vs-invented ゲート (段4 語の合否判定)

段4 へ昇格する前に通す。plausible (それっぽい) は**証拠ではない** — 次トークンの流暢さは grounding の代わりにならない (LLM hallucination の典型)。

**複数の実在ドメイン語がある時の選定 (頻度でなく概念一致)**: 成熟した repo には多数のドメイン語が在り、grep は複数を返す。grounding は「**この概念を指す語**」であって「repo で最頻のドメイン語」ではない。同種の語が複数ヒットしたら (例: `draft` も `document_item` も大量に在る)、**対象の use site に近い語を採る** — 対象自身の comment / 直接の caller / sibling 識別子が**この概念に対して**使う語 > repo 全体の出現頻度。別概念を指す語 (文書ライフサイクルの `draft` と、項目の保存状態を持つ `document_item` は別概念) は高頻度でも採らない (Step E の意味一致確認 = homonym/別概念の排除)。頻度は「その語が repo に在る」ことしか意味せず、「この概念の正しい語である」ことは意味しない。

概念一致の確認には**その語の repo 内での使用規約**を含める — その接尾辞/語がどんな種類の対象に付いているか (配置ディレクトリ・返り値の型・boolean 述語か値を返すか)。例: `*Policy` が repo 内で `app/policies/` の boolean 述語専用なら、値を返す PORO に `Policy` を付けるのは高頻度でも概念不一致で採らない。逆に、対象の役割を正確に指す語が CS 風接尾辞 (`Resolver` 等) しか無い場合は、規約の合わない実在ドメイン語へ snap するより、役割を正直に表す名前を段3 として採り、探索ログに「実在語 X は使用規約不一致で却下」と記す (ユーザーや reviewer が候補語を提案した場合も、CS 語彙という理由だけで却下せず、この使用規約一致で判定する)。

**PASS 条件**:
- 原則**2 つ以上の独立ソース**で出現する (PRD に出て、かつ user-facing 文言にも出る / 専門家・チケットが言い、かつ sibling 型が既に使う)。ただし**1 つでも権威的なソース** (確定したドメイン用語集の項目・専門家の明確な発言) があれば足りる (発見的な閾値。実験で 2 と確定した数ではない)。
- sentence test を通る (専門家が促されずその語で言う)。
- **経路B の型抽出は uniform な使用箇所が複数あること** (Belshee「one-off abstractions は noise」)。単一 call site のために作る型は造語であって抽象ではない。

**FAIL 条件 (= 造語。却下して据え置き or 経路探索やり直し)**:
- コード・仕様・チケット/PR・用語集・user-facing 文言の**どこにも出てこない** → 却下。
- CS/実装語彙をドメイン語に偽装 (`Handler`/`Manager`/`Processor`/`Strategy`/`Service` の grab-bag 接尾辞、`Data`/`Info`/`Dto` の形状接尾辞)。Belshee「プログラミング言語を書いているのでない限り、ソフトウェア工学のドメインを名前に持ち込むな」/ Hilton「型情報を省け」。
- 既に別の語で呼ばれている概念への**新 synonym** (Hilton/Deissenboeck & Pizka: 1 概念 1 語/bounded context)。「より精密な synonym」は name drift を生むだけ。

**境界判定の tie-break**: 迷ったら**下位の段に留める**。誤誘導名は無意味名より comprehension が悪い (Avidan & Feitelson) ので、未検証の段4 語は正直な段3/段1 名より厳密に有害。

## 名前が見つからない = 設計のサイン (経路B への routing)

段3 でも**ひとつの明確なイメージを作る語/句が書けない**なら、それは**名付ける側でなく対象 (THING) の問題** (Ousterhout の Hard-to-Pick-Name red flag「簡単な名前が見つからないのは、その対象がきれいに設計されていない兆候」)。正しい対応は辞書を引くことではなく**構造を直すこと**: 対象は 2 つ以上の概念を抱えているので、各片が 1 つの名付け可能な概念に対応するまで**分割 (T2) / 型抽出 (T5) / sum type 化 (T6)** する。

- 長い正直名に `and`/`with` が複数 → メソッドが多すぎを抱える → 分割 (T2)。各節を Belshee の 2 問で吟味:「この節は他の節と無関係か」「この節は隠蔽すべき副作用か」。`And`/`Or`/`If` は全てリファクタの合図。
- 機構語が消せない → ドメイン型が欠落 → 経路B の型抽出。

**Belshee の硬い規則**: 正直名が気に入らないなら、名前を短くするのではなく**コードがやることを変える**。命名は設計。改名は構造を直して初めて可能になる。

## 据え置きの記録 (根拠ある fallback)

段3 で止める時は、**なぜ段4 に届かなかったかを出力に必ず記録**する。未知の未知を「記録された既知の未知」に変える (Example Mapping の red-card / De-Hallucinator: near-miss が実在参照を引けなければ造語と分類)。出力に専用節を設ける:

```markdown
### 段4 据え置きの根拠 (探索ログ)
- 概念の 1 文 (Step A): 「…」
- 試した候補語: `…`, `…`
- 探索したソースと結果: codebase grep (該当なし) / UI 文言 (該当なし) / 仕様 (該当なし)
- 失敗したゲート基準: どのソースにも出現せず (= 造語になるため却下)
```

human reachable なら、この記録はそのまま「証拠付き提案語」の申し送りになり、後で専門家が確認して昇格できる。「ドメイン語が無い」を**探索ログで裏付けた主張**にする (最小抵抗で到達する既定にしない)。

## Surgical Changes との両立 (best-effort を暴走させない)

ゲートが通っても、**改名/型抽出は指定された 1 点に対してだけ**行う。新しい型を同じ pass で全 coddling call site へ波及させない (それは Surgical Changes が禁じる広域変更)。Belshee も「発見した抽象を即座に全面採用しない (間違っているかもしれない)。~60% 採用し、価値が証明されるにつれ残りを変える」。段4 を既定目標にすることが repo 全体改名の許可になってはならない。

## 出典

- Arlo Belshee, *Naming as a Process* — "Get to Intent Revealing" / "Get to Domain Abstraction" (digdeeproots.com)。Primitive Obsession → Whole Value 抽出、one-off abstractions は noise、CS 語彙禁止。
- Eric Evans, *DDD* — Making Implicit Concepts Explicit (listen to language / scrutinize awkwardness / model out loud)、Refactoring Toward Deeper Insight。
- Eghbali & Pradel, *De-Hallucinator* (arXiv 2401.01701) — LLM は実在識別子に似た名前を hallucinate。near-miss を retrieval key に実在参照へ snap。
- Feitelson et al., *How Developers Choose Names* (IEEE TSE 2022) — 命名 = 概念選択→語選択→構成。品質レバーは概念選択。2 開発者の一致率 6.9% (唯一の正名を主張しない)。
- Avidan & Feitelson, *Effects of Variable Names on Comprehension* (ICPC 2017) — 誤誘導名は無意味な単一文字名より comprehension が悪い。
- John Ousterhout, *A Philosophy of Software Design* — Hard-to-Pick-Name / Vague Name red flag。
- Peter Hilton, *How to name things* — 問題ドメインの語/1 概念 1 語/型情報を省く/辞書語。
