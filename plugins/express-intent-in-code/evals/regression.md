# regression eval (empirical-prompt-tuning 収束時保存)

収束記録:
- 2026-06-19 (v3.30.0 / 初版)。Iter1-3 で fresh executor が全 [critical] ○ / accuracy 100% / retries 0。median (bbox) + hold-out D/E で過学習なし。
- 2026-06-19 (v3.31.0 / 段4 ドメイン抽象を既定の到達目標へ強化)。段4 を「上限」から「既定目標 (探索手続き Step A–H + genuine-vs-invented ゲート + 根拠ある据え置き)」へ変更。Belshee「Naming as a Process」/ Evans DDD / De-Hallucinator (LLM 名前 hallucination の grounding) / Feitelson・Avidan「誤誘導名は無意味名より有害」/ Ousterhout Hard-to-Pick-Name の研究知見に基づく。fresh executor (blank slate) で 4 反復・計 9 試行が全 [critical] ○ / accuracy 100% / retries 0。
  - Iter1: median(bbox) + F/G/H/I を全実行、全 ○。非 critical の一意化 unclear (経路A/B 優先・複数候補 tie-break・public/internal 改名境界・嘘除去の振り分け) を surface。
  - Iter2: 一意化ルールを domain-abstraction.md / decision-procedure.md に追記。bbox/F/H 再実行 + hold-out J (Python/請求) 全 ○。新規に「T2 分割と Surgical Changes の境界」「grounding cite 形式」「単一 caller スキップ」が surface。
  - Iter3: boundary-and-scope §4 (分割は 1 点変換に含む)・cite 形式緩和・単一 caller スキップを追記。H/I 再実行 + hold-out K (Go/物流) 全 ○。skill 欠陥由来の新規 unclear ゼロ (clear 1)。
  - Iter4: hold-out L (Ruby/Money・経路B 型抽出) + M (Python/Redis・根拠ある据え置き) 全 ○。skill 欠陥由来の新規 unclear ゼロ (clear 2)。→ 2 連続 clear で収束。
  - 過学習チェック: fresh hold-out 4 種 (J/K/L/M、4 言語 5 ドメイン) が全 100%。全 3 経路 (A snap / B 型抽出 / 根拠ある据え置き) を実証。
  - 既知の軽微未着手 (収束下では threshold 未満・据え置き): (i) 省略語の段0/段1 判定は「展開して what が読めるか」で切るルールの明文化。fresh executor が明文ルール無しで正しく自己解決済み。
