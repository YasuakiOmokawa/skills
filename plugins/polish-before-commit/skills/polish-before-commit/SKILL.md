---
name: polish-before-commit
description: Auto-fixes convention and pattern-consistency issues, runs lint, and aggregates remaining judgment calls before stopping for the user (or, when explicitly delegated in orchestrated mode, escalating to a ledger and returning instead of waiting). Requires the Claude `feature-dev` plugin for the final review step and halts with install guidance when it is missing. Use when finalizing a branch, just before `git commit` or `/create-pr`, or whenever the user says "仕上げて" / "polish" / "コミット前チェック".
---

# polish-before-commit

**提案だけでなく、自動修正まで行う。** プロジェクト規約・パターン一貫性・impl/spec 整合 (現状 Ruby/RSpec の delegate/def 撤去後 dead-mock 削除のみ、TS/JS/Python は範囲外で skip) を点検し、Step 4 → 5 → 6 → 7 は順序固定で再評価ループ禁止。

**review-only モード (ファイル変更不可)**: user が「ファイル変更はしない」「レビューのみ」「他者の PR」を指示した場合は編集せず、auto-fix Step (4/5/6/7) は候補提示に留め各 Step を `[<Step>: review-only により提案のみ]` と報告する (`<Step>` は各 Step のレポート文言表のラベル: パターン一貫性 / lint / dead-mock 削除 / コメント改善)。実行するのは Step 0 (preflight) + Step 1 (規約収集) + Step 8 (最終レビュー) + Step 9 (集約)。対象が Ruby/TS/JS/Python 外 (Helm/YAML 等) の場合も Step 4/5/6/7 は言語スコープ外として skip し Step 8 中心で点検する (どちらも編集せず点検に倒す点は同じ)。明示指示が無い場合の一次検出は「## 委譲実行」節を参照。

**他者 PR の点検時の Step 9 読み替え**: 申し送りの採用判定は「`branch:` == 点検対象 (PR head ブランチ名)」で行う (カレントブランチ基準にすると自ブランチ宛の無関係な申し送りを混入させる)。自ブランチ宛の申し送りは採用もクリアもしない — Step 9 の申し送りファイル削除 (`rm`) は自ブランチのフロー最終段でのみ実行する。終了文言は「コミットへ進めますか?」でなく「レビュー点検完了。指摘一覧を確認してください」とする (commit する対象が無いため)。

**フロー最終段の役割**: この skill はフローの最後に置かれることを想定する。代表的な前段列 (可変) は `/simplify` → `/vercel-react-best-practices` → `/review-code-quality` → 本 skill だが、実運用ではこの間に `/vercel-composition-patterns`・`/express-intent-in-code`、文章チェーン (`/dry-ssot-text` → `/purge-private-vocab`) 等が挟まる場合がある。Step 9 で `/review-code-quality` からの申し送り (`.git/quality-review-handoff.md`) と本 skill の Manual Review Items を集約し、**末尾でユーザー判断が必要な項目を一覧提示してから止まる** (連続スキル実行で個別レポートが transcript に埋もれ握りつぶされるのを防ぐため)。

**Orchestrated モード**: ファイル存在からの推測では判定しない。呼び出し側（将来のオーケストレータ）が Task 起動プロンプトで「orchestrated モードで実行。escalation は `<path>` に記帳して続行せよ」のように明示指示した場合のみ発動する。指示が無い単独起動では現行動作（判断項目 1 件以上で停止しユーザーの明示指示を待つ）のまま進む。差分は Manual Review Items #4 (dead mock 部分削除) と Step 9 のみで、詳細は [references/orchestrated-mode.md](references/orchestrated-mode.md) を参照。

## 委譲実行 (subagent として起動された場合)

以下は、本 skill が `Task` で委譲された subagent として動く場合にのみ関係する読み替えである。判定はいずれも「利用可能ツール一覧」という観測可能な条件で行い、文字列一致による推測はしない。単独起動 (メイン会話でユーザーが直接起動) の現行動作はこれらの条件に当てはまらない限り変えない。

