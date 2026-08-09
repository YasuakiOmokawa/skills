# Analyst 契約 (BB / WB 統合定義)

BB (Black Box) / WB (White Box) 両 Analyst の責務・情報源制約・Critical 閾値・出力フォーマットの単一定義。

- **standard (inline)**: main agent が本ファイルの **BB 節と WB 節の両方** を読み、情報源制約と出力契約をそのまま適用して 2 視点の判定を別々に産出する (統合は Step 3 の機械合成で行い、判定段階で混ぜない)
- **deep (dispatch)**: 各 subagent は起動 prompt で指定された役割の節のみ適用する。BB Analyst と WB Analyst は独立に動くため互いの分析結果は参照しない

結果はメインエージェントの Red Team レビューで使用される。Markdown 形式で返すこと。

## 共通規則 (両役割)

### Critical 閾値

> この節は [red-team-checklist.md](red-team-checklist.md) の「Critical 閾値」と同内容の複製 (dispatch 先の 1 ホップ自己完結のため)。**変更時は両方を同時更新すること (sync 義務)**。

**判定の既定規則**: 「この欠陥は **それ単独で能動的に** 害を成立させるか? それとも害を **容易にする** だけか?」 — 成立させるなら Critical、容易にするだけなら Important。以下 4 類型に **現に該当** する指摘のみ Critical 認定:

1. **データロス / 破壊的変更** (DB drop, schema break, irreversible mutation, 既存データの整合性破壊、部分 payload 送信による既存データの無条件上書き = nested attributes の未送信キー = nil 代入)
2. **能動的に成立するセキュリティ侵害** — それ単独で不正アクセス / データ取得 / 権限昇格が **成立する** 欠陥 (認証バイパス / SQL・XSS injection / CSRF / SSRF / IDOR / open redirect / race condition による権限昇格 / mass-assignment 等)。攻撃者が既に有効な認証情報・セッションを保持している前提でのみ害が成立・継続する欠陥 (例: パスワード変更後のセッション未失効) は、単独で成立させるのでなく容易にする側 = Important に分類する
3. **既存ユーザ動線の破壊** (現行ユーザの操作が不可になる、互換性消失。遅延・文言品質の低下は含まない)
4. **ロールバック不能** (revert できない migration, 削除不可能な外部影響。コード差分の revert 可否と、既に外部へ渡った成果物 — 送付済み請求書・送信済みメール等 — の取り消し可否は別々に評価し、後者が取り消せないなら該当)

**Critical でないもの (Important 以下に格下げ)**: hardening / 防御の多層化の不足で、それ単独では侵害が **成立しない** もの — rate-limit / brute-force 耐性・アカウントロック・監査ログ・強パスワード方針の欠如、機微情報の localStorage 保管 等。攻撃を容易にするが単独で害を成立させない。性能劣化 / 観測性 / i18n / polish も Critical でない。「OWASP Top 10 に載るか」でなく「**それ単独で害が成立するか**」で決める。上記いずれにも当たらない指摘は Important / Nice-to-have に分類。「重大に見える」だけで Critical にしないこと。

### 指摘件数のルール

「最低 N 件出せ」のような件数縛りは**なし**。

- 該当があれば指摘する
- 0 件なら「該当なし」と明示し、根拠を 1 文で書く (例: 「コード上 enum 値が全て分岐に登場しており、状態マトリクスに漏れなし」)
- ノイズ目的の Nice-to-have 量産は禁止 (指摘の signal/noise を上げるための運用)

### Area カテゴリ (controlled vocabulary)

`area` フィールドには以下から選択する (Red Team が `area` タグで BB↔WB 指摘を機械的に集約し、真の合意・補強し合う合意を検出する):

`auth` / `data` / `security` / `performance` / `observability` / `network` / `ui` / `deps` / `business` / `infra` / `その他`

複数該当する場合はメインの 1 つを選ぶ (例: 認証バイパスは `security` を優先)。`その他` は最小化すること。

### AC ID

AC は `AC-1, AC-2, ...` の序数付きリストで渡される。判定オブジェクトでは `ac_id` フィールドで参照する。

### 出力契約 (JSONLines + Markdown 併用、両役割共通)

機械処理しやすさのため findings と AC 判定は **JSONLines** (1 行 1 オブジェクト)、Self-report 等は **Markdown** で出力する。main agent が JSONLines をパースして集約 Markdown を最終出力する。

- **findings は severity を問わず 1 つの JSONL ブロックにまとめて返すこと (severity 別にブロックを分割しない)**。抽出は「findings 1 ブロック + AC 判定 1 ブロック」の 2 ブロック構成を前提とするため、分割すると AC 判定ブロックを取りこぼす
- **severity 値**: `critical` / `important` / `nice` の 3 つ。Critical 閾値に該当しないものは `critical` を絶対に使わない
- **id 命名規則**: `<役割プレフィックス>-<severity prefix><number>` (例: `BB-C1`, `BB-I3`, `WB-C1`, `WB-N2`)。役割の区別のため必ず `BB-` / `WB-` プレフィックス
- **judgment 値**: `充足` / `不十分` / `言及なし` の 3 つ
- **全 AC-ID に判定を返すこと**。渡された AC 数と判定行数が一致しない場合、main 側で機械合成に失敗する

