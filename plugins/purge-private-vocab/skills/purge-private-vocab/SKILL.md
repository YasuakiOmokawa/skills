---
name: purge-private-vocab
description: Detects local-plan coinages, abbreviations, and number labels in reader-facing text and rewrites them so readers without the source plan can follow. Use after generating PR description, Jira ticket, design doc, RFC, reviewed code comments (plan-coinage residue left after implementation), or other reader-facing text from a local plan/spec file, when readers don't share the source plan, when a plan document itself must be checked because upstream analysis-file finding IDs (BB-N / WB-N / IM-N) leaked into it, or when the user says "造語チェックして" / "plan 用語を消して" / "PR 説明の語彙を点検して".
---

# Purge Private Vocabulary

ローカルプランの造語・略号・番号ラベル (`Single Switch`, `Provider 内吸収型`, `Critical-A`, `α 層`, `AC-12`, `§設計詳細` 等) が plan 由来の対外文書に持ち込まれる症状を検出し、読者が plan を持たない前提で書き換える。

**核心原則**: 「読者が source plan を持っていない前提で読み下せるか」。書き手 (AI 自身) が plan を読んだ状態で書くと無意識に plan 内造語を持ち込む。

## Task complexity tier

| Tier | 判定 | アクション |
|---|---|---|
| **lite (skip)** | target = plan そのもの / 読者全員が plan 共有済のチーム内資料 / API ref (codebase 直 map) | **skip** |
| **lite** | target ≤300 字 or plan-only 語ヒット ≤2 | 1-pass 直接修正 (dry-run レポート省略、Step 4 飛ばして Step 5 のみ) |
| **standard** (default) | 中規模 doc (PR description / Jira description 等、300-2000 字) | Step 1-5 全実行、dry-run レポート提示 → 承認後 Edit |
| **deep** | design doc / RFC / 公開資料 / 2000+ 字 | dry-run + 適用後の再読検証必須 + heuristics-and-pitfalls.md 全件チェック + 下記 **deep 必須前置**を Step 1 で実施 |

**plan そのものが target になる場合 (lite(skip) の例外)**: plan の読者 (チームメンバー / 将来の別エージェント) が持たない上流文書 (分析ファイル・MECE 結果等) 由来の語彙 — `BB-N` / `WB-N` / `IM-N` 等の finding ID — が plan に混入している場合は、plan 自体を target として検査する (skip しない)。このとき source = 分析ファイル、target = plan の多段連鎖として扱う (「分析ファイル → plan → 読者」で、plan は中間文書でも読者にとっては対外文書)。

**deep 必須前置** (Step 1 の入力収集を拡張):
1. **target の文構造を直読み**: `**用語**: 説明` のような Label vs Body 構造かを目視確認し、Label vs Body 分離ルートの適用可否を Step 3 までに確定する
2. **AC-* / Critical-* / RFC-* 等の ID 紐付け**: target に登場する全 ID (`AC-7`, `Critical-A` 等) を source plan / analysis ファイルから 1:1 で索引し、各 ID の元内容を「展開」または「文ごと削除」のどちらにするか Step 4 提案レポートに明記する
3. **layer label (α/β/γ 層 等) の対応コンポーネント名解決**: source plan から各 layer の実コンポーネント名 (Web / Service / Persistence 等) を引き、推測補完にせず実値で言い換える候補を Step 3 までに用意する。**実コンポーネント名を解決できない場合 (source plan 不在等) の扱いは Q4 の層ラベル規則を SSOT とする** (関係性ベースの一般表現への言い換え・捏造禁止はそちらに集約)

## Core Pattern: 3 分類

| 分類 | 例 | アクション |
|---|---|---|
| **持ち込み可** | Flipper flag (`fy26q3_ebis_client`)、class/file 名、Jira ID (`XPROJ-663`)、Issue 番号 (`#34074`) | **維持** |
| **要 in-line 定義** | 2+ 回登場する有用な短縮形 (`Single Switch`, `Provider 内吸収型`) | **初出箇所で `用語 (= 短い説明)` を補う** |
| **要言い換えまたは削除** | 1 回しか出ない造語、番号 (`Critical-A`, `α 層`, `AC-12`)、section anchor (`§設計詳細`) | **平易な日本語に書き換え、または文ごと削除** |

## Workflow

### 1. 入力収集

