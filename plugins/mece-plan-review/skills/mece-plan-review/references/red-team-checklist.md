# Red Team チェックリスト

メインエージェントの **Red Team Reviewer** が、BB Analyst と WB Analyst の分析結果を統合し、クロスリファレンス・お見合い検出・純技術リスク補完を行うためのチェックリスト。

Red Team は **fresh subagent** として起動され、プラン本文・AC 本文を持たない状態で、BB / WB 出力と本チェックリストのみを入力とする。

## 批判的レビュー姿勢

1. **「問題がある」前提で読め** — 穴を探せ
2. **重要度を分類**: 🔴 Critical / 🟡 Important / 🟢 Nice-to-have
3. **判定**: Critical 0件 → MECE OK、1件以上 → 要修正
4. **迷ったら問題側に倒す** — class / severity / お見合いの判定で確証が無い場合、立証責任は「問題なし」側に置く (表面的な整合は合意と扱わない)
5. **判定不能は Unknown で棄権** — 証拠が取れない項目は判定をでっち上げず、レポート Markdown 部の「判定不能 (Unknown)」に理由付きで明記して main agent に委ねる (0 件なら省略)。判別: 証拠が入力に存在するが弱い・相反する → 原則 4、証拠そのものが入力に無い → 原則 5

「最低 N 件出せ」のような件数縛りは**なし**。該当があれば指摘、0 件なら根拠 1 文で明示すること。

## Critical 閾値 (BB / WB と統一)

**判定の既定規則**: 「この欠陥は **それ単独で能動的に** 害を成立させるか? それとも害を **容易にする** だけか?」 — 成立させるなら Critical、容易にするだけなら Important。以下 4 類型に **現に該当** する指摘のみ Critical 認定:

1. **データロス / 破壊的変更** — 既存データの消失・不可逆な書き換え (部分 payload 送信による無条件上書き = nested attributes の未送信キー = nil 代入 を含む)
2. **能動的に成立するセキュリティ侵害** — それ単独で不正アクセス / データ取得 / 権限昇格が **成立する** 欠陥 (IDOR / SQL・command injection / 認証バイパス / mass-assignment 権限昇格 / stored XSS 等)。攻撃者が既に有効な認証情報・セッションを保持している前提でのみ害が成立・継続する欠陥 (例: パスワード変更後のセッション未失効) は、単独で成立させるのでなく容易にする側 = Important に分類する
3. **既存ユーザ動線の破壊** — 現行ユーザの操作が **不可** になる (遅延・文言品質の低下は含まない)
4. **ロールバック不能** — revert できない変更・削除不能な外部影響

**Critical でないもの (Important 以下に格下げ)**: hardening / 防御の多層化の不足で、それ単独では侵害が **成立しない** もの — rate-limit / brute-force 耐性・アカウントロック・監査ログ・強パスワード方針の欠如、機微情報の localStorage 保管 等。攻撃を容易にするが単独で害を成立させない。**性能劣化** (N+1 等) / **観測性 / i18n / polish** も Critical でない。「OWASP Top 10 に載るか」でなく「**それ単独で害が成立するか**」で決める。BB / WB が Critical タグで上げてきた指摘でも、上記に従い該当しなければ Important 以下に格下げすること (重複を統合する際の整理機会)。

## クロスリファレンス 4 分類 (主機能)

BB Analyst と WB Analyst の各指摘について、両者の言及状況で 4 分類する:

| BB 言及 | WB 言及 | 分類 | 意味 |
|---|---|---|---|
| ✓ | ✓ | **真の合意** | 両情報源で確認、信頼度高 |
| ✓ | — | **実装漏れ** | 仕様にあるがコードにない → Critical 候補 |
| — | ✓ | **仕様漏れ / 暗黙の前提** | コードに存在するが仕様未記載 → Critical 候補 |
| — | — | **お見合い** | 両者言及ゼロ。Red Team が独自検出すべき領域 |

### 4 分類判定の手順 (area タグ集約による機械化)

