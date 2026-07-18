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

- 2026-07-04 (v0.8.0 / 生成時経路 (経路2) を追加)。ninja-sign 実 PR (split-signer-view, +8,782行) で opus4.8 生成コードのコメント過多 (Ruby 密度18%、制約弁明の呼び出し側露出・同一 why の9箇所重複) が露呈させた「スキルが生成時に効かない」gap を修正。generation-recipe.md (3つの瞬間 + セルフチェック) を新設し、Step 0 入口を二経路化、T12 制約吸収ラッパーを追加。文言は RED-GREEN-REFACTOR で検証:
  - RED: 統制群 (利用側コメント規約のみ・opus・シナリオ生成P ×5) で「制約弁明の公開本体露出」4/5・「目的名ラップ」1/5 を確認。禁止形アーム (×5) は正当 why の全消しが4/5 発生し、4基準フルパス 0/5 — 禁止形はレシピ形より有害という writing-skills の知見を自ケースで実測。
  - GREEN/REFACTOR: レシピ v1 (フルパス3/5、E消失+ラップなしの崩壊2/5) → v2 (「0件」偏重のセルフチェックに E 保全の必須項目を追加、別ドメイン実例で出力形を固定。P 4/5) → v3 (why の置き場所を「名前付き定義の直上」に限定、公開本体の判断は先に述語抽出。Q 2/3) → v4 (ガード節の許容を明記し T8/T10 と整合、呼び出し側に同 why を書かない)。v4 最終: **P 3/3・Q 2/3 フルパス、コメント問題 (言い換え/露出/重複/E消失) は全 6 ファイルで 0 に収束**。
  - 既知の弱点: (i) Q 系で「裸の複合条件ガードを公開関数に残す」構造の癖が 1/3 残存 (コメント問題ではない)。対応としてセルフチェック項目6 を追記 — この項目は v4 で検証済みの瞬間2 の文の checklist への転記だが、項目単体の確認ラウンドは未実施 (次回 regression で要観測)。(ii) クリーンルーム検証中、実リポジトリを参照して汚染された実行体が 2/35 発生 (P-v5, P-x1 は除外し代替を生成)。
  - 経路1 の regression: 二経路化後のスキル全文で median (bbox) / F / G / H / I / N / O を fresh executor 再実行。median 7/7・F 4/4・G 4/4・H 3/3・I 3/3・O 3/3 で全 [critical] PASS。N は初回 2/4 (draft の罠は回避し use-site 近接の手続きも適用したが、`document_item` 接地名への最終昇格を「scope 不一致」を理由に見送り) → 同条件で 2 回再実行し 2/2 PASS (`useDocumentItemSaveStatus` / `useDocumentItemSaveTracking` へ経路A 昇格・出所引用あり)。N の選定規則の SSOT (domain-abstraction.md) は本改修で未変更のため、初回 FAIL は実行体の揺らぎと判断。N は 3 試行中 2 PASS の判定系シナリオとして、次回変更時も複数試行での観測を推奨。
  - 追加 empirical-prompt-tuning (subagent invocation contract の self-report 形式で3シナリオ median / 生成P / 生成Q × 2 iteration):
    - Iter 0 (静的整合性): SKILL.md の Workflow (Step 0〜9) と出力フォーマット節が経路1 前提であることが節見出しに明示されておらず、経路2 executor が変換成果物形式を出そうとする恐れを検出 → 節見出しに「(経路1・事後変換)」を追加、出力フォーマット節に「経路2 の出力はコードそのもの」を明記
    - Iter 1: 3/3 で全 [critical] PASS・accuracy 100%。unclear points 9件のうち skill 側の実質改善候補は 2件 — (a) technique-catalog.md T2 の bbox_xhtml canonical example で `parse_word_nodes` が SKILL 一般ルール「機構語を private 構築経路に残す」と齟齬 → `parse_word_bbox_nodes` に修正 + 整合性注記、(b) 生成時レシピの why 配置で複数の隣接名前付き定義が1判断を共同で担うときの優先順位が未規定 → generation-recipe.md 瞬間1 に「動機が最も読めない側 = 本体を持つ関数の実装直上に固定」を追記
    - Iter 2: 3/3 で全 [critical] PASS 維持。Iter 1 の2 fix が実測で機能 — genQ executor が Retry 1回で「generation-recipe.md 瞬間1 の記述を読み直し、データ側でなく本体を持つ関数側に置く方針」と明示的に自己解決、median executor が `parse_word_bbox_nodes` を採用。新規 unclear は scenario/harness 側または executor が原則から自己解決できる範囲に留まる。metric は step 9-10・retries 0-1 で安定。plateau と判断し収束
    - Failure pattern ledger: (P1) canonical worked example が一般ルールと齟齬している (Iter 1、以後 fix + 整合性注記で再発ゼロ)。(P2) 複数の隣接名前付き定義が1判断を共同で担うときの why 一意化欠如 (Iter 1、以後 fix で自己解決確認)。 P1/P2 の再発なし・skill 側改善候補が既に反映済みのため、これ以上の反復は diminishing returns として cutoff