- **Orchestrated モード**: 発動条件・記帳先・記帳規則は上記「Orchestrated モード」段落と [references/orchestrated-mode.md](references/orchestrated-mode.md) が正本 (本節では繰り返さない)。
- **review-only の一次検出**: `AskUserQuestion` が利用可能ツール一覧に無く、かつ実行モードの明示指定 (review-only / orchestrated 等) も起動プロンプトに無い場合に限り、`git log -1 --format='%an'` と `git config user.name` を比較する。不一致なら review-only を既定にする (ユーザーに確認できない状況で他者のブランチを誤って auto-fix する事故を防ぐため)。一致する場合、または `AskUserQuestion` が利用可能な単独起動では、現行どおり明示宣言が無い限り通常モードのまま進む。
- **Task 不可時の fallback**: `Task` が利用可能ツール一覧に無い場合のみ、Step 3 (パターン一貫性の並列処理) は並列化せず main thread で順次処理し、Step 8 (最終レビュー) は同 Step 記載の fallback 手順に切り替える。

## Task complexity tier

| Tier | 判定 | 実行 Step |
|---|---|---|
| **lite** | 1 ファイル、diff <30 LoC (ファイル総行数でなく追加+削除行数)、規約 hit 0、Ruby delegate/def 撤去なし | Step 5 (lint) + Step 8 (final review) + Step 9 (集約) |
| **standard** (default) | 2-5 ファイル, 規約 hit 1-3 | Step 1-5 + Step 8 + Step 9 (Step 6/7 は条件 hit 時のみ) |
| **deep** | 6+ ファイル / 規約 hit 4+ / Ruby delegate or def 撤去あり / multi-language | 全 Step (1-9) |

**Step 0 (preflight)** は全 tier で最初に必ず実行する (`feature-dev` 未導入なら他の Step に入る前に中止)。**Step 1 (規約の収集) も tier 判定の前に全 tier で必ず実行**する (tier 判定基準の「規約 hit 数」は Step 1 の収集結果からしか得られないため)。上表の「実行 Step」列は **Step 0/1 通過後にどの検査・修正 Step (4 以降) を実行するか**を指し、lite でも Step 0/1 は飛ばさない。リスク領域 (auth / billing / payment / migration) は LoC によらず **deep**。

補足:
- **規約 hit 数**: Step 1 で収集した明文規約への一致件数のみを指す (Step 4 の既存パターン多数派逸脱は判定軸が別のため含めない)。Step 1 はリポジトリ内 `CLAUDE.md`/`rules` とグローバル `~/.claude/CLAUDE.md`/`rules` の両方を収集対象とするため、hit 数は両者を合算した件数で数える (起源による区別はしない)。
- **Step 4 / Step 7**: tier 表の「実行 Step」列に無い tier では、各 Step 固有の条件判定 (規約の有無等) より tier-skip を優先し `[<Step>: tier-{lite,standard,deep} により省略]` を出力する。Step 固有の条件不一致文言は、その tier の「実行 Step」列に含まれる場合のみ使う。
- **Step 6 (dead-mock 削除)**: Ruby PR で `delegate :X` / `def X` 撤去を含む場合のみ実行する。Step 4/7 と異なり tier 表の「実行 Step」列の記載に関わらず、条件一致で tier 問わず発火する。
- **Step 9 (判断申し送りの集約)**: Step 0 で中止した場合を除き、tier 問わず必ず実行する (フロー最終出力のため lite でも省略不可)。

## Manual Review Items (自動修正せず提案のみ → Step 9 で集約)

以下は本 skill が検出しても自動修正せず、Step 9 の「ユーザー判断が必要な項目」に集約する (auto-fix に入る前にこの分類を確定しておくため、Step 一覧より前に置く):

