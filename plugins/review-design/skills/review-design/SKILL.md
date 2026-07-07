---
name: review-design
description: Reviews code placement and pattern choices before implementation using selected architecture reviewers (anti-pattern plus DDD, Hexagonal, Clean, Deep-Module) and a mandatory adversarial critique, editing the plan directly on fatal findings. Use when starting a new feature, adding a file or module, designing a module's interface (deep vs shallow / where a seam goes), deciding "where should this code live", or when the user requests a design review with `/review-design`.
---

# review-design

実装前の配置・パターン判定を Q1-Q3 で選択された reviewer subset (anti-pattern 必須 + DDD / Hexagonal / Clean Arch 選択) で並列レビュー → 必須 Devil's Advocate critique → 致命指摘があれば plan ファイルを直接書き換える。

## Task complexity tier (skip / scope decision)

| Row | 状況 | アクション |
|---|---|---|
| 1 | 1 ファイル <50 LoC かつ既存 class 内部 method の追加・修正のみ かつ配置決定済み | **skip** (本 skill 不要) |
| 2 | ファイル追加 or 配置に迷う or 既存パターン拡張 | Quick Start (Q1-Q3) → matrix で reviewer subset 決定 |
| 3 | 新規 module / 複数 file 跨り / domain 跨り | Quick Start (Q1-Q3) でも **all 5 reviewers を default** |
| 4 | auth / billing / payment / migration / security (= **territory**, not keyword match) | 配置が自明でも本 skill 実行 + DA を subagent dispatch |

**Row 1 と Row 4 の precedence**: territory (semantic) 判定を優先 — substring match による誤 escalate を避ける。read-only predicate / getter (例: `def admin?; role == 'admin'; end`) のような **既存属性に対する判定 method 追加** は Row 4 territory に該当せず Row 1 で **skip 可**。新たな write path / 新規ガード (`before_action :require_admin!` 等) / 新規 callback (after_save で session/token 操作) を含む場合は Row 4 で **強制 exec**。判定不能なら Quick Start に進む。

**Row 3 と Row 4 の compound**: 両 Row が同時に該当する場合 (例: 新規 module + auth territory) は **superset を採用** — Row 3 の "all 5 reviewers default" と Row 4 の "DA subagent dispatch 強制" を**両方適用**する。reviewer 選択は all 5、DA は subagent (inline ではない)。Row 4 の存在が DA mode を inline → subagent に上書きする。

## Quick Start: 3 questions (Q1-Q3)

| Q | Answer | Next |
|---|---|---|
| Q1: Similar feature exists? | Yes → Q1.1 | (Q1.1 で healthy/unhealthy 判定) |
| Q1 | No | Go to Q2 |
| Q2: Responsibility statable in one phrase? | Yes | 1 file, go to Q3 |
| Q2 | "X and Y" | Split first, then Q3 |
| Q3: Testable (deps swappable)? | Yes | Proceed |
| Q3 | No | Inject via DI / args (matrix への影響なし、anti-pattern-checker の Leaky Abstraction / Feature Envy 検出に委ねる) |

#### Q1.1: 既存類似機能の健全性チェック (Yes 時のみ)

以下の **5 項目すべて** (AND) を満たす場合のみ **healthy**。1 項目でも違反すれば **unhealthy**:

1. tests が通過している
2. single responsibility (責務が一句で言える)
3. 行数 ≤200
4. public method ≤10 / callback chain <3
5. **after_commit / after_create 内で external API / 外部 IO を呼んでいない** (escape hatch 条件と一致)

**Greenfield (コード不在) の扱い**: 項目 1 / 3 / 4 (tests 通過 / 行数 ≤200 / public method 数) は実コードがないと検証できない。検証不能な項目は **not satisfied (違反) 扱い**とし、結果 unhealthy → all 5 reviewers に倒す (criticism-first default を保つため。greenfield は本 skill の主用途なのでこの分岐を必ず通る)。

**Escape hatch**: 1-4 を満たし healthy 寄りでも、項目 5 (after_commit 内 external IO) を含む場合は healthy を撤回 = unhealthy 扱い → all 5 reviewers。

- **healthy**: Follow that pattern. Run `anti-pattern-checker` only.
- **unhealthy**: Propose new pattern. Run **all 5** reviewers.

### Reviewer selection matrix (Q1 × Q1.1 × Q2)

Pick the first matching row, top-down:

| Q1 | Q1.1 health | Q2 | Reviewers |
|---|---|---|---|
| Similar | healthy | single | `anti-pattern-checker` |
| Similar | healthy | "X and Y" | `anti-pattern-checker` + `ddd-reviewer` |
| Similar | unhealthy | any | **all 5** (parallel) |
| None | — | complex business rules | `ddd-reviewer` + `anti-pattern-checker` |
| None | — | external deps (API/DB swap) | `hexagonal-reviewer` + `anti-pattern-checker` |
| None | — | new layered design | `clean-architecture-reviewer` + `anti-pattern-checker` |
| None | — | new module / interface 設計 (深さ・seam が論点) | `deep-module-reviewer` + `anti-pattern-checker` |

"All 5" = `anti-pattern-checker` + `ddd-reviewer` + `hexagonal-reviewer` + `clean-architecture-reviewer` + `deep-module-reviewer`.

**None ブランチの複数行が同時にヒットする場合** (例: 外部 API 依存 **+** 新規レイヤー設計 **+** 複雑な業務ルール): first-match で打ち切らず、該当行の reviewers を **union** する (anti-pattern-checker は常時含めるため上限は all 5)。理由: None ブランチの行は機能の独立した次元 (依存 / レイヤー / ロジック複雑度) で、現実の機能はそれらを compound する。

## Arguments & target resolution (Step 0)