- 2026-07-07 (委譲実行摩擦の解消。plugin.json の version bump は本チューニングでは未実施、別バッチで反映予定)。design-doc.md の共通契約 (規則2: dialogue approver 不在時は確認待ちでなく宣言して終了) に基づき、decision-procedure.md Step 0 に「AskUserQuestion が利用可能ツールに無い実行文脈では handoff 無しのため変換対象なしを宣言して終了する」読み替え、Step 8 に「Task ツールが利用可能ツール一覧に無い場合のみ cold self-read へ切替え、その旨を明記する」tie-break、domain-abstraction.md Step G に「human reachable でない場合は確認を仰がず据え置きの記録へ進む」分岐を追加。SKILL.md に統一見出し「## 委譲実行 (subagent として起動された場合)」を新設し3箇所を要約参照した。
  - Iter1 (baseline, RED): シナリオA (明示ターゲット) は全 [critical] ○。シナリオB (対象未指定・handoff無し) は [critical] 2件が × (「ユーザーに確認」で停止し無人実行で最終メッセージが宣言でなく質問文になる) — 想定どおり RED を確認。
  - Iter2 (改修後): シナリオA/B とも全 [critical] ○・accuracy 100%。
  - Iter3 (再現性確認、fresh executor・スキル無変更): シナリオA/B とも全 [critical] ○・accuracy 100% 維持。両シナリオで surfaced した新規不明点 (Step 8 の段レベル不一致、diff 非存在時のバッチ走査範囲) はいずれも delegation テーマ外の一般的な曖昧さで 2 ラウンド共通のため収束条件 (2 連続で新規不明点0) を満たすと判定 (委譲テーマの新規不明点は 0)。
  - hold-out シナリオC (handoff ファイルは存在するが naming/凝集以外の finding のみ記載): 全 [critical] ○・accuracy 100%、直近平均からの低下なし (過学習兆候なし)。「handoff 無し」の文字どおりの読みに overfit せず「該当 finding 無し」への汎化を確認。
  - 経路1 の regression (単独起動動作の後方互換): median (bbox_xhtml) を fresh executor で再実行し全 [critical] (7件) PASS。Step 0/8 の読み替えは AskUserQuestion 有無に紐づく条件分岐のため、単独起動相当の経路には影響しないことを確認。
  - Failure pattern ledger: (P3) バッチ/パイプライン起動の no-op 宣言が SKILL.md Overview にのみ記述され、手続き詳細の SSOT である decision-procedure.md Step 0 に欠落 (Iter1 シナリオB、fix で Step 0 へ移設し再発ゼロ)。
  - 今回のスコープ外として記録するのみに留めた事項 (delegation テーマでなく一般的な skill 品質の曖昧さ。次回非 delegation テーマのチューニングで再訪): Step 8 fresh-eyes (intent-reader) が grounding 未共有のため段4 判定済みの語を段3 相当と保守的に見立てる不一致 (agents/intent-reader.md に Gotchas 1行を追記済み)、diff が存在しないバッチ起動時の走査範囲未定義、decision-procedure.md Step 6 「真の why 0件」時の扱い、命名梯子/技法選択の語彙リスト重複、「新規識別子」の定義が経路2 とバッチ起動で書き分けられていない、第三種の命名欠陥 (多義衝突・段0ノイズ語以外) の分類、handoff ファイルパターン検索の曖昧さ。

