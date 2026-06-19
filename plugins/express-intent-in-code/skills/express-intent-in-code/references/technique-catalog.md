# 技法カタログ (T1〜T11)

意図 (why) を表明する方向に効く変換手法。SKILL.md の「技法選択」表が trigger→T の引き表、ここが各 T の move と before/after の SSOT。**leverage 順** (high を先に検討)。

文献横断 (The Art of Readable Code / Clean Code / A Philosophy of Software Design / Refactoring / DDD / Naming as a Process / Parse Don't Validate / Make Illegal States Unrepresentable / BDD・property testing) を 1 つのカタログに統合したもの。

---

## T1 目的語昇格 rename (high)

**trigger**: メソッド/値名が取得元・内部表現・ノイズ語・`tmp`/`retval`/`get*` で構成され、用途を知るのに本体か why コメントを読む必要がある。

**move**:
1. 全 caller を grep する。
2. 「戻り値を次に**何に使うか**」を 1 動詞句で書く (例: 「署名フィールドを配置する」)。
3. そこから名詞句を抽出し、取得元/内部表現/ノイズ語を除いて**目的語を核に据える**。
4. 新名を caller に差し戻し「主語+述語」で音読し、why コメントなしで意図が通るか確認。
5. 通れば、役割を説明していた why コメントを削除。複数 caller が別目的なら分割 (T2) へ。

```ruby
# before — 用途を知るには本体かコメントを読むしかない
def bbox_xhtml
  # 署名フィールドの配置に使う単語座標
  ...
end
signature_fields = layout.bbox_xhtml.map { |w| anchor_for(w) }

# after — caller の音読で目的が通る。コメント不要
def signature_anchor_boxes
  ...
end
signature_fields = layout.signature_anchor_boxes.map { |w| anchor_for(w) }
```

---

## T2 意図名による関数抽出 (Extract Function) (high)

**trigger**: 1 メソッドが取得+変換+選別など複数段を抱え、各段の目的を段落ごとの why コメントが代弁している (コメントが抽象レベルの変わり目を区切っている)。

**move**:
1. コメントが区切る境界 = 抽象が変わる境界で塊を切り出す。
2. 下位の汎用機構 (`parse_word_boxes` / `to_pdf_coords`) は**機構名で private 抽出**。
3. 残った高位関数には**ドメイン目的名**を付ける。
4. 元関数を step-down の呼び出し列にし、上から物語として読める形にする。
5. 機構を説明していた why コメントは、下位関数の自明な what に縮退して消える。

> **rule-of-three の例外 (分割後の重複解消)**: T10 は「新しい抽象/概念の導入は rule of three を待つ」と律するが、**1 メソッド 2 役を分割した直後に両 public が同一本体を持つ場合、その共有本体を private 機構メソッドへ抽出するのは別動機 (copy-paste 回避) なので 2 箇所でも正当**。rule of three が律するのは「新概念の早すぎる抽象化」であって、自分が作った分割の重複解消ではない。

```ruby
# before — 1 メソッドに 3 段、コメントが段を代弁
def signature_anchor_boxes
  # xhtml をパースして単語ノードを取る
  nodes = Nokogiri::XML(xhtml).css("word")
  # PDF 座標系 (左下原点) に変換
  boxes = nodes.map { |n| { x: n["x"].to_f, y: page_height - n["y"].to_f } }
  # 空行は配置対象外なので除外
  boxes.reject { |b| b[:x].zero? && b[:y].zero? }
end

# after — 高位関数は目的だけを物語る。下位は機構名で private
def signature_anchor_boxes
  word_boxes_in_pdf_coords.reject { |b| empty_box?(b) }
end

private

def word_boxes_in_pdf_coords
  parse_word_nodes(xhtml).map { |n| to_pdf_coords(n) }
end
```

---

## T3 コメント→名前/型/定数への蒸留 (Replace Comment / Magic Literal) (high)

**trigger**: 式や数値リテラルや条件の横に「これは何を計算/判定しているか」の説明コメントが付く。同じ概念を説明する why コメントが 2 箇所以上に散る (概念欠落のサイン)。

**move**: 各コメントを説明対象へ振り分ける — 存在理由→メソッド名、値の正体→値オブジェクト/型名、分岐理由→述語メソッド名、マジック値→意味のある定数名。畳めたコメントは削除。同一 why が 3+ 箇所なら ADR に集約しコメントは 1 行参照に縮約。

```ruby
# before
# 信頼度 0.8 未満は誤認識なので捨てる
words.select { |w| w.confidence >= 0.8 }

# after — マジック値が定数名で語る
MIN_RELIABLE_CONFIDENCE = 0.8 # OCR 誤認識の足切り (実測: 0.8 未満は誤認識率 30%超)
words.select { |w| w.confidence >= MIN_RELIABLE_CONFIDENCE }
```

---

## T4 説明変数・要約変数 (Explaining / Summary Variable) (high)

**trigger**: 巨大な式や複合 boolean 条件があり、何を判定しているか式を実行シミュレートしないと読めない。条件式にコメントで意味を添えている。

**move**: 部分式をその**概念名の変数**に、複合条件を**業務状態名**に代入する。変数名は「その値が何か (what)」でなく「**なぜそれを見るか (業務状態)**」を述べる。ただし 1 回しか使わず意味が自明な値には付けない (T10 の歯止め)。

```ruby
# before — 何を判定しているのか式を追わないと分からない
if box[:y] > header_height && box[:y] < page_height - footer_height && box[:text].match?(/署名|捺印/)
  anchors << box
end

# after — if 文がドメイン語彙で読める
in_body_region   = box[:y] > header_height && box[:y] < page_height - footer_height
is_signature_label = box[:text].match?(/署名|捺印/)
anchors << box if in_body_region && is_signature_label
```

---

## T5 primitive を値オブジェクト/型へ昇格し smart constructor で封印 (high)

**trigger**: Hash/Array/string/数値タプルのまま流れる値に、同じ why コメント (署名配置用座標・検証済み・単位 pt) が利用箇所ごとに散る (primitive obsession)。検証済みか・どの座標系か・何用かが型に現れない。

**move**: 概念にドメイン名の型を与え、検証/座標変換を生成時の smart constructor に集約、不変条件はガード化。境界でのみ wrap/unwrap しドメイン内部は型のまま運ぶ。機構語 (`bbox`/`xhtml`) は private 構築経路に残し grep 可能性を保つ。

```ruby
# before — Hash が流れ、座標系や用途がコメント頼み
boxes = parse.map { |n| { x: n.x, y: page_h - n.y } } # PDF 左下原点に変換済み

# after — 型名と smart constructor が散在コメントを恒久的に凝縮
class SignatureAnchor
  # 生成は from_xhtml_node 経由のみ。座標系変換と検証はここに集約
  def self.from_xhtml_node(node, page_height)
    new(x: node.x, y: page_height - node.y) # PDF 左下原点
  end
  attr_reader :x, :y
  def initialize(x:, y:) = (@x, @y = x, y)
end
```

```typescript
// TypeScript: branded type + smart constructor で「検証済み」を型に載せる
type PdfCoord = number & { readonly __brand: "PdfCoord" };
const toPdfCoord = (xhtmlY: number, pageHeight: number): PdfCoord =>
  (pageHeight - xhtmlY) as PdfCoord; // 左下原点への変換を一点に封印
```

---

## T6 矛盾しうる record/分岐を sum type へ畳む + 網羅強制 (high)

**trigger**: 状態タグ + 状態依存の option/null フィールド同居で「あり得ない組合せ」が構築可能。`type code`/`status` で分岐する switch が複数メソッドに散在し、ケース集合が一望できず追加時に修正漏れが沈黙する。

**move**: 正当な状態だけを variant の各 case が固有フィールドを持つ形に宣言。利用側を網羅 match にし、TS は `assertNever(x: never)`、Ruby は `case/in` の `else raise` で漏れを機械強制。型定義自体が「この概念が取る全状態と各々の形」という業務ルール = why を自己文書化する。

```typescript
// before — status と任意フィールドが同居し不正状態が作れる
type Delivery = { status: string; email?: string; address?: string };

// after — 各 case が固有フィールド。不正組合せは型で表現不能
type Delivery =
  | { kind: "emailOnly"; email: string }
  | { kind: "postOnly"; address: string }
  | { kind: "emailAndPost"; email: string; address: string };

function format(d: Delivery): string {
  switch (d.kind) {
    case "emailOnly": return d.email;
    case "postOnly": return d.address;
    case "emailAndPost": return `${d.email} / ${d.address}`;
    default: return assertNever(d); // case 追加忘れがコンパイルエラーになる
  }
}
```

> **言語注記**: T6/T7 は静的型システムが強い言語で leverage が最大。Ruby では `Data.define` + `case/in` パターンマッチ + `else raise` で近似する。型の無い動的言語では「不正状態を構築不能にする」強制力が落ちるため、guard clause (T8) や validation の集約で代替する。

---

## T7 validate→parse 変換 / 戻り型を呼び手の意図に寄せる (medium)

**trigger**: `T→boolean` / `T→void(throws)` が検査結果を捨て呼び出し後も弱い型のまま、下流で再検証や「なぜここで保証されるか」の why コメントが要る。nil/空/例外の特殊ケースが呼び手に nil 分岐と why コメントを散らす。

**move**: `WeakT→StrongT` (`NonEmpty a` / `Email`) に書き換え、検証済みを型で運ぶ。特殊ケースは存在ごと消す — 空なら必ず空配列を返し nil を返さない (複数形名で集合を返す契約を表明)。呼び手の nil 分岐と「nil は画像 PDF の場合」コメントが消える。境界で 1 回だけ検証し以降は strong type を引き回す (Parse, Don't Validate)。

```ruby
# before — nil を返し、呼び手に分岐とコメントを強いる
def signature_anchors
  return nil if image_pdf? # 画像 PDF は文字座標が無い
  ...
end
anchors = doc.signature_anchors
anchors&.each { ... } # nil ガードが散る

# after — 「無い」を空配列で表現し、呼び手の分岐を消す
def signature_anchors
  return [] if image_pdf?
  ...
end
doc.signature_anchors.each { ... } # nil 分岐不要
```

---

## T8 制御フローを目的の流れへ (Guard Clauses + パイプライン化 + CQS) (medium)

**trigger**: 深いネストで正常系の主筋が分岐の谷に埋もれる。再代入される中間変数で値の概念が時間軸でブレる。値を返すついでに副作用がある/純粋計算と取得が同居し名前が嘘をつく。

**move**: 異常系をガード節で冒頭に集め早期 return しネストを 1 段に潰す → 最後の 1 行が関数の目的を表明。再代入を `map`/`select`/`const` のパイプラインにし「パース→変換→抽出」の意図を上から下へ一直線に。query (副作用なし述語/名詞) と command (動詞命令形 + `!`) を分ける。

```ruby
# before — 正常系が谷に埋もれる
def anchor_for(box)
  if box
    if box.confidence >= MIN
      build_anchor(box)
    end
  end
end

# after — ガード節で異常系を先に出し、最後の行が目的
def anchor_for(box)
  return unless box
  return unless box.confidence >= MIN
  build_anchor(box)
end
```

---

## T9 テスト/property を why の第二の声にする (medium)

**trigger**: 名前を改名しても why が目的名に乗りきらない (用途が複数・全称的な約束)。why が散文コメントに退避して実行されず陳腐化する。production 名と独立した語彙で目的を固定したい。

**move**: 改名で why に届かない残差を、production 名でなく**テストの声**に乗せる — テスト名を `should_<期待>_when_<条件>` の振る舞い文 (機構名を排しドメイン効果を述語に)、key example を table-driven で各見出しに規定ルールを 1 文付与し SSOT 化、本質的不変条件を property (round-trip/invariant) で全称宣言。リファクタ時は characterization test で振る舞いを先に固定してから改名する。

```ruby
# テスト名が「いつ・何を保証するか (why)」を述べる
describe "#signature_anchors" do
  it "空行を錨点から除外する (誤配置防止)" do ... end
  it "画像 PDF では空集合を返す (文字座標が無いため)" do ... end
end
```

---

## T10 Inline/据え置きの歯止め (過剰昇格を畳む) (medium)

**trigger**: 意図を足さないラッパ (`get_x` が `x` を返すだけ)、1 回使い捨ての自明な値への命名、1 ケースしかない分岐の多態化、共有ドメイン語が無いのに造語した目的名、過長名 (`save_user_because_legacy_api_requires_sync`)。

**move**: 「その名前/型/層は**新しい概念か why を 1 つ足すか**」を問い、足さないなら Inline で畳む。昇格は「閉じたケース集合が複数箇所に散在し漏れリスクがある」時のみ (rule of three、2 例目で昇格)。why は核 1 ドメイン語に圧縮し、残りは文脈 (クラス名)・コメント・ADR に分担。共有語が無ければ段3 で据え置き、造語しない。

```
# 過長名 (why を全部名前に詰めた)
save_user_because_legacy_api_requires_sync
↓ 核 1 語に圧縮し、根拠はコメント/ADR へ
sync_save_user  # 同期保存。理由: docs/adr/0007-legacy-api-sync.md
```

---

## T11 境界・範囲・一貫命名の固定 (low)

**trigger**: `max_x`/`x_limit` が包含か排他かを名前で約束しておらず off-by-one の温床。同一概念が `bbox`/`coordinate`/`word_data`/`position` と箇所ごとに揺れ、同一物か別物か判断に対応付けコメントが要る。

**move**: 含む両端は `first`/`last`、排他終端は `begin`/`end`、含む上下限は `min_`/`max_` を選び、規約選択自体を包含意図の表明にする。概念の正準名を 1 つ決め全 grep して統一、別概念に同語を流用していないかも検査。命名表を CONTEXT.md/用語集に SSOT 記録。**既存コードベースの慣習が優先する場合はそれに従う** (Surgical Changes)。