- `$ARGUMENTS`: feature description (optional。プランファイルパスまたは自由文どちらでもよい)。`--strict-da` forces subagent DA.
- If empty: read `Plan File Info:` from context → Read plan file. Fall back to conversation context. **この 2 経路は単独起動時のみ有効** (委譲実行時の扱いは「## 委譲実行」参照)。
- feature description のみ (プランファイルパスなし) でも Step 1 以降は実行できる。プランファイルの有無は Step 4 (Edit 対象) と Step 6 (Write 先) にのみ影響する。
- プラン本文が PoC の仮説 ledger や「やらなかったこと→対応先」マッピング表を別ファイルで参照している場合は、そのファイルも Read する (Step 5 の grounding 材料として使うため)。

## Workflow

1. **Step 1-2**: Run Q1-Q3 → pick reviewers from the matrix.
2. **Step 3 — Parallel Review**: Dispatch selected reviewers via `Task(subagent_type="general-purpose")` in parallel. Each Task reads the corresponding `agents/*.md` and applies it. **Greenfield (まだコードが無い設計レビュー) の場合**: 各 reviewer の判定基準を Grep/Glob による反例検索ではなく、提案された構造への forward-looking な制約として適用する (本 skill は "starting a new feature" が主用途のため、コード不在でもレビューを成立させる)。Task が使えない場合の fallback、agent 定義中の `${CLAUDE_PLUGIN_ROOT}` の解決は「## 委譲実行」参照。
3. **Step 4 — Plan edit**: Integrate reviewer outputs. If issues found, **rewrite the plan file directly** with `Edit` (do NOT paste analysis summaries into the plan — modify the design itself). Do not emit a report here — flow into Step 5.
4. **Step 5 — Devil's Advocate (MANDATORY)**: Always run, even when all reviewers returned ✅ (reviewers each see only their own lens). Inline minimal recipe (default mode = main agent self-critiques):
   1. Produce **3 critiques from angles NOT in the Step 3 output** (repeating reviewer points is forbidden), attacking from operations (just-after-deploy / pre-retirement / incident) / scale (100x traffic or data) / cross-team-or-plugin interface / rollback cost.
   2. **Ground each critique in the actual code before labeling** (when existing code is available): Read the lines the critique depends on, or grep for a counter-example. A critique whose premise does not hold in the code (the claimed sink / caller / scope does not exist as described) is labeled `acceptable`, not `fatal` — ungrounded fatals have produced over-escalation and "fixes" that would break working code. Greenfield (no code yet): ground against the plan's stated structure instead. 会話文脈や隣接ファイルに PoC (使い捨て検証) の仮説 ledger (grounded/killed) や「やらなかったこと→対応先」マッピング表が存在する場合は、それも grounding 材料に含める。そこで対応済み・意図的 deferral と記録されている論点は対応先 (後続チケット等) が明記されているため `fatal` 化しない。
   3. **Label each critique `fatal` or `acceptable`** (fatal = `anti-pattern-checker` ❌ OR any single-trigger escalator [DB tx boundary / concurrency / security / contract breach]; subjective preference = acceptable). The fatal criteria are a closed set — a problem outside the checker's table and the four escalators stays `acceptable` + recommendation, however severe it looks.
   4. Surface 1-2 hidden assumptions.

   Escalate inline→**subagent dispatch** when **reviewers' ❌ ≥ 2, OR any single-trigger escalator hit (DB tx boundary / concurrency / security / contract breach), OR `--strict-da`** (full table = SSOT in [references/escalation-rules.md](references/escalation-rules.md)); full DA prompts in [references/reviewer-modes.md](references/reviewer-modes.md).
5. **Feedback loop**: If DA flags any "fatal" finding → Edit plan → re-run Step 3-4 → re-evaluate DA escalation. Repeat until all DA findings are "acceptable".
6. **Step 6 — Final report**: One-line-per-issue でチャットに表示する。加えて `Write` で `<plan>.design-review.md` (プランファイルパスの拡張子直前に `.design-review` を挿入したパス) へ同内容を保存する。保存内容・パス規則・プラン不在時の扱いは [references/final-report-format.md](references/final-report-format.md) を参照。

Three execution modes / DA escalation conditions / Fatal vs single-trigger 全表は [references/escalation-rules.md](references/escalation-rules.md) を参照。

## 委譲実行 (subagent として起動された場合)

Task ツールで委譲された場合、単独起動 (メイン会話でユーザーが直接起動) の動作に次を追加する。判定基準は「AskUserQuestion が利用可能ツールに無いか」で機械的に行う。

- **入力解決**: `Plan File Info:` と会話文脈は単独起動時のみ有効な経路であり、委譲時は試みない。起動プロンプト本文の明示指定のみを `$ARGUMENTS` として扱う。$ARGUMENTS からプランファイルパスも feature description も得られない場合のみ、「不足入力: レビュー対象のプランファイルまたは feature description」を最終メッセージで返し即座に終了する (返答を待たない)。
- **Step 3 の Task 不可時**: reviewer dispatch (`Task`) が利用可能ツール一覧に無い場合、main agent が [references/reviewer-modes.md](references/reviewer-modes.md) の Parallel Review fallback に従い `agents/*.md` を自ら Read して適用する。
- **Design It Twice (deep-module-reviewer escalation)**: [references/deep-modules.md](references/deep-modules.md) の問題空間提示 (Step 1) は、対話承認者がいない (= AskUserQuestion が利用可能ツールに無い) 実行では提示のみで確認を待たず、即座に Step 2 (sub-agent 並列起動) へ進む。
- **`${CLAUDE_PLUGIN_ROOT}` の解決**: `agents/*.md` を `Read` で直接実行しており本文中に `${CLAUDE_PLUGIN_ROOT}` が生文字列で残る場合、いま読んでいる agent ファイルの 1 階層上 (`skills/review-design/`) を skill root とみなして解決する。nested `Task` へ埋め込むパスは解決後の絶対パスにする。
- **完了報告**: Step 6 の最終メッセージ・保存ファイルの規定は [references/final-report-format.md](references/final-report-format.md) のとおり (委譲・単独起動で同一)。

## Quality standards

- **Criticism first** — default verdict is "there is a problem"。一貫性 (existing patterns) と最小構成 (minimum viable structure) は Q1 matrix と `anti-pattern-checker` が判定するため、ここでは再掲しない。

## Gotchas（観測済みの罠 — 実測で判明したものを 1 件 1 行で追記）

- 「## 委譲実行」の入力解決ルールは「$ARGUMENTS からパス文字列も feature description も得られない」場合のみを不足入力としているが、「パス文字列は渡されたが指す先のファイルが存在しない」場合も同じ即時終了 (内容を捏造せず、その旨を返して完結) として扱う。executor はこの区別を自己裁量で埋めて正しく処理したが、明文化はされていない。

## Advanced

- [references/escalation-rules.md](references/escalation-rules.md) — Three execution modes / DA escalation conditions / Fatal vs single-trigger 全表
- [references/reviewer-modes.md](references/reviewer-modes.md) — DA prompts (inline & subagent), feedback loop details, in-context fallback rules.
- [references/final-report-format.md](references/final-report-format.md) — Problem-free / problem-found templates, "1-issue-1-line" granularity, fallback tag examples.
- [references/detailed-workflow.md](references/detailed-workflow.md) — When Quick Start does not resolve the design (directory placement, dependency direction, pattern selection).
- Reviewer specs: `agents/anti-pattern-checker.md`, `agents/ddd-reviewer.md`, `agents/hexagonal-reviewer.md`, `agents/clean-architecture-reviewer.md`, `agents/deep-module-reviewer.md`.
- [references/deep-modules-quickref.md](references/deep-modules-quickref.md) / [references/deep-modules.md](references/deep-modules.md) — deep-module-reviewer の早見表 / 詳細 (用語・依存 4 分類・Design It Twice escalation)。
- [references/rails-patterns.md](references/rails-patterns.md) — Rails プロジェクトでの配置判断 (Model / Service / Form Object 等の第一候補表)。対象が Rails の場合、`anti-pattern-checker` の判定や [references/detailed-workflow.md](references/detailed-workflow.md) の配置場所決定で参照する。

## Companion skills

- `/define-acceptance-criteria` — define AC after design review, before implementation.