- 2026-07-07 (G-EIIC-1。バッチ/パイプライン起動の規定に「経路2 適用済みでも品質パス連鎖内の本呼び出しは経路1として独立実行し no-op としない」を追記)。fresh executor (Task dispatch) で median (経路2済み後の連鎖内呼び出し) / edge (経路1単独・handoff 無し) の2シナリオを検証。
  - Iter1: median/edge とも全 [critical] ○・accuracy 100%・retries 0。median executor は「経路2 実施済みを理由にした no-op」を検討すらせず、handoff の2件 (naming: `trackData`→段4 相当への変換、凝集: `notifyAndRecord`→責務分割) を両方消化した。経路2 で既に整えた対象外ファイル (`seal-image-controller.ts`) は変更なしのまま保持。
  - Iter2 (再現性確認、fresh executor・スキル無変更): median/edge とも全 [critical] ○・accuracy 100% 維持。新規に surface した不明点はいずれもテーマ外 (テスト基盤不在時の検証代替、T3 の適用範囲境界、疎な repo での段4 探索手順、フィクスチャのパスプレフィックス誤認、同一コミット内での自己参照的な grounding 出所) で 2 ラウンド共通のため、委譲テーマの新規不明点 0 で収束と判定。
  - hold-out (handoff は存在するが naming/凝集以外の finding のみ): 全 [critical] ○・accuracy 100%。business-impact/coupling の finding をこの skill の対象と誤認して不要な改名・分割を作り出すことはなく、no-op を宣言し実ファイル変更 0 のまま終了 (過学習兆候なし)。
  - regression gate (代表3シナリオ再実行): median (bbox_xhtml)・委譲実行 (対象明示)・委譲実行 (対象未指定・handoff無し no-op) のいずれも全 [critical] PASS。G-EIIC-1 の追記は単独起動・委譲実行いずれの既存経路にも影響しないことを確認。
  - Failure pattern ledger: 新規なし (G-EIIC-1 は Iter1 から一貫して意図どおり動作し、fix 適用は不要だった)。
  - スコープ外として記録するのみに留めた事項 (次回非 G-EIIC-1 テーマのチューニングで再訪): テスト基盤が無い fixture での「検証」記述の代替手段が不明瞭、T3 (コメント→名前/型/定数) の適用範囲境界、疎な repo (grounding 証拠が少ない) での段4 探索手順の簡略化余地。

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

---

## シナリオ O: 接尾辞の使用規約不一致 (高頻度語の suffix 規約と、正しい候補の CS 風接尾辞)

実利用 (2026-07-01) が露呈させたケース。working code (Ruby)、署名者ビューのレイアウト種別を決めて返す PORO:

```ruby
# 文書の署名方式・デバイス幅から、署名者ビューのレイアウト (split / stacked / pdf-only) を決めて返す
class SignerViewLayout
  def determine(document, viewport)
    return :pdf_only if document.handwriting_only?
    viewport.narrow? ? :stacked : :split
  end
end
```

探索手続きで得られる search results (ground truth):
- grep `Policy`: 40+ hits — ただし全て `app/policies/` 配下の **boolean 述語専用** (`can_edit?` 等を持つ認可 Policy)。値 (レイアウト種別) を返すこの PORO とは使用規約が不一致。
- grep `Resolver`: 0 hits (repo 内に実在しない)。ただし対象の役割 (入力条件からレイアウトを解決して返す) を正確に指す。
- ユーザーが `SignerViewLayoutResolver` を提案してくる。

### Requirements checklist

1. [critical] `Policy` の高頻度に引かれず、repo 内の使用規約 (boolean 述語専用・`app/policies/` 配置) を確認して概念不一致と判定する (`SignerViewPolicy` に snap しない)
2. [critical] ユーザー提案の `Resolver` を「実在証拠のない CS 語彙」という理由だけで却下しない — 使用規約一致 (値を返す解決役) で判定する
3. [critical] 規約の合わない実在ドメイン語より、役割を正直に表す名前 (`SignerViewLayoutResolver` 等) を採り、探索ログに「`Policy` は使用規約不一致で却下」と記す
4. 判定根拠に返り値の型 / 述語か値かの別を挙げている

合格条件: 全 [critical] PASS。**`Policy` へ snap (suffix 規約不一致の高頻度語) したら FAIL**。**ユーザー提案語を CS 語彙の理由のみで却下したまま終えたら FAIL**。


---

## シナリオ 生成P: 生成時レシピ — 制約弁明の集約 (Ruby / Rails コントローラ)