1. 設計判断: サービス切り出し / モジュール化 / 責務分離
2. 影響範囲調査: メソッド名・引数・戻り値の変更
3. ビジネスロジック: バリデーション追加 / 認可変更
4. Dead mock の**部分削除** (`receive_messages(a:, b:)` のうち一部 identifier だけ削除): 書換え候補を併記してユーザー承認後に編集 (Orchestrated モード時は削除せず、書換え候補を escalation ledger に保留として記帳する。[references/orchestrated-mode.md](references/orchestrated-mode.md) 参照)

## 現在の対象 (skill 読み込み時に自動取得)

!`git branch --show-current`

!`git diff --name-only origin/${BASE_BRANCH:-develop}...HEAD`

!`git diff --name-only HEAD`

!`git diff --name-only --cached`

!`(grep -q '"feature-dev@' ~/.claude/plugins/installed_plugins.json 2>/dev/null || ls -d ~/.claude/plugins/cache/*/feature-dev >/dev/null 2>&1) && echo 'preflight: feature-dev INSTALLED' || echo 'preflight: feature-dev MISSING'`

> 上 5 行は Claude Code が skill 読み込み時に実行し結果へ置換する (読み取り専用・冪等)。2-4 行目はそれぞれ ブランチ全体 / 未コミット (worktree) / staged 差分で、スコープ判定 (Quick start 1) に使う。失敗時のフォールバックは原因別: (a) 生コマンド文字列のまま見える (注入非対応環境) → Step 0 / Quick start 1 の同コマンドを Bash で実行。(b) `unknown revision` 等のエラー (base branch が develop でない) → 次の順で能動的に解決する (`/create-pr` Step 0b と同じ手順、`git remote show origin` 単独には頼らない — remote の HEAD symref が dangling だと `(unknown)` を返し base を特定できないため): ① `gh repo view --json defaultBranchRef --jq .defaultBranchRef.name` ② 失敗時 `git symbolic-ref refs/remotes/origin/HEAD --short | sed 's@^origin/@@'` ③ いずれも失敗なら `main` を既定にする。決定した値を `BASE_BRANCH=<base>` として以降のコマンドに指定して再実行する (以降の `${BASE_BRANCH:-develop}` はこの値を優先して使う)。

## Quick start

0. **preflight (全 tier 必須・最初に実行)**: `feature-dev` plugin (Step 8 の `feature-dev:code-reviewer` が依存) の導入を確認。未導入なら**インストール方法を提示して即終了**し、以降の Step を一切実行しない (下記 Workflow Step 0)。
1. 引数 `$ARGUMENTS` あり → そのファイルを対象。なし → `git diff --name-only origin/${BASE_BRANCH:-develop}...HEAD` (ブランチ全体) で取得 (0 件なら終了)。**ただしブランチ全体と未コミット+staged 差分が大きく乖離する長命ブランチでは、今 commit しようとしている未コミット+staged 差分 (冒頭 3-4 行目) を既定スコープにする** (本 skill は commit 直前の用途なので、過去コミット分まで巻き込まない。ブランチ全体を polish したい時のみ明示指定し、判断に迷えば user に確認)。
2. 規約を収集 (下記 Workflow Step 1) → 規約 hit 数 + ファイル数で tier 表の実行範囲を確定 → tier 対応 Step を順に実行。
3. 各 Step の結果を**文言バリアント表に厳密一致**させた最終レポートを返す (silent skip 禁止)。省略文言の使い分け: **tier 由来の省略**は `[<Step>: tier-{lite,standard,deep} により省略]`、**条件不一致由来のスキップ** (Step 6 の撤去なし等) は各 Step 固有のスキップバリアント文言を優先する。最後に Step 9 で `### ⚠️ ユーザー判断が必要な項目` を集約提示し、commit へ進まず判断を仰ぐ。

## Workflow

### 0. 前提 plugin チェック (preflight / 全 tier 必須・最初に実行)

本 skill は最終レビュー (Step 8) で Claude 公式 plugin `feature-dev` の `code-reviewer` agent を使う。**他の Step に着手する前に**導入を確認し、未導入なら自動修正を一切行わずインストール方法を提示して終了する (auto-fix を進めてから Step 8 で止めると、修正だけが宙に浮くため最初に fail-fast する)。