1. **area タグで集約**: BB / WB の全 Findings を `Area` 列でグループ化 (`auth` / `data` / `security` / `performance` / `observability` / `network` / `ui` / `deps` / `business` / `infra` / `その他`)
2. **同 area 内で BB↔WB pair 検出**: 同じ area に BB と WB の両方が指摘を出している場合、それらは「真の合意」または「補強し合う合意」の候補。Issue 本文の意味的一致で最終判定
3. **片側のみの指摘**: 同 area に BB のみ → 「実装漏れ」(コードに反映確認できず)、WB のみ → 「仕様漏れ」(コードの実装事実が仕様化されていない)。BB が**仕様自体の欠落**を指摘したケース (例: enum 未定義) も機械分類上は「実装漏れ」とし、content にその旨を注記する
4. **「真の合意」は両者の根拠を統合した 1 件にマージ** (重複カウントしない、両方の Evidence を併記)
5. **「お見合い」**: BB / WB のどちらも触れていない area を Red Team が次節の検出フローで埋める

### 「真の合意」と「偽の合意」の区別

両者が同じ Area で言及していても、根拠の出所が完全に同じ場合 (例: 両者とも AC の同じ行を指摘) は「真の合意」、根拠の層が異なる場合 (例: BB は仕様、WB はコード) は「補強し合う合意」として整理する。後者の方が信頼度が高い。

## お見合い検出 (両者言及ゼロの領域)

BB / WB のいずれにも言及がない領域を、以下のチェック観点から能動的に検出する:

**裏取り手段 (Read / Grep / Wiki) が全滅した area の扱い**: お見合い JSONL (M 行) は severity 必須のため、証拠ゼロのまま M 行を起票しない。代わりに MECE 判定の「判定不能 (Unknown)」行に area 名 + 棄権理由を書き、漏れ件数には数えない (severity 捏造と無言スキップの両方を防ぐ)。

### 事前分析チェック観点 (お見合い検出の起点)

1. **曖昧表現**: 「必要に応じて」「適切に」等の逃げ言葉が両者の指摘から見える領域
2. **責任の継ぎ目**: QA 的でも Arch 的でもない中間領域 (例: 運用手順、監視、ロギング)
3. **暗黙の前提**: 明示されず、成立しないと破綻する条件
4. **スコープ外だが影響を受ける領域**: プランは触れていないが連動する既存機能
5. **楽観的見積もり**: 「影響なし」「変更不要」の根拠不足

### 純技術リスク補完 (BB / WB の盲点になりやすい領域)

旧 Tech Analyst が見ていた領域のうち、BB (仕様) / WB (コード) のどちらにも入らない横断的観点を Red Team が補完する:

1. **セキュリティ (OWASP Top 10)** で BB / WB 双方が見落とした項目
   - A01 Broken Access Control (権限境界)
   - A03 Injection (SQL / XSS / Command)
   - A05 Security Misconfiguration (XML パーサ XXE、デフォルト設定)
   - A06 Vulnerable Components (依存ライブラリ CVE)
   - A07 Identification Failures (アカウント列挙、Replay)
2. **パフォーマンス**
   - N+1 クエリの可能性
   - INDEX 不足 (full scan リスク)
   - 接続プール枯渇
   - レート制限欠落 (DoS リスク)
3. **依存ライブラリ制約**
   - バージョン互換性 (breaking change)
   - CVE 履歴 (passport-saml, xml-crypto 等の特定ライブラリは過去 CVE 多数)
   - メンテナンス状況 (deprecated 検知)
4. **並行性 / 競合**
   - race condition (複数タブ・複数インスタンス)
   - 同時実行時の分離レベル
5. **観測性**
   - 構造化ログ・metrics・audit log 欠落
   - 個人情報の log マスキング

### 新機能ライフサイクル / クロス機能観点 (新機能の抜け漏れが偏在する)