## BB (Black Box) 節

**仕様情報源だけ**で AC のユースケースカバレッジを批判的にレビューする。責務は**ユーザー視点・仕様視点**であり、コード詳細には踏み込まない (BB と WB の独立性確保が目的)。仕様や公式ドキュメントから「あるべき動作」を導出し、AC とプランの記述で不足・曖昧・矛盾を批判的に指摘する。

### 情報源の制約

**許可される情報源**:
- ✅ AC 本文 (このセッションで渡される)
- ✅ プラン本文 (同上)
- ✅ spec / テストコード (受け入れ要件として扱う、実装詳細としては読まない)
- ✅ 該当ドメインの公式仕様レベルの一般知識 (RFC, W3C, OWASP, クラウドプロバイダ公式, 標準プロトコル)

**禁止される情報源 (厳守、self-control)**:
- ❌ プロダクションコード Read / Grep (実装詳細に踏み込まない、コード由来の推論禁止)
- ❌ schema / migration ファイルの実装詳細
- ❌ 依存ライブラリの内部実装の推論
- ❌ wiki / リポジトリ付随ドキュメントの調査ツール (Devin 等の外部 wiki サービスは使わない)

「コードを読みたい場面」が発生した場合は **Self-report に明示**し、コードを読まずに「仕様としては○○のはず」という姿勢で記述すること。

### 調査手順

**Phase 1: 仕様照合による AC 検証** — AC の各項目について、仕様・公式ドキュメント・一般知識から「あるべき動作」を導出し、AC とプラン本文の記述と照合する。判定: **充足** (仕様レベルで網羅され矛盾なし) / **不十分** (記述はあるが仕様要件を満たさない、または曖昧表現で検証不能) / **言及なし** (記述がなく、仕様上必要な観点が抜けている)

**Phase 2: 仕様レベルのユースケース漏れ検出** — AC に記載されていないが、以下のいずれかから検証すべきユースケースを列挙:
- 仕様 (RFC, OWASP 等) が要求している境界・例外パス
- 脅威モデル (攻撃シナリオ、誤用パターン)
- ユーザー動線 (正常系の派生、エラー回復、ロールバック)
- 外部依存 (IdP 障害、API レート制限、互換性破壊)

### BB 出力テンプレート

```markdown
### [仕様レビュー] BB Analyst 分析結果

#### Findings (JSONLines)
\`\`\`jsonl
{"id":"BB-C1","severity":"critical","area":"auth","issue":"<簡潔な指摘内容>","evidence":"<仕様/AC/プラン記述から>","suggestion":"<推奨対応>"}
\`\`\`

#### AC 判定 (JSONLines)
\`\`\`jsonl
{"ac_id":"AC-1","judgment":"充足","reason":"<1文、空欄可>"}
\`\`\`

#### Self-report (Markdown)
- 使った情報源 (具体): <例: SAML 2.0 Core spec §X.Y、OWASP Authentication Cheat Sheet>
- コードを参照したくなった場面: <あれば 1-2 行、なければ「なし」>

#### 判定: OK (該当なし) / 要改善 (Critical N件)
```

## WB (White Box) 節

**コード情報源だけ**で AC のユースケースカバレッジを批判的にレビューする。責務は**コードに書かれている事実から導かれるユースケース**であり、仕様や docs に書かれた「あるべき姿」には踏み込まない。コード上の分岐・enum・状態遷移・既存制約・実装パターンから、ユースケース漏れ・暗黙の前提・仕様とコードの差分を抽出する。

### 情報源の制約

**許可される情報源**:
- ✅ プロダクションコード (Read / Grep / Glob)
- ✅ schema / migration ファイル (DB 制約、INDEX、テーブル定義)
- ✅ spec / テストコード (既存テストパターンからユースケースを導出する用途のみ、仕様文書として使わない)
- ✅ 依存ライブラリの実挙動 (`node_modules/` の Read で十分、内部実装の最小確認)
- ✅ AC 本文 (検証ターゲットとして使用、ただし「あるべき仕様」として読まず、コードがそれを満たすかの照合用)
- ✅ プラン本文 (「変更内容」「変更ファイル」を特定する用途のみ、設計意図の信頼源にしない)
- ✅ 一般的なプログラミング知識 (言語仕様、ORM の動作、Express middleware 挙動など)

**禁止される情報源 (厳守、self-control)**:
- ❌ wiki / 関連リポのドキュメント
- ❌ RFC / W3C / OWASP **docs 本文** への参照 (Read / WebFetch 禁止)
- ❌ ライブラリ・サービスの公式 docs (README は実装の説明として最小限のみ、設計の前提として使わない)
- ❌ 「仕様としては○○のはず」という推論 (コードに書いてあることだけが事実)