```bash
if grep -q '"feature-dev@' ~/.claude/plugins/installed_plugins.json 2>/dev/null \
   || ls -d ~/.claude/plugins/cache/*/feature-dev 2>/dev/null | grep -q .; then
  echo "feature-dev: INSTALLED"
else
  echo "feature-dev: MISSING"
fi
```

冒頭の自動取得に `preflight: feature-dev INSTALLED / MISSING` が出ていればそれを判定に採用してよい (bash 再実行は不要)。

- `INSTALLED` → `[preflight: feature-dev 導入済み]` を出力して Step 1 へ進む。
- `MISSING` → **ここで終了**する (Step 1〜9 を一切実行しない)。中止は「未到達」であり「到達したが省略」ではないため、Step 1-9 の skip 文言 (`[<Step>: …により省略]`) も Step 9 の集約も出力しない。出力は次の 2 つだけを**この順で**返す:
  1. Step 0 の中止レポート文言 (下表「未導入 (中止)」): `[preflight: feature-dev 未導入のため中止 (インストール方法を提示)]`
  2. 下記の**ユーザー向けメッセージ**。agent 自身は `/plugin` を実行せず提示するだけで、`# marketplace 未追加の場合のみ` のコメントも含め改変せず転記する (条件判断はユーザーに委ねる)。`/plugin` 行はユーザーが実行する独立コードブロックとして見せる:

ユーザー向けメッセージ (内容をそのまま提示):

⚠️ `feature-dev` plugin が未導入のため polish-before-commit を中止しました。Step 8 の最終レビューで Claude 公式 plugin `feature-dev` の `code-reviewer` agent を使います。以下で導入してから再実行してください:

```
/plugin marketplace add anthropics/claude-plugins-official   # marketplace 未追加の場合のみ
/plugin install feature-dev@claude-plugins-official
```

導入後にもう一度 `/polish-before-commit` を実行してください。

**Step 0 レポート文言** (2 バリアント、いずれかを必ず出力):

| 条件 | 文言 |
|---|---|
| 導入済み | `[preflight: feature-dev 導入済み]` |
| 未導入 (中止) | `[preflight: feature-dev 未導入のため中止 (インストール方法を提示)]` |

### 1. 規約の収集

```bash
find . -maxdepth 4 -name "CLAUDE.md" -type f 2>/dev/null
find . -maxdepth 5 -path "*/.claude/rules/*.md" -type f 2>/dev/null
```

加えて `~/.claude/CLAUDE.md` と `~/.claude/rules/*.md` も Read。抽出対象: コーディング規約 / 命名 / 禁止事項 / 推奨パターン / コメント原則。0 件なら以降の各ステップのフォールバック (スキップ + 文言明示) に従う。

**規約 0 件時の分岐**: Step 4 → 既存パターン多数決のみ (規約根拠なしの逸脱検出は行わない、文言 `[パターン一貫性: 違反なし]` を流用) / Step 7 → 即 `[コメント改善: スキップ（規約に原則なし）]` を出力。

### 2. 対象ファイル確定 / 3. 処理方式