経路2 (生成時) の regression。fresh executor に「利用側コメント規約 (コードコメント7原則相当) + generation-recipe.md + 下記課題」だけを与え、コードを新規生成させる (実リポジトリ参照は禁止。課題文の API は実在とみなす)。

課題: 電子契約アプリに、署名者向け画面からマイ印鑑 PNG を配信する読み取り専用エンドポイント `Documents::Approvals::SealImagesController#show` を新設する。制約: (1) 既存 `Teams::SealImagesController#show` は team ログインセッション必須で、URL token 認証の署名者からは使えない。(2) 署名者は `SignerUser.find_by!(token: params[:token])` で特定できる。(3) 印影は署名者の team が `can_use_my_seal?` (プラン許可 + active 印鑑あり) を満たすときだけ返す。フロントも同条件で出し分けるが、直接リクエストにも印影を漏らさない。既存側は `require_plan_ability :my_seal` で守られており認可条件を揃える。(4) 印鑑は `team.seal_images.active.first`、画像は `seal_image.png_binary`。(5) 見つからない・権限なしは 404。

### Requirements checklist

1. [critical] 名前・シグネチャの言い換えコメント (A) = 0件
2. [critical] 制約の弁明・正当 why が公開 `show` 本体に露出していない (C-露出 = 0 かつ E-露出 = 0)
3. [critical] 認可判定が目的名の述語/ヘルパー (例 `authorized_seal_image`) にラップされ、弁明はその定義直上1箇所 (素の1条件ガード節は `show` にあってよい)
4. [critical] 正当 why (認証方式 or 認可契約 or 404統一のセキュリティ判断) が名前付き定義の直上に**1件以上残っている** (0件 = 削りすぎで FAIL)
5. 同一 why の本文重複 = 0件

合格条件: 全 [critical] PASS。**E 全消し (基準4違反) は、コメント0件の「綺麗な」出力でも FAIL** (= 禁止形への退行)。

## シナリオ 生成Q: 生成時レシピ — 状態機構の名前化 (TypeScript / React hook)

課題: 署名画面 (左 PDF / 右フォーム) の双方向フォーカス同期 hook `useBidirectionalFocus`。仕様: フォーム focus → 対応 overlay box へ scrollIntoView + 選択状態更新 / overlay box クリック → フォーム field へ focus() / overlay box 参照は `overlayBoxRefs: Map<string, HTMLElement>` (キー `${fieldId}-${page}`) / ページは遅延レンダリングされ、未レンダリング時の scrollIntoView は `notifyPageRendered(page)` まで保留 / クリック→focus() はフォーム onFocus を再発火させる (はね返り)。

### Requirements checklist

1. [critical] A = 0件 (型・名前から自明な言い換えを書かない)
2. [critical] はね返り・保留の why が公開コールバック本体に露出していない (E-露出 = 0)。why は ref / 述語 / ヘルパーの定義直上に集約
3. [critical] はね返り判定・保留処理が述語/ヘルパー/型設計 (ページキー Map 等) で名前化されている
4. [critical] 遅延レンダリング or はね返りの why が1件以上残っている (全消しは FAIL)
5. 同一 why の本文重複 = 0件 / 公開関数本体に裸の複合条件ガードを残さない (既知の弱点: v0.8.0 時点で 1/3 発生。悪化していないか観測する)

合格条件: 全 [critical] PASS。

---

以下は 2026-07-07 (委譲実行摩擦の解消) 追加分。収束記録: 上記参照。fresh executor (Task dispatch、AskUserQuestion/EnterPlanMode/ExitPlanMode/ScheduleWakeup 不可) で下記 3 シナリオを実行し全 [critical] ○・accuracy 100%。

## シナリオ: 委譲実行 (Task dispatch) で対象明示時は通常どおり変換する

working code: todo アプリの `feature/priority` ブランチに、優先度でソートする関数 (取得元/内部表現由来の機構名 + 直上に日本語 why コメント) が追加されている。`/review-code-quality` から naming/凝集 finding としてこの関数が申し送られている想定で、対象を明示して委譲する。

### Requirements checklist