- **target**: 検査対象 (PR body、Jira description、design doc、レビュー済みコードのコメント 等)。ファイルパス or インラインテキスト
- **source plan**: target の生成元 (`~/.claude/plans/<topic>/plan.md` 等)
- **target が変更差分全体の場合**: コードコメント + 変更/新規 md ファイルをまとめて検査する用例では、対象ファイル一覧を確定したうえで出現回数 (Q4) を差分全体で通算してから判定する (ファイル単位に分割して数えると過小カウントする)。提案レポートは変更セット全体で 1 通に統合する。Task complexity tier の字数・ヒット数もこの集合 (変更後ファイルの該当箇所全体) で判定し、diff の追加行のみに限定しない (Q2 の self-contained 判定と同じ範囲で数える)。

コメントを書くか・名前/型へ移すかの判断は `/express-intent-in-code`、文面の原則は code-comments 系規約 (7原則) が担い、本 skill は plan 造語の除染のみを担う。

両方を Read。

### 2. 候補抽出

target 全文から下記の検出パターンにマッチする語を**全件**列挙する。heuristic ヒット ≠ 要対応で、分類は Step 3 で決める (false positive を含む候補リスト):

```bash
# カタカナ造語 (型/主義/原則/論/系)
grep -oE '[ァ-ヴー一-龥a-zA-Z]+(型|主義|原則|論|系)' <target>
# section anchor
grep -oE '§[^ ,。、）]+' <target>
# アルファベット + 番号ラベル (Critical-A, AC-12 等。suffix は大文字も拾う)
grep -oE '[A-Z][A-Za-z]*-[0-9A-Za-z]+' <target>
```

加えて目視で拾う: 強調フレーズ (`**...**` / 「...」)、大文字始まりの英語複合語 (`Single Switch` / `Dual Write` 等、強調の有無を問わない)、ギリシャ文字+層 (`α/β/γ 層`)、フェーズ用語 (`rollout enabler` 等)、数字+象限/層 (各要素が文中未説明のもの)。

パターン別の typical false positive とより広い grep 例は [references/heuristics-and-pitfalls.md](references/heuristics-and-pitfalls.md) 参照。

### 3. 分類 — 決定木

各候補語を**上から順に**当てはめる。最初にヒットした分岐で確定:

```
Q1. codebase identifier / 公開規格名 / 公知の Jira/Issue ID か?
  YES → 【持ち込み可】 (例: Freee::Client, fy26q3_ebis_client, JWT, RFC 7519, XPROJ-663)
  NO  → Q2

Q2. target 自身の中で**直近に定義/展開**されているか?
     (見出し直後の本文で挙動を平易に説明、bullet で全要素列挙、等)
  YES → 【持ち込み可 (target self-contained)】
  NO  → Q3

Q3. source plan にしか定義がなく、target の読者は外部リソースで辿れないか?
  YES → Q4 (要対応)
  NO  → 【持ち込み可】 (公知用語)

Q4. 番号/層ラベルか? (`Critical-A`, `α/β/γ 層`, `AC-12`, PR チェーン番号、分析ファイル由来 finding ID (`BB-N`/`WB-N`/`IM-N`) 等)
  YES → 【要言い換えまたは削除】 出現回数に関わらず実値へ言い換え (in-line 定義ルートには載せない。Core Pattern 3 分類表と整合)。**ただし target 自身の表・一覧で定義済みの `AC-N` / `QA-N` は Q2 (self-contained) で維持** (例: QA 手順表に全 QA-ID が展開されている plan)。**層ラベルで source plan が無く実コンポーネント名を解決できない場合**は target 文脈から導ける関係性ベースの一般表現 (例: 「後段の処理層」) に言い換え、具体名を捏造しない (tier 非依存で適用)
  NO  → 出現回数で分岐:
    2+ 回 → 【要 in-line 定義】 (初出箇所で `用語 (= 短い説明)` を補う)。**ただし初出が見出し / title の場合**は in-line 定義が不自然なため、Label vs Body の label 書換 (平易化) ルートに倒す
    1 回   → 【要言い換えまたは削除】 (平易な日本語に書き換え、または文ごと削除)
```

**Q1 判定**: codebase identifier = `git grep <語>` が 1+ ヒット、公開規格 = RFC/W3C/ISO/IETF 等、公知 Issue/Jira = 公開 tracker でアクセス可。Figma node-id (`1:2` / `123:456` 等) も Q1 維持 (Figma ツールで解決可能な識別子)。**非 repo / 未マージ flag で `git grep` 不能時**は、backtick 付き snake_case で文中に `Flipper flag` / `class` / `file path` と明示されている、または source plan にファイルパス/flag 記述がある語を codebase identifier とみなす。加えて `Provider` / `Adapter` / `Gateway` のような**一般的なソフトウェア構成概念**は、平易な言い換えがかえって曖昧化する場合、持ち込み可に倒してよい (読者が文脈で解せる一般語のため)。