Step 2 は Quick start の通り。Step 3: ファイル ≤ 5 は main thread で直接処理、> 5 かつ複数言語混在は `subagent_type: "general-purpose"` で並列 (規約・対象ファイル・[references/pattern-consistency.md](references/pattern-consistency.md) を渡す)。`Task` が利用可能ツール一覧に無い場合は並列化せず main thread で順次処理する (「## 委譲実行」節参照)。

### 4. パターン一貫性

対象ファイルの既存パターン分析 → 同一ファイル内混在検出 → 類似ファイル間不整合検出 → 規約整合性確認 → 既存パターンへ統一。

**統一先の優先順 (上から、一致したら止める)** — auto-fix の判断はこの順で確定する:
1. プロジェクト規約 (CLAUDE.md / rules) に対象パターンのキーワードを含む明示指定 → それに従う (多数派と競合しても規約が勝つ)
2. 同一ファイル内の多数派 (2/3 以上の出現) → それに合わせる
3. 同一ディレクトリの他ファイルの多数派 (5 割超) → それに合わせる
4. 上記で決まらない (同数 / 出現 1 件) → 自動修正せず Manual Review Items に統一先候補を列挙
5. 同種ファイル 0 件 (新規追加 only で比較対象なし) → 判定不能、`[パターン一貫性: 違反なし]`

言語別の混在しやすい観点 (Ruby の結果オブジェクト OpenStruct/Hash・inline/block rescue、TS の絶対/相対 import・type/interface 等) とファイル間整合 (認可チェック配置・トランザクション境界等) の網羅例は [references/pattern-consistency.md](references/pattern-consistency.md) を参照。

**4.6 同種違反の網羅確認 (必須)**: 1 ファイルでパターン違反を修正したら、変更ファイル群の他箇所に同じ違反が残っていないか `grep` で網羅確認し、見つけた違反は同時修正する。

- 検査コマンド汎用形: `grep -l '<違反パターン>' $(git diff --name-only origin/${BASE_BRANCH:-develop}...HEAD)`
- Step 5 (lint) が Step 2 で確定した変更ファイル群全体をカバーするため、4.6 で広げた範囲も自動再検証される。

**Step 4 レポート文言** (3 バリアント、いずれかを必ず出力):

| 条件 | 文言 |
|---|---|
| 違反 0 件 | `[パターン一貫性: 違反なし]` |
| 1 ファイル修正 + 他箇所 0 件 | `[パターン一貫性: N 件修正、網羅確認 OK]` |
| 複数ファイル同時修正 | `[パターン一貫性: N 件修正 (うち網羅確認発火 M 件)]` |

### 5. lint 自動修正 (言語別分岐)

| 言語 | コマンド |
|---|---|
| Ruby | `bundle exec rubocop ${files} --autocorrect-all` |
| TypeScript/JavaScript | `yarn eslint ${files} --fix` |
| Python | `ruff check --fix ${files}` または `black ${files}` |
| その他 (Go/Rust/Shell 等) | `Makefile` / `package.json` / `pyproject.toml` から lint タスク探索。なければ `[lint: 未定義言語のためスキップ（手動確認要）]` |

成功するまで最大 3 回繰り返す。3 回試行で解決しなければ手動対応として報告。

**順序保証**: Step 5 の auto-fix 差分は Step 6 / 7 の評価対象に含める (lint 結果を信頼)。Step 4 の再評価はしない。Step 4 → 5 → 6 → 7 で確定、逆順・再評価ループは禁止。

**Step 5 レポート文言** (5 バリアント、いずれかを必ず出力):

| 条件 | 文言 |
|---|---|
| 違反 0 件 | `[lint: 違反なし]` |
| 自動修正実施 | `[lint: N 件自動修正]` |
| 対象言語のツールが未導入/未設定 (依存関係・設定ファイル不在) | `[lint: ツール未導入のためスキップ（手動確認要）]` |
| 3 回試行しても解決しない | `[lint: 3 回試行で未解決、手動対応要]` |
| 表に無い言語 (その他行) | `[lint: 未定義言語のためスキップ（手動確認要）]` |

### 6. Dead mock 削除 (Ruby/RSpec)

詳細手順・スキップ条件・文言 4 バリアントは [references/dead-mock-removal.md](references/dead-mock-removal.md) に従う。要旨:

- 対象: impl 側で `delegate :X` / `def X` を撤去した PR の spec 残存 mock (`receive(:X)` / `receive_messages(X:)` / `instance_double(..., X:)` / `double(..., X:)`)。
- スキップ判定の優先順: ① `*.rb` なし / `spec/` なし → 対象外、② 削除 identifier 0 件 → 撤去なし。
- 削除単位: 単独 stub と「全 identifier が削除済の `receive_messages`」は auto、部分削除は Manual Review。
- 削除後は編集 spec 全件を `bundle exec rspec` で 0 failures 確認。失敗時は revert + 報告。

### 7. コメント改善

Step 1 で収集した規約テキストに「コメント」「comment」キーワードを含む節が**ある場合のみ**実施。なければ独自判断で追加・削除しない。先行パス (`/express-intent-in-code` や `/dry-ssot-text` 等) で判断済みの箇所は対象外とし、規約準拠の機械的観点のみに限定する。

**Step 7 レポート文言** (3 バリアント、いずれかを必ず出力):

| 条件 | 文言 |
|---|---|
| 規約に原則なし | `[コメント改善: スキップ（規約に原則なし）]` |
| 規約あり + 違反なし | `[コメント改善: 違反なし（規約適用済み）]` |
| 規約あり + 修正実施 | `[コメント改善: N 件修正（<規約根拠>準拠）]` (根拠は適用規約のファイル名) |

### 8. 最終レビュー

preflight (Step 0) で `feature-dev` の導入は保証済みのため、`code-reviewer` agent を直接呼ぶ:

```
Task(subagent_type="feature-dev:code-reviewer", prompt="変更ファイルの git diff をレビューし、バグ・規約違反を報告せよ")
```

直前に `/review-code-quality` と `/express-intent-in-code` が完了済みであれば、その旨と `quality-review-handoff.md` の既知 finding 概要を prompt に含め、未発見のバグ・規約違反へ焦点を促す (同種分析の重複を避けるため)。

Task ツールが利用可能ツール一覧に無い場合のみ、main thread で同等のレビュー (変更 diff のバグ・規約違反確認) を直接行い、`[最終レビュー: ... (fallback)]` と明示する (silent skip 禁止)。`feature-dev` 未導入は Step 0 で中止済みなので、ここには未導入状態で到達しない。

**review-only で他者の PR を点検する場合**: code-reviewer には PR head を展開した worktree (`gh pr checkout` または `git worktree add`) の絶対パスと base 読み替え後の diff を渡す。現在の worktree が PR head と一致しないまま実行した場合は、指摘の根拠行を PR head 側で再確認してから採用する (stale なローカル worktree の値を根拠にした誤指摘の実績があるため。`/review-code-quality` の「PR レビューモード」と同じ規則)。

**Step 8 レポート文言** (2 バリアント、いずれかを必ず出力):

| 条件 | 文言 |
|---|---|
| 指摘なし | `[最終レビュー: 指摘なし]` |
| 指摘あり | `[最終レビュー: 指摘 N 件 (内訳: バグ X / 規約違反 Y / その他 Z)]` |

内訳 3 分類の判定基準: **バグ** = 実行時に誤動作する欠陥 (誤った出力・例外・データ破損等)。**規約違反** = Step 1 で収集した明文規約との不一致。**その他** = 上記いずれでもない品質指摘 (デッドコード・命名・テスト不足等)。

### 9. 判断申し送りの集約 (フロー最終 / 全 tier 必須・ただし Step 0 中止時は実行しない)

このフローの**最終出力**として、ユーザー判断が必要な項目を 1 箇所に集約・提示してから止まる (Step 0 preflight で中止した場合はフロー自体が止まるため、この Step には到達せず集約も行わない)。連続スキル実行で個別レポートが transcript に埋もれ握りつぶされるのを防ぐ。

1. 申し送りファイルを読む (`--git-dir` でなく `--git-common-dir` を使う: `git worktree add` で作った linked worktree では `--git-dir` が worktree 固有ディレクトリを返し、main 側と共有の申し送りファイルを見失うため。通常の worktree では両者は同じ値になり挙動は変わらない):
   ```bash
   HANDOFF="$(git rev-parse --git-common-dir)/quality-review-handoff.md"
   [ -f "$HANDOFF" ] && cat "$HANDOFF"
   ```
   本 skill 実行前に外部診断ツール (react-doctor 等) の指摘が会話内で共有され、修正しきれず残った指摘がある場合は、その残存指摘も出所「外部診断ツール」として集約リストに追加する (修正済みの指摘は集約不要)。
2. ファイル先頭の `branch:` が現在のブランチ (`git branch --show-current`) と一致するもののみ採用。不一致なら stale として除外し `[申し送り: stale (別ブランチ) のため除外]` を 1 行明示。
3. 採用した申し送り項目 + 本 skill の Manual Review Items (前掲・tier 表直後) + **Step 8 (最終レビュー) の指摘のうち auto-fix されず残ったもの**を統合し、同一箇所の重複は 1 件にまとめる (Step 8 由来も次項の出所ラベルでは「polish 検出」に含める — review-code-quality からの申し送りと区別できればよく、出所を 3 系統に分けて併記する必要はない)。
4. 末尾に **`### ⚠️ ユーザー判断が必要な項目`** セクションを出力。各項目は `/abs/path:line` + 要約 + 出所 (review-code-quality 申し送り / polish 検出 / 外部診断ツール) + 推奨対応を併記。1 項目の形式例:

```
### ⚠️ ユーザー判断が必要な項目
1. `/repo/app/services/billing_service.rb:42` — 認可チェックを before_action へ寄せるか要判断 (出所: polish 検出) → 推奨: TeamsController と揃え before_action :authorize へ統一
2. `/repo/spec/models/user_spec.rb:88` — `receive_messages(a:, b:)` の `a:` のみ削除の部分 dead-mock (出所: polish 検出) → 推奨: `b:` を残す書換え案で承認後に編集
```
5. **一覧を提示したらここで本 skill は終了する。** agent 側から commit / `git add` / `/create-pr` を自発実行・提案しない (フロー開始時点で既にコミット / PR を指示済みなら、その指示に従ってよい)。**本 skill の後に外部診断ツール (例: `npx react-doctor`) を実行する場合は、その指摘は本 skill の集約一覧に含まれない** (本 skill 実行前に共有され修正しきれず残った指摘は Step 9 の 1. のとおり集約対象であり、この後実行ケースとは前提が異なる) — ユーザーが別途確認するか、ツール実行後に Step 8-9 だけ再実行して束ね直す。判断項目の有無で終了時の文言を分ける (自発 commit はしない原則はどちらも同じ):
   - **判断項目 0 件**: 質問形にせず「判断項目なし。コミット可能な状態」と完了報告して終了する (ユーザーの返答を待たない)。
   - **判断項目 1 件以上**: 現行どおり一覧を提示し「polish 完了。コミットへ進めますか?」と 1 文返してユーザーの明示指示を待つ。
   - **Orchestrated モード時**: 判断項目が 1 件以上でもユーザーの返答を待たず、一覧を escalation ledger に記帳したうえで完了報告して終了する。記帳内容は [references/orchestrated-mode.md](references/orchestrated-mode.md) を参照。
6. 提示後、申し送りファイルをクリアする (次フローに stale を持ち越さない): `[ -f "$HANDOFF" ] && rm "$HANDOFF"`

**Step 9 レポート文言** (2 バリアント、いずれかを必ず出力):

| 条件 | 文言 |
|---|---|
| 判断項目 0 件 | `[ユーザー判断項目: なし]` |
| 判断項目あり | `[ユーザー判断項目: N 件 (申し送り X / polish 検出 Y)]` |

## 前提 plugin

- **`feature-dev` (Claude 公式)** — Step 8 の最終レビューで `code-reviewer` agent を使う。未導入時は Step 0 (preflight) で中止し、`/plugin install feature-dev@claude-plugins-official` を案内する。

## 併用推奨 skill

- `/review-code-quality` — 設計レベルの品質課題を検出し、自動適用しない needs-judgment を本 skill へ申し送る (Step 9 で集約)
- `/create-pr` — Step 9 のユーザー判断が片付いた後にカレントブランチから PR を作成