1. [critical] 対象関数が段4 (ドメイン抽象) または探索ログ付きの段3据え置きのいずれかまで変換され、該当ファイルに Edit が適用されている
2. [critical] Step 8 fresh-eyes 検証で nested Task (`agents/intent-reader.md`) の起動が試みられている (Task が利用可能な環境で無条件に cold self-read へ切り替えていない)
3. 変換後にプロジェクトのテストランナー相当の検証、またはそれが無い場合の手動検証の明記がされている
4. 出力フォーマット (診断 / 改名候補3案 / 段4到達根拠または据え置き根拠 / before-after diff / 昇格して削除したコメント / 残す真の why) の各節が最終報告に含まれている
5. 対象限定の Edit のみが行われ、対象外ファイルが変更されていない

合格条件: 全 [critical] PASS。

## シナリオ: 委譲実行 + 対象未指定・handoff 無しは確認待ちでなく no-op 宣言で終了する

対象リポジトリに 申し送りファイル (`quality-review-handoff-<branch>.md`) が存在せず、委譲プロンプトにも対象の明示指定が無い状態で「このリポジトリの命名を良くしてください」とだけ指示される。

### Requirements checklist

1. [critical] 申し送りファイル (`quality-review-handoff-<branch>.md`) 相当のファイルが存在しないことを確認したうえで、diff 全体や全識別子を対象にした改名候補スキャンを行っていない
2. [critical] 「ユーザーに確認」で停止する代わりに、「handoff 無しのため変換対象なし」相当の no-op 宣言を最終メッセージに含めて終了している
3. 多義衝突 (blast radius 内で同じ語が2つのドメイン概念を指す) や段0ノイズ語 (`doc`/`data`/`info`/`target`/`tmp` 等) の grep スクリーニングが実行されている、または該当なしと明記されている
4. リポジトリ内のファイルが実際には変更されていない (no-op 宣言と実態が一致している)
5. 副次候補が見つかった場合、対象化せず据え置きログとして1行で記録している (該当が無ければ本項目は「該当なし」の明記で満たされる)

合格条件: 全 [critical] PASS。**「ユーザーの返答を待つ」旨を宣言して成果物ゼロで終える、または no-op 宣言と裏腹にファイルを変更していたら FAIL**。

## シナリオ: 委譲実行 + handoff は存在するが該当 finding が無い (hold-out・過学習チェック)

対象リポジトリに 申し送りファイル (`quality-review-handoff-<branch>.md`) は存在するが、記載されている finding がパフォーマンス・テストカバレッジのみで naming/凝集 finding を含まない。対象の明示指定も無い状態で「このリポジトリの命名を改善してください」と指示される。

### Requirements checklist

1. [critical] 申し送りファイル (`quality-review-handoff-<branch>.md`) を確認したうえで、記載されている finding が naming/凝集 finding でないことを認識し、それらを誤って対象化していない
2. [critical] 「ユーザーに確認」で停止する代わりに、「該当する naming/凝集 finding が無いため変換対象なし」相当の no-op 宣言を最終メッセージに含めて終了している
3. 多義衝突・段0ノイズ語の grep スクリーニングが実行されている、または該当なしと明記されている
4. リポジトリ内のファイルが実際には変更されていない (no-op 宣言と実態が一致している)
5. 副次候補が見つかった場合、対象化せず据え置きログとして1行で記録している (該当が無ければ本項目は「該当なし」の明記で満たされる)

合格条件: 全 [critical] PASS。**「handoff が存在する」という表層だけで naming finding があると誤認し無関係な finding を対象化したら FAIL** (= 「handoff 無し」の文字どおりの読みへの過学習)。

## シナリオ: 経路2 適用済みコードへの品質パス連鎖内呼び出し (no-op 化しない)

working code (TypeScript): 実装時に経路2 (生成時レシピ) を適用済みという設定の2ファイル。

```typescript
// フィールドは反映項目(document_item)の編集単位に対応する。保存ステータスの遷移履歴をフィールド単位で保持する
export function trackData(fieldId: string, status: SaveStatus) {
  const record = registry.get(fieldId) ?? { history: [] };
  record.history.push({ status, at: Date.now() });
  registry.set(fieldId, record);
  return record;
}
```

```typescript
// 承認者への通知と監査ログ記録を1関数に集約
export function notifyAndRecord(document: Document, approver: Approver) {
  emailClient.send(approver.email, buildApprovalRequestEmail(document));
  auditLog.append({ documentId: document.id, approverId: approver.id, action: "notified", at: Date.now() });
}
```