- 2026-06-19 (v3.32.0 / 実 PR #39624 適用が露呈させた gap を修正)。実 ninja-sign repo に `draft`(73 hits)と `document_item`(100+)が**両方**実在し、正しい grounding は `document_item`(この概念を指す語)だった。現ゲートは homonym 確認 (Step E) を持つが「複数の実在ドメイン語がある時、頻度でなく概念一致で選ぶ」明示規則が弱く、naive な executor は高頻度の別概念語 (`draft`) へ snap しうる gap があった。domain-abstraction.md のゲートに「複数の実在ドメイン語がある時の選定 (頻度でなく概念一致・use site 近接)」節を追加。シナリオ N (draft vs document_item) を追加し fresh executor で検証: N + bbox 回帰再実行が全 [critical] ○ / 100% / 新規 unclear ゼロ。executor は `draft`(73 hits)でなく `document_item` を概念一致で選択し新節を明示引用、frequency-vs-concept-match の罠を回避した。

用途: **regression 検出器** (capability 改善の信号としては使わない)。本 skill を変更する PR では fresh executor (blank slate, Task dispatch) で下記シナリオを再実行し、全 [critical] ○ を確認してから merge する。実行方法は empirical-prompt-tuning の「Subagent invocation contract」に従う (成果物はインライン、ファイル編集禁止)。

シナリオは median (bbox) + 段4 強化の hold-out 4 種 (F 段4 到達 / G 根拠ある据え置き / H 造語の罠 / I 名前不能→構造変更) + 旧 edge 4 種 (over-promotion+keep+drive-by 回避 / 分割判定 / 言語フォールバック / no-op 抑制) を必要に応じ再現する。

---

## シナリオ median: bbox_xhtml (機構名) → 段4 への昇格 + コメント keep/promote

working code として以下が与えられる (Ruby, ninja-sign の実ケースを単純化):

```ruby
class SignatureLayout
  def bbox_xhtml
    # 署名フィールドの配置 (押印アンカー) に使う単語座標
    # PDF は左下原点で文字座標が無いため xhtml 経由で取得する
    nodes = Nokogiri::XML(@xhtml).css("word")
    boxes = nodes.map { |n| { x: n["x"].to_f, y: @page_height - n["y"].to_f } }
    # 空行は配置対象外なので除外
    boxes.reject { |b| b[:x].zero? && b[:y].zero? }
  end
end

# 唯一の caller
fields = layout.bbox_xhtml.map { |b| place_signature_field(b) }
```

加えて、リポジトリ内に次の grounding 証拠が**存在する**ものとする (探索手続きで発見できるか試す): `app/models/signing_position.rb` に `SigningPosition` 型、i18n `ja.yml` に `署名位置` ラベル、PRD に「署名位置 (signing position) に押印する」記述。

### Requirements checklist

1. [critical] caller を観測し「戻り値を署名フィールドの配置 (押印アンカー) に使う」を動詞句で言語化してから命名する (caller 未観測で `signature` と決め打ちしない)
2. [critical] 1 段ずつ上げ、`bbox_xhtml` (段0 機構) → `word_coordinate_data` 相当 (段1 正直名) を経由してから目的名へ (段0→目的名の飛び級をしない)
3. [critical] 目的名候補が caller 用途 (押印アンカー配置) を核に据えていること、かつ候補を 3 案出し各案が表明する why の差分を示す
4. [critical] 嘘の除去: 空行除外を名前 (`…_excluding_empty` 等) か別メソッドへ昇格している
5. [critical] **段4 を試みる**: ドメイン語の探索手続きを実行し、`SigningPosition` 型・i18n `署名位置`・PRD の記述を発見し、`signing_positions` 相当の段4 語へ到達する (段3 `signature_anchor_boxes` で安住しない)
6. [critical] **grounding を明記**: 採用した段4 語の出所 (file:line / spec section) を引用し、経路A (実在語へ snap) と判定している
7. [critical] keep-vs-promote: 「PDF 左下原点・文字座標なし xhtml 経由」を外部仕様 (4 類型 a) として残し、座標変換手順/空行除外/用途説明コメントは昇格して削除すると判定している
8. 機構語 `bbox`/`xhtml` を public 名から外しつつ private 構築経路に残し grep 可能性を保つと述べている
9. 出力が指摘リストでなく before/after 変換 + 改名 3 案 + 段4 grounding/探索ログ + 昇格削除コメント一覧 + 残す真 why の形式
10. 広域 gsub/sed を使わず対象限定 Edit + lint/test (rubocop/rspec) で検証すると述べている

合格条件: 全 [critical] PASS。

---

## シナリオ F: 段4 到達 (実在語が複数ソースにある)

working code (TypeScript, React):

```typescript
// 署名者の各項目について、値・印影・手書きの保存が完了したかを保持する
function useFieldSaveState(documentId: string) {
  const [statuses, setStatuses] = useState<Record<string, "idle" | "saving" | "saved" | "error">>({});
  // ... 値保存 / 手書き endpoint / supersede / 422 抽出 ...
  return { statuses, markSaving, markSaved };
}
```

grounding 証拠が**存在する**: i18n に `下書き保存しました` / `保存に失敗しました` (UI 文言)、PRD に「各入力項目は自動保存 (draft) され、署名完了まで draft 状態」、sibling に `DraftField` 型。

### Requirements checklist

1. [critical] 概念を 1 文化して探索キーを生成し、codebase grep / UI 文言 / 仕様 を探索している (探索手続きを実行)
2. [critical] 実在語 (`draft` / 下書き保存) を発見し、`useDraftPersistence` / `useFieldDraftState` 等の段4 語へ snap している (`useFieldSaveState` の what 名で据え置かない)
3. [critical] 採用語の grounding (i18n / PRD / sibling 型の file:line・section) を出力に引用している
4. [critical] 造語していない (発見した実在語を使い、`SaveStateManager` のような CS 語彙にしない)
5. パラメータ/公開面の名前を優先し、throwaway local には深入りしていない

合格条件: 全 [critical] PASS。**段3 (`useFieldSaveState` 据え置き) のまま終えたら FAIL** (= path-of-least-resistance 退行)。**出所を引用せず昇格したら FAIL** (= 未接地)。

---

## シナリオ G: 根拠ある据え置き (実在語が存在しない純技術機構)

working code (Ruby):

```ruby
# 同一ページの座標変換結果を一度だけ計算してプロセス内で使い回す
def coord_cache_key(page, dpi)
  "#{page.id}:#{dpi}:#{@revision}"
end
```

grounding 証拠は**存在しない**: この概念を指すドメイン語は codebase・仕様・UI 文言・用語集のどこにも無い (純粋にキャッシュキー生成という技術機構)。

### Requirements checklist

1. [critical] 探索手続きを実行し、grep / 仕様 / UI 文言 を当たっている
2. [critical] どのソースにも実在ドメイン語が無いことを確認し、段3 / 正直な what 名 (例 `cache_key_for_page_coords`) で据え置いている
3. [critical] **造語していない**: `CoordinateRegistry` / `PositionCacheStrategy` のようなドメインっぽい/CS 語彙の段4 名をでっち上げていない
4. [critical] **探索ログを記録**: 概念の 1 文・試した候補語・探索したソースと結果 (該当なし)・失敗したゲート基準を出力に残している
5. 「純粋な技術機構なのでドメイン語が無いのが正しい」と判断理由を述べている

合格条件: 全 [critical] PASS。**探索ログ無しで段3 据え置きしたら FAIL** (= unearned fallback)。**ドメインっぽい語を造ったら FAIL**。

---

## シナリオ H: 造語の罠 (それっぽい語に誘導される)

working code (Ruby), 転送署名 (multiple_approvals) を束ねるメソッド:

```ruby
# multiple_approvals namespace の承認者全員に通知し、未完了なら次の承認者へ回す
def process_approvals(document)
  document.approvers.each { |a| notify(a) }
  advance_to_next_pending(document)
end
```

executor を `ApprovalOrchestrator` / `MultipleApprovalsManager` / `process_approvals` 据え置きへ誘導する罠。grounding 証拠: codebase に `multiple_approvals` namespace と `転送署名` という UI 文言・PRD 記述が**存在する** (= 実在ドメイン語は「転送署名 / forwarded approval」)。

### Requirements checklist

1. [critical] genuine-vs-invented ゲートを適用し、`Orchestrator` / `Manager` (CS 語彙 grab-bag) を段4 語として**却下**している
2. [critical] 探索手続きで実在語 (`multiple_approvals` / 転送署名 / forwarded approval) を発見し、それへ接地した名前 (`forward_to_next_approver` / `notify_forwarded_approvers` 等の段3-4 intent) にしている
3. [critical] `process_approvals` (段1 what + 機構動詞 `process`) で据え置かず、caller 用途 (順次転送) を表明している
4. plausible (それっぽい) は証拠でないと判断理由に述べている (確信ありげな誤誘導名は有害)

合格条件: 全 [critical] PASS。**`process_approvals` 据え置き or CS 語彙への改名は FAIL**。

---

## シナリオ I: 名前が見つからない → 構造変更 (改名で押し切らない)

working code (TypeScript), 1 hook が複数概念を抱える:

```typescript
// 値/印影/手書きの3モダリティ state + 保存ステータス + 検証エラー + 送信機構 を1つに抱える
function useSplitViewForm(documentId: string) {
  const [values, setValues] = useState({});
  const [seals, setSeals] = useState({});
  const [handwritings, setHandwritings] = useState({});
  const [statuses, setStatuses] = useState({});
  const [errors, setErrors] = useState({});
  // ... 値保存 / 手書き endpoint / supersede / 401 reload / 422 抽出 ...
  return { values, seals, handwritings, statuses, errors, submit };
}
```

`useSplitViewForm` という 1 つの良い段4 名を付けようとしても、対象が複数概念 (モダリティ state と送信機構) を抱えるため**ひとつの明確なイメージを作る語が書けない**。

### Requirements checklist

1. [critical] 段3 でも 1 つの明確な語が書けないことを**設計のサイン** (Ousterhout Hard-to-Pick-Name) と診断している (辞書を引いて synonym を量産しない)
2. [critical] 改名で押し切らず、責務分割 (T2) / 型抽出 (T5/T6) で概念を分けてから命名すると判断している (例: 送信機構を `useFieldSaveState` 相当へ分離し、`useSplitViewForm` はモダリティ state に専念)
3. [critical] 分割後に各片が 1 つの名付け可能な概念に対応することを確認している
4. Surgical Changes: 分割は対象内に閉じ、全 call site への波及を広げていない

合格条件: 全 [critical] PASS。**muddy な対象に磨いた synonym を被せて終えたら FAIL**。

---

## シナリオ N: 複数の実在ドメイン語がある時の選定 (頻度でなく概念一致)

実 PR #39624 (ninja-sign) 適用が露呈させたケース。working code (TypeScript):

```typescript
// 反映項目(document_item)の編集について、保存ステータス(saving/saved/error)を field 単位で追跡する
function useFieldSaveState() {
  const [statuses, setStatuses] = useState<Record<number, SaveStatus>>({});
  // ... 値保存(document_item)/手書きの 2 endpoint・supersede・401/422 ...
  return { statuses, errors, markSaving, clearErrors };
}
// caller (use-split-view-form.ts): statuses/errors を受け取り保存追跡を合成
```

探索手続きで得られる search results (ground truth。**複数のドメイン語が実在する**):
- grep `draft` / `下書き`: 73 / 28 hits — ただしこれは**文書全体の下書きライフサイクル**を指す別概念。この hook の保存ステータスとは別物。
- grep `document_item` / `DocumentItem`: 100+ hits。sibling `useSignerDocumentItemSave` が実在。対象自身のコメントも「値保存(document_item)」。
- grep `SaveStatus` / `saveStatus`: この hook 内のみ (外部 0 hit = ローカル造語)。

### Requirements checklist

1. [critical] 探索手続きを実行し、複数の実在ドメイン語 (`draft` と `document_item`) があることを認識する
2. [critical] **頻度に引かれず**、対象の概念 (項目の保存状態) を指す語 = `document_item` を選ぶ。`draft` (73 hits だが文書ライフサイクルの別概念) へ snap しない
3. [critical] use site 近接で判定したと述べる (対象の comment「値保存(document_item)」/ sibling `useSignerDocumentItemSave` が `document_item` を使う > repo 全体の `draft` 頻度)
4. [critical] `document_item` に接地した段4 名 (`useDocumentItemSaveState` 等) へ昇格し、出所を引用する
5. ローカル造語 `SaveState`/`SaveStatus` (外部 0 hit) を段4 語の根拠にしない

合格条件: 全 [critical] PASS。**`draft` へ snap (高頻度の別概念語) したら FAIL** (= 頻度を概念一致と取り違える誤り)。

