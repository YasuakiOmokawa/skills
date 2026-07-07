# Detection heuristics と common pitfalls

## Detection Heuristics

**重要**: 本セクションは Workflow Step 2「候補抽出」専用。パターンにヒットした語は **false positive を含む候補リスト**。実際の分類は Step 3 の決定木で行う (heuristic ヒット ≠ 自動的に要対応)。

target 文書から以下のパターンを候補としてリストアップ:

| パターン | 候補例 | typical false positive (Step 3 で「持ち込み可」に倒れやすい例) |
|---|---|---|
| カタカナ + 「型」「主義」「原則」「論」「系」 | `Provider 内吸収型`, `短絡型`, `Critical-A/D 系` | `Faraday 系` (gem 名 + 系)、`同期型/非同期型` (一般用語) |
| 強調された (`**...**` / 「...」) 専門フレーズ | `**Single Switch**`, `「Provider 内吸収型」` | 強調された codebase 識別子、見出し用の強調 |
| アルファベットラベル + 数字: `[A-Z]+-[0-9a-z]+` | `Critical-A`, `AC-12`, `α 層` 番号 | `XPROJ-663` (Jira ID)、`AUTH-203` (Jira ID)、`PR4-a` 等 (target 内で全展開済なら OK) |
| ギリシャ文字 + 「層/相」: `[α-ω]\s*層` | `α 層`, `β 層`, `γ 層` | 数学/物理文脈の正当な α/β 層 |
| section anchor: `§...` | `§設計詳細`, `§Single Switch` | (基本 false positive なし、target 内に該当 section があれば OK) |
| フェーズ分類用語 | `rollout enabler`, `enabler` | `kill switch` (英語圏で確立済)、`feature flag` 等 |
| 数字 + 「象限/層」 | `4 象限`, `3 層` (文中で各要素が説明されていない場合) | OSI 7 層など公知の分類 |

**heuristic ヒット後の方針**: 列挙された語は**全件 Step 3 へ渡す**。Step 3 の決定木で分類されるまで「要対応」と決めつけない。

### 参考 grep コマンド

```bash
# カタカナ造語パターン
grep -oE '[ァ-ヴー一-龥a-zA-Z]+(型|主義|原則|論|系)' <target>

# section anchor
grep -oE '§[^ ,。、）]+' <target>

# アルファベット + 番号ラベル (suffix は大文字も拾う: Critical-A / Critical-D 等)
grep -oE '[A-Z][A-Za-z]*-[0-9A-Za-z]+' <target>
```

## Common Mistakes

### ❌ 持ち込み可な codebase 固有名詞まで言い換えてしまう

**症状**: `Freee::Client` を「ライセンスクライアント」に言い換え。読者が grep できなくなり混乱が増す。

**修正**: class/file/Flipper flag 名は維持。読者は codebase で確認できる前提。

### ❌ in-line 定義を毎回繰り返して冗長化

**症状**: `Single Switch (Flipper 参照を 1 箇所に集約)` を出現箇所 3 回すべてに付ける。文書が読みづらくなる。

**修正**: 定義は **初出 1 回のみ**。2 回目以降は短縮形のまま使う。

### ❌ 番号ラベル / section anchor の機械的削除

**症状**: `§設計詳細` を機械削除。直前の「§設計詳細 を参照」が「を参照」だけ残り文として壊れる。

**修正**: 番号ラベル / anchor を削除する場合は**文単位で再構成**する。参照元が target に無いなら、参照先の要点を 1 文でインライン化するか、文ごと削除。

### ❌ source plan を未収集のまま target だけ点検

**症状**: target にある「Single Switch」が plan 内造語か codebase 由来か判別できないまま「要言い換え」に分類してしまう。

**修正**: source plan path を最初に確認。直前の Claude Code session で plan を扱っていれば `~/.claude/plans/<topic>/plan.md` を Read。見つからない場合の扱いは SKILL.md の「委譲実行 (subagent として起動された場合)」節の入力解決順位に従う。

### ❌ Dry-run なしで直接書き換え

**症状**: 候補語をいきなり言い換え → 「この語は意図的に使った」と後で指摘される。

**修正**: 必ず提案レポートを先に提示し承認を取る。