新規 feature (リンク生成・スケジュール・トークン発行・共有 等) の抜け漏れは、**生成パスではなく「作った後どうなるか」と「依存する既存リソースが変化したとき」に偏在する**。BB は仕様の正常系、WB は生成時のコード構造に寄りやすく、この領域は両者の盲点になりやすい。以下 4 レンズを各々**明示的に**チェックする (汎用観点だけでは取りこぼす):

1. **ライフサイクル**: 作成後の各段が定義されているか — 有効期限 / TTL、取り消し・無効化・一時停止、再生成、削除時の挙動、終了条件。「作って終わり」でなく「**作った後どう畳むか**」を問う
2. **クロス機能相互作用**: 本機能が依存する既存リソースが変化したときの挙動が定義されているか — 対象の **削除** (孤児/dangling) / **更新** (内容変化で訪問者が見るのは live か発行時 snapshot か) / **可視性・権限変更** (後で private 化しても旧 grant が bypass し続けないか = authz staleness) / **所有者変更・所有者アカウント削除** (orphan 化)
3. **露出面**: 本機能が新たに公開する面の制御が定義されているか — 認証なしアクセス、URL、**検索エンジン/クローラの index 化** (noindex/robots)、キャッシュ、社外宛送信・第三者への拡散
4. **新露出の観測性**: 新しい露出・操作の **監査/追跡** (誰が・いつ・何に対して)、および失敗 / bounce の検知が定義されているか

### 必要に応じてコード裏取り

Red Team は fresh subagent だが、お見合い検出や純技術リスク補完で具体的な裏取りが必要な場合のみ Read / Grep を使用してよい (BB / WB の独立性は維持される、Red Team の追加検証は許容)。

## AC カバレッジ機械合成 (main agent が実施 / Red Team は介入しない)

BB / WB が返す「AC 判定」テーブルの AC-ID join と総合判定マージは **main agent が `references/synthesis-and-errors.md` Step 3-1 のマージルール (SSOT) で実施**する。Red Team はマージに介入しないが、以下の検証責務だけ負う:

### Red Team の AC マージ検証責務

- BB と WB の AC 判定行数が dispatch 時の AC 数と一致するか確認 (不一致は subagent 不全のシグナル)
- 同じ AC-ID で BB「充足」/ WB「不十分」のように判定が割れる場合、両者の根拠を見て「コード上未実装だが仕様上は意図あり」(= 実装漏れ Critical 候補) か「コード上は対応しているが仕様文言が曖昧」(= 仕様明確化 Important) かを判別

## 統合 Severity の決定ルール

BB / WB / Red Team 独自検出の各指摘について、統合 Severity を以下で決定:

- BB or WB のいずれかが Critical 認定 + 閾値該当 → **Critical**
- BB と WB が両方とも Important 認定 → **Important** (重複指摘の統合)
- BB or WB のいずれかが Important 認定、片方は言及なし → **Important** (片側補強)
- BB / WB のいずれも Nice-to-have → **Nice-to-have**
- Red Team お見合い検出 → 該当 Critical 閾値があるなら **Critical**、なければ Important / Nice-to-have

## 入力フォーマット

BB / WB Analyst の出力は **JSONLines** (findings + AC 判定) と **Markdown** (Self-report 等) の併用。本チェックリストは:

- findings JSONLines を `id`, `severity`, `area`, `issue`, `evidence`, `suggestion` フィールドで読み取る
- `area` フィールドで peer 候補を機械集約 (4 分類クロスリファレンス)
- AC 判定 JSONLines を AC-ID で join

## 統合評価レポートのフォーマット (JSONLines + Markdown 併用)

機械処理しやすさのため 4 分類クロスリファレンス / お見合い / 純技術リスク / 統合 Critical は **JSONLines**、人間可読の MECE 判定サマリーと Self-report は **Markdown** で出力する。