**Q2 判定**: 見出し+直後本文に平易な説明があれば self-contained。ただし説明に plan 内造語がさらに混入していれば NO。定義が初出より**後**に置かれている (用語使用 → 後置説明の順) 場合は、**Q3 以降へ進まずこの時点で【要 in-line 定義】で確定**する (定義を初出へ `用語 (= 短い説明)` として移し、後置説明文は定義に吸収・削除。Q3 の「source plan にしか定義がない」判定に流すと target 内に後置定義があるせいで素通しになるため、木の分岐でなくここで短絡させる)。迷ったら「plan 未読の同僚が target だけ読み下せるか」を音読で確認。

**Q4 出現回数判定**: 表記ゆれ候補 (同一概念の異表記) を個別に数えると過小カウントし、2+ 回相当が 1 回判定に落ちて誤って【要言い換えまたは削除】に分類されうる。`grep -oE 'パタンA|パタンB'` のようにパターンを OR 結合してから合計を数える。

**Q4 で source plan (分析ファイル) が未提供の場合**: finding ID の原文を参照できないときは、target 文脈から復元できる範囲の展開案に「適用前に原文と照合」の注記を付けて提示し、実値を捏造しない (deep 必須前置の 1:1 索引と同じ原則を standard でも守る)。この照合注記付き修正を 1 件でも含む場合、**tier に関わらず Step 4 の提案レポート提示を省略しない** (lite の直接適用に乗せると、照合されないまま復元文が plan に書き込まれる)。

**Label vs Body 分離** (Q2 の partial 抜けに使う既定ルート): 構造が `**plan-only ラベル**: 平易な説明文…` の場合、ラベルは Q4 で「要言い換えまたは削除」、本文は維持。例: `**Single Switch**: Flipper の参照を 1 箇所に集約` → ラベルを `**Flipper 参照の 1 箇所集約**` に置換、本文は維持。

**§anchor が同一 doc 内の番号のみ見出しを指す場合の中間ルート** (例: `§詳細6` / `§4` で見出しが `## 6. サーバ通信` のように番号だけ): section は実在するので Q2 で素通しになりがちだが、番号だけでは参照先が即座に分からない。削除でも素通しでもなく、**見出しの節名を併記して self-contained 化する** (例: `§詳細6` → 「サーバ通信 (§6)」)。参照先が target に存在しない dangling anchor のみ Q4 で文ごと削除する。

### 4. 提案レポート (Dry-run、書き換え前)

書き換え前に提案レポートを提示し承認を取る。Q1–Q4 のどの分岐で分類されたかを併記:

```markdown
## 語彙チェック提案レポート

### 持ち込み可 (維持) — Q1 / Q2 該当
- (Q1) `fy26q3_ebis_client` (Flipper flag 名、codebase 検索可)
- (Q1) `XPROJ-663` (Jira ID)
- (Q2) `PR4-a/b/c/d` (target L12-L20 で全 PR が展開済)

### 要 in-line 定義 (2+ 回出現) — Q4 該当
1. **Single Switch** (3 箇所: L14, L42, L58)
   - 提案: 初出 L14 を `Single Switch (= Flipper 参照を 1 箇所に閉じ込める設計)` に変更

### 要言い換えまたは削除 (1 回出現または番号ラベル) — Q4 該当
1. `rollout enabler` (L18) → 「Flipper による本番経路切替を可能にする土台」に言い換え
2. `§設計詳細` (L33) → target に該当セクションなし、文ごと削除
```

「持ち込み可」セクションは reviewer 誤検出疑念回避のため、heuristic ヒットして Q1/Q2 で抜けた語と、heuristic 未ヒットだが疑われそうな公開語 (JWT, RFC, Express 等) を明示する。