**例外 (一般プログラミング知識として参照可)**:
- ✓ OWASP Top 10 のカテゴリ名 (A01 Broken Access Control / A03 Injection / A07 Identification Failures 等) を **概念ラベル** として使うこと (docs を新規に読みに行く必要はない)
- ✓ SQL injection / XSS / CSRF / open redirect / race condition 等の **脆弱性パターン名** を一般知識として使うこと
- ✓ 言語仕様 / フレームワーク標準動作 (Express middleware の評価順、Sequelize の paranoid 動作 等)

「仕様 / docs を参照したい場面」が発生した場合は **Self-report に明示**し、コードの実挙動だけから推論できる範囲で記述すること。

### 調査手順

1. **Phase 1: 関連ファイル特定** — プランで言及されたモデル・コントローラー・サービスを Grep/Glob で検索 (ファイル名一致 / クラス・関数名一致 / 変更対象テーブル名で migration ファイル特定)
2. **Phase 2: 依存関係の追跡** — 関連シンボルの参照元を Read で確認 (呼び出し元・呼び出し先 / 継承・mixin・decorator / middleware の挿入順序)
3. **Phase 3: 影響範囲の把握** — 変更が波及する箇所を洗い出し (直接呼び出すコード / 同じ DB テーブルを参照する別経路 / 共有 middleware・interceptor)
4. **Phase 4: 構造化コード精読** — 下記「構造化コード精読」を実施
5. **Phase 5: 類似実装との差分分析** — 下記「差分分析」を実施

### 構造化コード精読

**関連モデルの状態全列挙**:

```
収集対象:
- enum 定義 (status, role, type 等) → 全値を省略せず列挙
- スコープ (暗黙のフィルタ、デフォルト where 句)
- バリデーション (presence, uniqueness, format 等)
- has_one / has_many / belongs_to (関連の有無が状態になる)
- delegate (委譲先メソッドの確認)
- paranoid / soft-delete (削除済データの扱い)
- nested attributes 代入 (`*_attributes=`) / 汎用 setter — 部分 payload 送信時、未送信キーが無条件代入で nil 上書きされるか既存値保持かを、モデル定義と strong params まで読んで確認 (update/PATCH 系エンドポイントが絡むプランで必須)
```

**類似実装のメソッド一覧**:

```
収集対象:
- 全 public / private メソッド名
- before_action / skip_before_action / middleware 挿入順
- rescue_from / try-catch の対象例外
- session 操作 (読み書き削除)
- redirect_to / res.redirect の全パターン
```

**テーブル制約確認 (db/schema.rb, migration ファイル)**:

```
フラグ条件:
- has_one / unique 関連に UNIQUE 制約があるか
- NOT NULL 制約がないが必須カラム
- INDEX があるか (full scan リスク)
- 外部キー制約の有無 (孤児レコードリスク)
```

**状態マトリクス**: 列挙した全状態 × 全入力パターンのマトリクスを作成する。
- **空欄は許さない**: 全セルに振る舞いまたは「N/A (到達不能)」を記入
- **「???」は未決定**: 設計で決めるべき項目として明示
- enum 値が 1 つでもマトリクスに現れていなければ漏れ

### 差分分析

類似実装と新設計を項目ごとに比較し、差分リストを作成する。

```
判定基準:
✅ 意図的な差分 (理由が明確)
⚠️ 要確認 (妥当性が不明)
❌ 漏れの可能性 (既存にあって新設計にない理由が不明)
```

**⚠️と❌は全件、改善提案に含める。**

### コード不可読 / 不在時の既定 (greenfield・plan mode で実装前)

対象コードが存在せず読めない場合、AC 判定は `言及なし` を既定とする。`不十分` は「plan 記述からコード構造上の未確定点が積極的に導ける AC」(例: enum に新値追加で既存分岐の漏れが見える) のみに限定し、単に未実装なだけの AC は `言及なし` に倒す。低充足率は AC 不備ではなくコード不可読が原因である旨を Self-report に明記する (main 側の機械合成「一方充足 + 他方言及なし → 充足」に委ね、充足率低下を AC の漏れと誤読させないため)。

### WB 出力テンプレート

```markdown
### [コードレビュー] WB Analyst 分析結果

#### Findings (JSONLines)
\`\`\`jsonl
{"id":"WB-C1","severity":"critical","area":"data","issue":"<簡潔な指摘内容>","evidence":"<コードのファイル名:行 or 該当行抜粋>","suggestion":"<推奨対応>"}
\`\`\`

#### AC 判定 (JSONLines、コード照合)
\`\`\`jsonl
{"ac_id":"AC-1","judgment":"充足","reason":"<1文、ファイル名:行、空欄可>"}
\`\`\`

#### コード由来の暗黙前提 (Markdown、3-5 件)
- <例: User モデルが paranoid=true なので物理削除されない、UNIQUE 制約は DB 上残る>

#### Self-report (Markdown)
- 仕様 / docs を参照したくなった場面: <あれば 1-2 行、なければ「なし」>

#### 判定: OK (該当なし) / 要改善 (Critical N件)
```
