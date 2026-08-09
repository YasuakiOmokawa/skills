# Step 3 結果統合 + Error Handling

## Step 3-1: AC カバレッジ表の機械合成 + 全指摘の記録

### AC カバレッジ機械合成 (main agent)

1. BB が返した「AC 判定」テーブルと WB が返した「AC 判定」テーブルを AC-ID で join
2. 各 AC-ID について以下の **AC カバレッジ機械合成ルール (本ファイルが SSOT)** で総合判定 (判定値は 3 値文字列のみ: `充足` / `不十分` / `言及なし`、絵文字エイリアス禁止):
   - どちらか「不十分」 → **不十分**
   - 両方「言及なし」 → **不十分** (お見合い検出対象)
   - 少なくとも一方「充足」+ 他方「充足」or「言及なし」 → **充足**
   - 両ロール「充足」要件にしない理由: BB は仕様観点・WB は実装観点。片方が言及なしでも他方が充足なら「不十分」とは言えない。Red Team が独自に懸念を検出した場合のみ「不十分」に格下げする
3. 元 AC 文の「カテゴリ」(正常系/異常系/エッジ/非影響) を分析ファイルの AC セクションから補完
4. `references/output-format.md` のフォーマットで分析ファイルに記録

### 指摘の記録

Red Team の統合 Critical / Important / Nice-to-have を **分析ファイル** に記録:

- **🔴 Critical**: プラン内の該当箇所 (セクション名・内容) と推奨修正内容を併記
- **🟡 Important / 🟢 Nice-to-have**: 簡潔に記録

**severity は Red Team 出力をそのまま転記せず、main agent が Core rule 3 の Critical 決定規則 (「その欠陥が *それ単独で* 害を成立させるか」/ hardening 不足は Important) を適用して確定する。** MECE判定 は Critical 件数のみで決まるため、規則の適用者を置かないと判定が Red Team の裁量に丸投げされる (Red Team 自身も BB / WB の Critical タグを同じ規則で格下げする義務を負っており、main agent はその最終段)。格下げ / 格上げしたときは Red Team の元 severity と変更理由を該当行に併記し、後から監査できる形にする。

## Step 3-2: AC ブラッシュアップ

Red Team の 4 分類結果から AC 改善点を統合:

- **実装漏れ** (BB ✓ WB —) → 該当 AC を強調 + Critical 指摘。ただし red-team-checklist が「BB が**仕様自体の欠落**を指摘した」ケースを機械分類上 `実装漏れ` に寄せた行 (content にその旨の注記あり) は、強調対象の AC が存在しないため **AC 追加 (`[MECE追加]`) 側で扱う**。**severity が Critical 未満の実装漏れ**は指摘表 (Important / Nice-to-have) への記録に加え、必要に応じて既存 AC の補足 (無タグ) または `[MECE追加 変更]` で消化する (Critical 指摘・プラン修正推奨の対象にはしない)
- **仕様漏れ** (BB — WB ✓) → AC 追加 (`[MECE追加]` タグ)
- **お見合い** (両者言及なし、Red Team 検出) → AC 追加 (`[MECE追加]` タグ)

### 分析ファイル AC セクションへの操作分類 (output-format.md の 3 ケース表と整合)

| 操作 | タグ | 例 |
|---|---|---|
| 新規 AC 項目を追加 (仕様漏れ・お見合い・仕様欠落注記付きの実装漏れ から) | `[MECE追加]` | 該当カテゴリ内に新規行追加 |
| 既存 AC を **補足のみ** (元の文意を変えずカッコ書きで追記) | タグ不要 | 元の行末尾に `(...)` |
| 既存 AC を **書き換え** (元の文意を変える、実現不可能 / 曖昧 / 不十分の修正) | `[MECE追加 変更]` | 修正後の行頭にタグ + 修正理由併記 |

### 「補足」と「書き換え」の境界

元の文の主述が変わるかで判定する。

- 主述が同じで限定句や境界値だけが追加されるなら**補足**
- 主述や HTTP ステータス / I/O 値が変わるなら**書き換え**

## Step 3-3: MECE 分析結果セクション追記

`references/output-format.md` のフォーマットに従い、**分析ファイル**末尾に追記。

「各ロール出力 (JSONL)」セクションには `${BB_JSONL}` / `${WB_JSONL}` のみを `<details>` で格納する。元 Markdown 全文 (Self-report 等) は転記しない (分析ファイル肥大とコンテキスト保持コストの主因だったため廃止済み。詳細は output-format.md)。

## Step 3-4: プランファイルに 1 行サマリー追記

プランファイルの `## 品質検証` セクションに以下を追記する (セクション無ければ作成):

```markdown
- MECE判定: [OK (Critical: 0) or 要修正（Critical N件）] / Important [I]件 (うちAC反映 [R]件) → [分析ファイル名]
```

サマリー値の定義 (SSOT):
- `Critical N件`: 統合 Critical 指摘の件数 (severity Critical のみ)。Red Team 起動時は統合後の件数に main agent が Core rule 3 を適用して確定する
- `I` (Important): 統合 Important 指摘の件数。Red Team 起動時は統合後の件数、standard で Red Team を skip した場合は inline BB/WB の important findings に main agent が Core rule 3 (Critical 決定規則) を適用して確定した件数
- `R` (AC反映): `I` のうち、Step 3-2 の AC ブラッシュアップで `[MECE追加]` / `[MECE追加 変更]` 操作の起点になった件数 (機械集計: Step 3-2 で操作した AC 行の根拠 finding を数える)。無タグ補足のみで消化した finding は R に数えない。Critical 0 でも AC/プラン修正に至った実価値をサマリーに露出させる列で、体感検出率と実検出の乖離を防ぐ

AC カバレッジ・漏れ・重複・判定不能 (Unknown) などの詳細集計は、プラン 1 行サマリーには載せず**分析ファイルの分析サマリー行にのみ記録する** (定義は `references/output-format.md` の分析サマリー節)。

## Error Handling

### Analyst subagent 失敗

```
Task の戻り値がエラーまたはタイムアウト:
  → 該当ロールを [未取得] として記録
  → Red Team に「BB or WB のいずれかが取得できなかった」旨を伝え、残りの結果のみで Step 2 を継続
```

### Red Team subagent 失敗 (Task 不可時のフォールバックも兼ねる)

```
Red Team が失敗した場合、または Task (Agent) ツールが利用可能ツール一覧に無く nested dispatch 自体ができない場合:
  → メインエージェントが手動で BB+WB の結果を統合 (フォールバック)
  → 統合時は references/red-team-checklist.md のチェックリストを main agent 自身に適用する (Red Team の判定ロジックを代行)
  → 結果に [Red Team フォールバック] タグ付与
```

### プランファイル書き込み失敗

AskUserQuestion でパス確認を依頼する (委譲実行時の読み替えは [delegated-execution.md](delegated-execution.md))。

### 分析ファイル lock / non-git リポジトリ

- 分析ファイル書込み時に lock 検出 → 1 回リトライ、それでも失敗なら AskUserQuestion で対応確認 (委譲実行時の読み替えは [delegated-execution.md](delegated-execution.md))
- non-git リポ (`git remote get-url origin` 失敗) → `${REPO_NAME}` を「unknown-repo」として継続
