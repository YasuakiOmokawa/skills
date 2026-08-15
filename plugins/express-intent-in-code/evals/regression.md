# express-intent-in-code regression

## シナリオ median: bbox_xhtml (機構名) → 段4 への昇格 + コメント keep/promote

working code として以下が与えられる (Ruby, 実プロジェクトの実ケースを単純化):

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

実プロジェクトの実 PR 適用が露呈させたケース。working code (TypeScript):

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

working code: todo アプリの `feature/priority` ブランチに、優先度でソートする関数 (取得元/内部表現由来の機構名 + 直上に日本語 why コメント) が追加されている。コードレビューの naming/凝集 finding としてこの関数が判断項目に挙がっている想定で、対象を明示して委譲する。

### Requirements checklist

1. [critical] 対象関数が段4 (ドメイン抽象) または探索ログ付きの段3据え置きのいずれかまで変換され、該当ファイルに Edit が適用されている
2. [critical] 変換後の名前とシグネチャだけで目的が読めるか検証している
3. 変換後にプロジェクトのテストランナー相当の検証、またはそれが無い場合の手動検証の明記がされている
4. 最終報告に chosen ladder rung、編集ファイル、検証、残余リスクが含まれている
5. 対象限定の Edit のみが行われ、対象外ファイルが変更されていない

合格条件: 全 [critical] PASS。

## シナリオ: 委譲実行 + 対象未指定・handoff 無しは確認待ちでなく no-op 宣言で終了する

会話内にコードレビュー由来の naming/凝集 finding が共有されておらず、委譲プロンプトにも対象の明示指定が無い状態で「このリポジトリの命名を良くしてください」とだけ指示される。

### Requirements checklist

1. [critical] 対象指定 (会話内の naming/凝集 finding・明示指定) が無いことを確認したうえで、diff 全体や全識別子を対象にした改名候補スキャンを行っていない
2. [critical] 「ユーザーに確認」で停止する代わりに、「handoff 無しのため変換対象なし」相当の no-op 宣言を最終メッセージに含めて終了している
3. リポジトリ内のファイルが実際には変更されていない (no-op 宣言と実態が一致している)

合格条件: 全 [critical] PASS。**「ユーザーの返答を待つ」旨を宣言して成果物ゼロで終える、または no-op 宣言と裏腹にファイルを変更していたら FAIL**。

## シナリオ: 委譲実行 + handoff は存在するが該当 finding が無い (hold-out・過学習チェック)

会話内にコードレビュー由来の finding は共有されているが、内容がパフォーマンス・テストカバレッジのみで naming/凝集 finding を含まない。対象の明示指定も無い状態で「このリポジトリの命名を改善してください」と指示される。

### Requirements checklist

1. [critical] 共有された finding が naming/凝集 finding でないことを認識し、それらを誤って対象化していない
2. [critical] 「ユーザーに確認」で停止する代わりに、「該当する naming/凝集 finding が無いため変換対象なし」相当の no-op 宣言を最終メッセージに含めて終了している
3. リポジトリ内のファイルが実際には変更されていない (no-op 宣言と実態が一致している)

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

会話内にコードレビュー由来の naming/凝集 finding が2件共有されている (`trackData`, `notifyAndRecord`)。シナリオ文脈に「実装時に経路2を適用済み。品質パス連鎖の一環として本 skill を実行」と明記する。

### Requirements checklist

1. [critical] 経路2 適用済みであることを理由に no-op 宣言をしていない (今回の呼び出しは経路1として独立に実行される)
2. [critical] handoff の2件 (naming: `trackData`、凝集: `notifyAndRecord`) を両方消化している (変換実施、または根拠を明記した見送り)
3. [critical] naming finding は段階を踏んで caller 用途に接地した名前 (`trackFieldSaveStatus` 相当) へ変換している
4. [critical] 凝集 finding は通知/監査ログ記録の責務分割で対応している
5. handoff に無い他ファイル (経路2 で既に整えたコントローラ等) には手を入れていない (対象限定)

合格条件: 全 [critical] PASS。**「経路2 済みのため対象なし」を理由に no-op 宣言したら FAIL** (= G-EIIC-1 が防ぐべき退行)。

## シナリオ R: 禁止規律コメント → 静的テスト昇格 + 述語 kernel 例外

実利用 (taimei-auth PR #142 セッション) が露呈させたケース。working code (TypeScript, `src/mfa/policy.ts`)。hook が「コメント追加 計3行 (3 行以上)」を指摘した状態でスキルを起動する:

```typescript
// src/mfa/ の他ファイルで user.twoFactorEnabled を直接比較しないこと。
// MFA 要否の判定は必ずこの関数を通す (ログイン時の判定と設定画面の出し分けの二重化防止)。
// この関数は 1 行だが削除しないこと。
export function requiresMfaChallenge(user: User): boolean {
  return user.twoFactorEnabled;
}
```

ground truth: caller 2 箇所 (`login-flow.ts` 判定経路 / `security-screen.tsx` 表示経路)、`2fa-` リテラルを grep で固定する静的 tripwire テストの前例が実在、ESLint 導入済み。

### Requirements checklist

1. [critical] 禁止規律コメント (直接比較禁止) を名前・型・定数のどれにも昇格できないと判定し、静的テスト (grep tripwire) / ast-grep / lint ルールへの昇格を具体形 (何をどこに作るか) 付きで提案する
2. [critical] `requiresMfaChallenge` を「意図を足さないラッパ」として削除提案しない — 複数文脈 (判定経路と表示経路) が同一述語を要求する 1 行述語 kernel の例外を適用する
3. [critical] 防御コメント (「削除しないこと」) は静的テスト昇格を提示した上で不要化する (ルールとコメントの軍拡競争を解消する)
4. 二重化防止の why の記録が 0 箇所にならない (テスト・lint ルールまたは 1 文コメントとして残る)

合格条件: 全 [critical] PASS。**禁止規律コメントを「真の why 4 類型でない」ことだけを理由に代替なしで削除したら FAIL**。**述語 kernel をインライン化 (削除) 提案したら FAIL**。

## シナリオ S: 正本参照 1 文の残置判定

実利用 (taimei-auth PR #142 の /dry-ssot-text 縮約置換セッション) が露呈させたケース。working code (Ruby, `app/services/challenge_store.rb`)。hook が「コメント追加 計3行 (3 行以上)」を指摘した状態でスキルを起動する:

```ruby
class ChallengeStore
  # 設計詳細: docs/adr/0013-mfa-challenge-expiry.md
  def store(challenge)
    # 5 分で失効させるための TTL
    ttl = 300
    # キーを組み立てる
    key = "mfa:#{challenge.user_id}"
    redis.setex(key, ttl, challenge.code)
  end
end
```

ground truth: ADR は実在し失効時間設計の正本。同一 why の重複は他ファイルに無い。

### Requirements checklist

1. [critical] 正本参照 1 文 (`# 設計詳細: docs/adr/...`) を「4 類型のどれでもない」ことを理由に削除しない — 残す判定 (code-comments 原則 6 の受け皿)
2. [critical] TTL コメント + `ttl = 300` を意図名の定数 (`CHALLENGE_EXPIRY_SECONDS` 相当) へ昇格しコメントを削除する
3. [critical] `# キーを組み立てる` (what コメント) を削除する
4. 重複 why の正本への集約作業 (本スキルの管轄外) へ脱線しない

合格条件: 全 [critical] PASS。**正本参照を削除、または「4 類型でないが特例で残す」等の根拠なし判定をしたら FAIL** (根拠は本文の残置基準を引くこと)。

---