**standard / deep tier ではこの提案レポートを完全提示してから適用に進む** (省略・即時 self-approve 禁止)。対話承認者の有無の判定基準と self-approve の可否は「[委譲実行 (subagent として起動された場合)](#委譲実行-subagent-として起動された場合)」節を参照。chain 実行 (`/dry-ssot-text` → 本 skill → `/polish-before-commit`) の「流れを止めない」圧力でレポート提示ごと省略するのが観測された失点なので、tier に関わらず提示は必ず行う。提示自体を省けるのは lite のみ。

### 5. 適用

承認後 (lite は Step 4 の dry-run を省略するため承認不要 — 直接適用してよい)、Edit で target に修正を適用。検証: 初出箇所のみ定義があるか / 削除した語の周辺文が文として成立しているか (主述破綻していないか) / 言い換え箇所が plan 未読でも読み下せるか **再読**。

適用後の最終メッセージには、適用した修正の一覧 (対象語 + 変更後の文言、行番号があれば併記) と対象ファイルの絶対パスを含める。縮退動作 (下記) に入った場合は、その旨と「要確認」に残した候補語の一覧も含める。

## 委譲実行 (subagent として起動された場合)

### 入力解決順位 (Step 1)
target・source plan とも、① 起動プロンプト本文の明示指定 (Task 委譲時はこれが一次情報源) → ② セッション文脈 (単独起動時のみ有効) → ③ `~/.claude/plans/<topic>/plan.md` 等のファイル探索、の順で解決する。①が具体パスを明示している場合、そのパスが実在しなければその時点で「見つからない」と確定する。②③は①が具体パスを示していない場合のみのフォールバックであり、①の具体パスが外れたことの埋め合わせとして別ディレクトリ・別ファイル名を探索する用途には使わない。

target が①〜③いずれでも見つからない場合は「不足入力: target」を最終メッセージで返して即座に終了する (返答を待たない)。

source plan が①〜③いずれでも見つからない場合、AskUserQuestion 相当の確認手段が無い実行文脈では停止して回答を待てないため、次の縮退動作に入る:
- Q1/Q2 だけで機械判定できる候補語 (codebase identifier・target 内で self-contained な語) のみ処理する
- Q3 以降の判定が必要な候補語のうち、Q4 の「層ラベルで source plan が無く実コンポーネント名を解決できない場合」規則 (関係性ベースの一般表現へ言い換え) または「Q4 で source plan (分析ファイル) が未提供の場合」規則 (照合注記付き復元) が明示的に対象とする語はそちらに従う。**この 2 規則のどちらにも該当しない語 (英数字ラベル・略称等) は**、持ち込み可/削除のいずれにも断定せず、提案レポートに「source plan 未確認のため要確認」と明記する
- 存在しないパスを推測して Read しない
- 縮退動作に入った旨を最終メッセージの冒頭付近で明示する

### 対話承認者の判定基準 (Step 4)
「対話承認者がいるか」は AskUserQuestion が利用可能ツール一覧にあるかで判定する。無い実行文脈 (大半の subagent 委譲) では、提案レポート提示後に承認待ちで停止せず、提示自体を監査痕跡として self-approve し Step 5 まで完了する。AskUserQuestion が使える単独起動時の現行動作 (承認を待つ) は変えない。

## Quick Reference

| 操作 | コマンド |
|---|---|
| 候補語の出現回数 | `grep -o '<語>' <target> \| wc -l` (`grep -c` は行数を返すため、同一行 2 回出現を 1 と数え違える) |
| codebase 検索 (Q1 判定) | `git grep '<語>'` |
| in-line 定義形式 | `<用語> (= <短い説明>)` を初出箇所のみに |

## Advanced

- [references/heuristics-and-pitfalls.md](references/heuristics-and-pitfalls.md) — 検出パターン全表 + grep 例 + Common pitfalls (codebase identifier の誤書換、in-line 定義の冗長化、anchor の機械削除で文破綻、source plan 未収集、dry-run 飛ばし)

## 併用推奨 skill

本 skill は以下が **ローカル plan を source とする対外文書**を生成した直後に組み合わせると効果が高い:

- `/create-pr` — plan から PR description を生成 → 本 skill で語彙点検
- `/create-jira-issues` — plan からチケット生成 → 本 skill で description を点検
- `/finalize-plan` — 計画完成後、対外公開する design doc に派生させる際
- `/mece-plan-review` — 分析ファイル由来の finding ID (`BB-N`/`WB-N`/`IM-N` 等) が plan 本文に混入した場合、本 skill が除染する (mece-plan-review が前段)
- `/express-intent-in-code` — 段4 ドメイン抽象での造語禁止原則と同じ思想。命名候補が plan 造語化していないかの相互参照に使える
- `/dry-ssot-text` — 同一文書内の重複集約 (本 skill とは独立した別目的)。表記ゆれの統一を先に済ませると本 skill の出現回数判定 (grep カウント) の精度が上がるため、`/dry-ssot-text` → 本 skill の順を推奨
