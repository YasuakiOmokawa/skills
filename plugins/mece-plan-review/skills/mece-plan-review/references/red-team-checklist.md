# Red Team チェックリスト

メインエージェントの **Red Team Reviewer** が、BB Analyst と WB Analyst の分析結果を統合し、クロスリファレンス・お見合い検出・純技術リスク補完を行うためのチェックリスト。

Red Team は **fresh subagent** として起動され、プラン本文・AC 本文を持たない状態で、BB / WB 出力と本チェックリストのみを入力とする (empirical 検証で「真にフレッシュな統合判定」が独自 Critical 検出力を持つことが確認されている)。

## 批判的レビュー姿勢

1. **「問題がある」前提で読め** — 穴を探せ
2. **重要度を分類**: 🔴 Critical / 🟡 Important / 🟢 Nice-to-have
3. **判定**: Critical 0件 → MECE OK、1件以上 → 要修正

「最低 N 件出せ」のような件数縛りは**なし**。該当があれば指摘、0 件なら根拠 1 文で明示すること。

## Critical 閾値 (BB / WB と統一)

以下のいずれかに該当する指摘のみ Critical 認定:

1. **データロス or 破壊的変更**
2. **セキュリティホール** (OWASP Top 10)
3. **既存ユーザ動線が壊れる**
4. **ロールバック不能**

BB / WB が Critical タグで上げてきた指摘でも、上記閾値に該当しなければ Important 以下に格下げすること (重複を統合する際の整理機会)。

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
3. **片側のみの指摘**: 同 area に BB のみ → 「実装漏れ」(コードに反映確認できず)、WB のみ → 「仕様漏れ」(コードの実装事実が仕様化されていない)
4. **「真の合意」は両者の根拠を統合した 1 件にマージ** (重複カウントしない、両方の Evidence を併記)
5. **「お見合い」**: BB / WB のどちらも触れていない area を Red Team が次節の検出フローで埋める

### area タグ集約の利点

- BB が `security: RelayState オープンリダイレクト` と指摘し、WB も `security: req.body.RelayState を無検証で res.redirect` と指摘 → area `security` で機械的に紐付け候補に → 「補強し合う合意」として 1 件に統合
- BB が `auth: SAML Replay` と指摘し、WB が同 area で言及なし → 「実装漏れ」候補
- BB / WB ともに `observability` 領域の指摘ゼロ → 「お見合い」候補 → Red Team が監査ログ・metrics の観点で能動検出

### 「真の合意」と「偽の合意」の区別

両者が同じ Area で言及していても、根拠の出所が完全に同じ場合 (例: 両者とも AC の同じ行を指摘) は「真の合意」、根拠の層が異なる場合 (例: BB は仕様、WB はコード) は「補強し合う合意」として整理する。後者の方が信頼度が高い。

## お見合い検出 (両者言及ゼロの領域)

BB / WB のいずれにも言及がない領域を、以下のチェック観点から能動的に検出する:

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

### 必要に応じてコード裏取り

Red Team は fresh subagent だが、お見合い検出や純技術リスク補完で具体的な裏取りが必要な場合のみ Read / Grep を使用してよい (BB / WB の独立性は維持される、Red Team の追加検証は許容)。

## AC カバレッジ機械合成 (main agent 側で実施)

BB / WB が返す「AC 判定」テーブル (AC-ID + 判定 + 理由) を main agent が機械的にマージして、統合 AC カバレッジ表を生成する。Red Team はこのマージに直接介入しないが、不整合があれば指摘する。

### マージルール

各 AC-ID について、BB 判定列と WB 判定列を見て総合判定を決定:

```
BB 判定 / WB 判定 (controlled vocabulary: `充足` / `不十分` / `言及なし` の 3 値のみ。✅/❌ 絵文字は使わない):
├─ どちらかが「不十分」 → 総合判定: 不十分 (要修正候補)
├─ 両方が「言及なし」 → 総合判定: 不十分 (Red Team お見合い検出対象)
└─ 少なくとも一方が「充足」、他方は「充足」または「言及なし」 → 総合判定: 充足
```

**両ロール「充足」要件にしない理由**: BB は仕様観点、WB は実装観点。片方が言及していなくても、もう片方が充足判定なら「不十分」とは言えない。Red Team が独自に懸念を検出した場合のみ「不十分」に格下げ。

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
{"id":"M1","area":"security","perspective":"純技術リスク補完","content":"<発見事項>","severity":"critical"}
{"id":"M2","area":"observability","perspective":"責任の継ぎ目","content":"...","severity":"important"}
\`\`\`

**perspective 値**: 「事前分析チェック観点」(曖昧表現 / 責任の継ぎ目 / 暗黙の前提 / スコープ外 / 楽観的見積もり) または「純技術リスク補完」(セキュリティ / パフォーマンス / 依存ライブラリ / 並行性 / 観測性)。

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
- 漏れ件数: N (お見合い検出された件数 = M1, M2, ... の数)
- 重複件数: K (4 分類クロスリファレンスのうち class が `真の合意` または `補強し合う合意` の数)
- 判定: MECE OK / 要修正 (Critical N件)

#### Self-report (Markdown)
- 分析所要 (体感): <短>
- BB と WB の独立性の質: 高 / 中 / 低 + 1 文で理由
- プラン本文 / AC 本文を欲しいと思った場面: <あれば、なければ「なし」>
- 確信度: 高/中/低
```
