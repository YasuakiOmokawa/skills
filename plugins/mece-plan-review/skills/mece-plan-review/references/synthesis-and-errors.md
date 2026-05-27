# Step 3 結果統合 + Error Handling

## Step 3-1: AC カバレッジ表の機械合成 + 全指摘の記録

### AC カバレッジ機械合成 (main agent)

1. BB が返した「AC 判定」テーブルと WB が返した「AC 判定」テーブルを AC-ID で join
2. 各 AC-ID について `references/red-team-checklist.md` の「AC カバレッジ機械合成」ルールで総合判定 (判定値は 3 値文字列のみ: `充足` / `不十分` / `言及なし`、絵文字エイリアス禁止):
   - どちらか「不十分」 → **不十分**
   - 両方「言及なし」 → **不十分** (お見合い検出対象)
   - 少なくとも一方「充足」+ 他方「充足」or「言及なし」 → **充足**
3. 元 AC 文の「カテゴリ」(正常系/異常系/エッジ/非影響) を分析ファイルの AC セクションから補完
4. `references/output-format.md` のフォーマットで分析ファイルに記録

### 指摘の記録

Red Team の統合 Critical / Important / Nice-to-have を **分析ファイル** に記録:

- **🔴 Critical**: プラン内の該当箇所 (セクション名・内容) と推奨修正内容を併記
- **🟡 Important / 🟢 Nice-to-have**: 簡潔に記録

## Step 3-2: AC ブラッシュアップ

Red Team の 4 分類結果から AC 改善点を統合:

- **実装漏れ** (BB ✓ WB —) → 該当 AC を強調 + Critical 指摘
- **仕様漏れ** (BB — WB ✓) → AC 追加 (`[MECE追加]` タグ)
- **お見合い** (両者言及なし、Red Team 検出) → AC 追加 (`[MECE追加]` タグ)

### 分析ファイル AC セクションへの操作分類 (output-format.md の 3 ケース表と整合)

| 操作 | タグ | 例 |
|---|---|---|
| 新規 AC 項目を追加 (仕様漏れ・お見合いから) | `[MECE追加]` | 該当カテゴリ内に新規行追加 |
| 既存 AC を **補足のみ** (元の文意を変えずカッコ書きで追記) | タグ不要 | 元の行末尾に `(...)` |
| 既存 AC を **書き換え** (元の文意を変える、実現不可能 / 曖昧 / 不十分の修正) | `[MECE追加 変更]` | 修正後の行頭にタグ + 修正理由併記 |

### 「補足」と「書き換え」の境界

元の文の主述が変わるかで判定する。

- 主述が同じで限定句や境界値だけが追加されるなら**補足**
- 主述や HTTP ステータス / I/O 値が変わるなら**書き換え**

## Step 3-3: MECE 分析結果セクション追記

`references/output-format.md` のフォーマットに従い、**分析ファイル**末尾に追記。

各ロール分析詳細セクションには 3 つの `<details>` ブロックを置き、`${BB_RESULT}` / `${WB_RESULT}` / `${WIKI_RESULT}` の元 Markdown 全文をそのまま埋め込む。

## Step 3-4: プランファイルに 1 行サマリー追記

プランファイルの `## 品質検証` セクションに以下を追記する (セクション無ければ作成):

```markdown
- MECE判定: [OK or 要修正（Critical N件）] / ACカバレッジ [N]/[M] (うち[MECE追加] [X]件) / 漏れ [Y]件 / 重複 [Z]件 → [分析ファイル名]
```

サマリー値の定義 (SSOT):
- `N`: 充足判定の AC 数 (分子)。`[MECE追加]` 行は BB/WB 判定を経ていないため AC カバレッジ表では **BB / WB / 総合の 3 列すべて「未判定」** と表記し、分子 N には含めない
- `M`: 元 AC 数 + `[MECE追加]` 件数 (分母)。`[MECE追加]` は分母には入るが追加直後は未判定なので分子 N にはカウントしない
- `X`: `[MECE追加]` 件数 (M に含まれる内訳)
- `Y` (漏れ): Red Team が独自検出した `お見合い` の件数。**severity 問わず全件、ただし 1 件のお見合いを Critical に昇格させても M* で 1 件のみカウント (Y 内では二重計上禁止)**
- `Z` (重複): 4 分類クロスリファレンス表で **「真の合意」+「補強し合う合意」の合計件数**
- `Critical N件`: 統合 Critical 指摘の件数 (severity Critical のみ)。**Y と Critical 件数は独立に集計** (Critical 昇格お見合いは Y に 1 件 + Critical に 1 件カウントするが、両者は別軸の集計なので二重計上違反にはならない)

お見合い M* と AC カバレッジ表の関係:
- **既存 AC に紐付く** お見合い (例: AC-7「/admin/* 非影響」が両者言及なし) → AC カバレッジ表で総合「不十分」+ 4 分類クロスリファレンス表でも「お見合い」行として両方に出す
- **既存 AC に紐付かない** お見合い (例: Red Team 独自検出の rate-limit / cleanup 等) → 4 分類クロスリファレンス表のみに「お見合い」行として出し、`[MECE追加]` AC として AC カバレッジ表の末尾に追加する

`[MECE追加] [X]件` は品質指標 (詳細は `references/output-format.md`)。

## Error Handling

### Devin MCP 利用不可 / カレントリポ未収録 (即時 cutoff)

Step 0-4.5 の preflight (`read_wiki_structure` を 1 回だけ probe、`ask_question` 禁止) で判定:

```
ToolSearch("+fdev-devin") 失敗 OR read_wiki_structure が "Repository not found"/error/空
  → ${DEVIN_COVERAGE}=none
  → Wiki Researcher を dispatch しない (Step 1 は BB+WB の 2 並列)
  → ${WIKI_RESULT}="[Devin未使用] ..." を確定、BB は Phase 0 をスキップ
  → BB はローカル仕様 + 一般知識でフォールバック、結果に [Devin未使用] タグ
```

**遅延防止 (本 cutoff の主眼)**: 収録判定に `ask_question` / `generate_wiki` を使わない (Devin 調査セッション起動で分単位の遅延)。判定は軽量な `read_wiki_structure` 1 回に限定し、not found なら即打ち切る。preflight で `none` 確定なら Wiki Researcher subagent 自体を起動しない (slow path をそもそも踏まない)。

### Analyst subagent 失敗

```
Task の戻り値がエラーまたはタイムアウト:
  → 該当ロールを [未取得] として記録
  → Red Team に「BB or WB のいずれかが取得できなかった」旨を伝え、残りの結果のみで Step 2 を継続
```

### Red Team subagent 失敗

```
Red Team が失敗した場合:
  → メインエージェントが手動で BB+WB の結果を統合 (フォールバック)
  → 結果に [Red Team フォールバック] タグ付与
```

### プランファイル書き込み失敗

AskUserQuestion でパス確認を依頼。

### 分析ファイル lock / non-git リポジトリ

- 分析ファイル書込み時に lock 検出 → 1 回リトライ、それでも失敗なら AskUserQuestion で対応確認
- non-git リポ (`git remote get-url origin` 失敗) → `${REPO_NAME}` を「unknown-repo」として継続、Wiki Researcher は `[non-git: Devin 未使用]` で skip