申し送りファイル (`quality-review-handoff-<branch>.md`) に review-code-quality 由来の naming/凝集 finding が2件記載されている (`trackData`, `notifyAndRecord`)。シナリオ文脈に「実装時に経路2を適用済み。品質パス連鎖の一環として本 skill を実行」と明記する。

### Requirements checklist

1. [critical] 経路2 適用済みであることを理由に no-op 宣言をしていない (今回の呼び出しは経路1として独立に実行される)
2. [critical] handoff の2件 (naming: `trackData`、凝集: `notifyAndRecord`) を両方消化している (変換実施、または根拠を明記した見送り)
3. [critical] naming finding は段階を踏んで caller 用途に接地した名前 (`trackFieldSaveStatus` 相当) へ変換している
4. [critical] 凝集 finding は通知/監査ログ記録の責務分割で対応している
5. handoff に無い他ファイル (経路2 で既に整えたコントローラ等) には手を入れていない (対象限定)

合格条件: 全 [critical] PASS。**「経路2 済みのため対象なし」を理由に no-op 宣言したら FAIL** (= G-EIIC-1 が防ぐべき退行)。

収束記録: 2026-07-17 (v0.16.0 progressive disclosure 分割)。バッチ/パイプライン起動パラグラフを references/batch-invocation.md へ退避 (SKILL.md diff は 1 行のみ、挙動変更なし)。全 13 シナリオを fresh executor で再実行し、移設内容に関わる委譲 B/C/D 含め [critical] ○ (batch-invocation.md への 1 hop 到達と行番号付き引用を確認)。シナリオ O は 3 試行中 2 PASS — 今回未変更の domain-abstraction.md 側の判定揺らぎで N の収束記録 (3 試行中 2 PASS) と同型、分割由来の regression ではない。O/N は判定系シナリオとして複数試行での観測を継続する。

収束記録: 2026-07-18 (regression 再検証・skill 無変更)。express-intent-in-code の SKILL 本文・agents・references を一切変更せず、保存済み全 13 シナリオ (median / F / G / H / I / N / O / 生成P / 生成Q / 委譲4種) を fresh executor (general-purpose subagent, blank slate, Task dispatch) で 1 ラウンド再実行。全シナリオで全 [critical] ○・accuracy 100%・skill 欠陥由来の新規不明点 0。Iter 0 静的整合性チェックで frontmatter description のトリガー (経路1 の handoff/mechanism 名, 経路2 の生成3瞬間, whole-diff 機械スクリーニング 3 兆候) と本文カバー範囲に乖離なしを確認 (修正不要)。委譲4種は実 git fixture repo で ground-truth 検証: target は対象 (`orderByWeightMap`→`sortTasksByPriority` 段4 snap) + 唯一の caller のみ改名伝播 (無関係 2 ファイルは無変更)、noop/holdout は git status clean の真正 no-op (機械検査 3 兆候いずれも該当なし)、chain は handoff 2件 (`trackData`→`trackFieldSaveStatus` / `notifyAndRecord` の通知/監査ログ責務分割) を消化し `seal-image-controller.ts` は無変更、を git status で実測確認。過去に判定揺らぎ (3 試行中 2 PASS) を記録した N (`draft` 73hits vs `document_item` の概念一致選定) と O (`Policy` suffix 規約不一致で却下・ユーザー提案 `Resolver` を CS 語彙理由だけで却下しない) は本ラウンド 1 試行でいずれも PASS — capability の劣化兆候なし。委譲 target/chain の Step 8 で executor が nested intent-reader Task を実起動 (無条件 cold self-read への退行なし) を確認。F は intent-reader の medium 確信 + 具体的曖昧性指摘を受け Step 8 の設計どおり推奨名を 1 回再調整 (skill が意図どおり機能した retry で欠陥ではない)。生成Q の既知弱点 (公開関数本体に裸の複合条件ガードを残す・v0.8.0 で 1/3) は本ラウンドで非再現 (単一述語呼び + 単一比較のみ)。新規不明点は全て scaffolding 起因 (fixture に実 lint/test 基盤・caller・grounding file:line が無い) または skill 既存規則から自己解決される一般曖昧さ (段1/段3 境界, T2 分割境界, intent-reader 段ラベル不一致=intent-reader.md Gotchas 既定) で、いずれも過去記録の「テーマ外」項目と同型。過去の収束記録が直前ラウンドのクリアとして先行するため、本日 1 ラウンドで収束確定。Failure pattern ledger: 新規なし。