```markdown
### [Red Team] 統合評価レポート

#### 4 分類クロスリファレンス (JSONLines)
\`\`\`jsonl
{"id":"X1","area":"auth","bb_id":"BB-C1","wb_id":"WB-C2","class":"真の合意","severity":"critical","content":"<統合内容、両者の根拠を併記>"}
{"id":"X2","area":"security","bb_id":"BB-C2","wb_id":null,"class":"実装漏れ","severity":"critical","content":"..."}
{"id":"X3","area":"data","bb_id":null,"wb_id":"WB-C1","class":"仕様漏れ","severity":"critical","content":"..."}
\`\`\`

**class 値**: `真の合意` / `補強し合う合意` / `実装漏れ` / `仕様漏れ` の 4 値。「お見合い」は class フィールドに入れず、後述「お見合い検出 JSONLines (`M*`)」で別出力する (main agent 側で 4分類クロスリファレンス表に統合する手順は output-format.md 参照)。
**severity 値**: `critical` / `important` / `nice`。
**bb_id / wb_id**: 該当する BB/WB findings の id (`BB-C1` 等)。片側のみの場合は反対側を `null`。

#### お見合い検出 (JSONLines、両者言及ゼロの領域)
\`\`\`jsonl
{"id":"M1","area":"business","perspective":"暗黙の前提","content":"<発見事項>","severity":"critical"}
{"id":"M2","area":"observability","perspective":"責任の継ぎ目","content":"...","severity":"important"}
\`\`\`

**perspective 値**: 「事前分析チェック観点」の 5 値 (曖昧表現 / 責任の継ぎ目 / 暗黙の前提 / スコープ外 / 楽観的見積もり) のみ。**純技術リスク由来の発見 (セキュリティ / パフォーマンス / 依存ライブラリ / 並行性 / 観測性) は M ブロックに起票せず、次の「純技術リスク補完 (T)」ブロックへ振り分ける** (M と T は対象領域を排他にする。同一発見を両ブロックに二重起票しない)。

#### 純技術リスク補完 (JSONLines、お見合いの一部)
\`\`\`jsonl
{"id":"T1","category":"security","subcategory":"A07-Replay","content":"<発見事項>","severity":"critical"}
{"id":"T2","category":"performance","subcategory":"N+1","content":"...","severity":"important"}
\`\`\`

**category 値**: `security` / `performance` / `deps` / `concurrency` / `observability`。

#### 統合 Critical / Important / Nice (JSONLines、重複マージ後)
\`\`\`jsonl
{"id":"CR1","severity":"critical","title":"<統合タイトル>","sources":["BB-C1","WB-C2"],"suggestion":"<推奨対応>"}
{"id":"IM1","severity":"important","title":"...","sources":["BB-I3"],"suggestion":"..."}
{"id":"N1","severity":"nice","title":"...","sources":["M2"],"suggestion":"..."}
\`\`\`

**sources**: 統合元の id 配列 (BB/WB/M/T のいずれか)。

#### MECE 判定 (Markdown)
- 漏れ件数: N (お見合い検出された件数 = M1, M2, ... と T1, T2, ... の合計数。T は「純技術リスク補完」節の注記どおり、お見合いの一部として合算する)。判定不能 (Unknown) がある場合は `漏れ件数: N (+ Unknown K 件は未確定)` と併記する (棄権を「漏れゼロ」と誤読させないため)
- 重複件数: K (4 分類クロスリファレンスのうち class が `真の合意` または `補強し合う合意` の数)
- 判定: MECE OK / 要修正 (Critical N件)
- 判定不能 (Unknown): [証拠不足で class / severity を確定できなかった項目を理由付きで列挙。0 件ならこの行ごと省略]

#### AC マージ検証 (Markdown、不整合があるときのみ)
- BB / WB の AC 判定行数が dispatch 時の AC 数と不一致、または片側がまるごと欠落している場合、ここに「subagent 不全シグナル」として明記し main agent へ再取得を指示する (不整合 0 ならこのセクションごと省略)

#### Self-report (Markdown)
- 分析所要 (体感): <短>
- BB と WB の独立性の質: 高 / 中 / 低 + 1 文で理由
- プラン本文 / AC 本文を欲しいと思った場面: <あれば、なければ「なし」>
- 確信度: 高/中/低
```
