---
name: review-design
description: Reviews architecture placement and pattern decisions before code is written, runs a Q1-Q3 selected subset of parallel reviewers (anti-pattern always + DDD / Hexagonal / Clean Arch as applicable) and a mandatory Devil's Advocate critique, and rewrites the plan file directly when reviewers or Devil's Advocate find issues. Use when starting a new feature, adding a file or module, deciding "where should this code live", or when the user requests a design review with `/review-design`.
---

# review-design

## Quick Start: 3 questions (Q1-Q3)

| Q | Answer | Next |
|---|---|---|
| Q1: Similar feature exists? | Yes → Q1.1 へ進む | (Q1.1 で healthy/unhealthy 判定) |
| Q1 | No | Go to Q2 |
| Q2: Responsibility statable in one phrase? | Yes | 1 file, go to Q3 |
| Q2 | "X and Y" | Split first, then Q3 |
| Q3: Testable (deps swappable)? | Yes | Proceed |
| Q3 | No | Inject via DI / args (matrix への影響なし、anti-pattern-checker の Leaky Abstraction / Feature Envy 検出に委ねる) |

#### Q1.1: 既存類似機能の健全性チェック (Yes 時のみ)

以下の **5 項目すべて** (AND) を満たす場合のみ **healthy** と判定。1 項目でも違反すれば **unhealthy**:

1. tests が通過している
2. single responsibility (責務が一句で言える)
3. 行数 ≤200
4. public method ≤10 / callback chain <3
5. **after_commit / after_create 内で external API / 外部 IO を呼んでいない** (= 後述 escape hatch 条件と一致)

- **healthy**: Follow that pattern. Run `anti-pattern-checker` only.
- **unhealthy**: Propose new pattern. Run **all 4** reviewers.

**Escape hatch (Q1.1 評価順序)**: 1-4 項目を満たし healthy 寄りでも、項目 5 (after_commit 内 external IO) を含む場合は **healthy を撤回** = unhealthy 扱い → all 4 reviewers。すなわち項目 5 は他項目と独立に致命的 (Q1.1 と escape hatch は **同じ判定基準を 1 つに統合**)。これにより「既存パターンが DA escalation conditions / Single-trigger escalators に該当しているのに healthy 判定されて誤誘導」を防ぐ。

### Reviewer selection matrix (Q1 × Q1.1 × Q2)

Pick the first matching row, top-down:

| Q1 | Q1.1 health | Q2 | Reviewers |
|---|---|---|---|
| Similar | healthy | single | `anti-pattern-checker` |
| Similar | healthy | "X and Y" | `anti-pattern-checker` + `ddd-reviewer` |
| Similar | unhealthy | any | **all 4** (parallel) |
| None | — | complex business rules | `ddd-reviewer` + `anti-pattern-checker` |
| None | — | external deps (API/DB swap) | `hexagonal-reviewer` + `anti-pattern-checker` |
| None | — | new layered design | `clean-architecture-reviewer` + `anti-pattern-checker` |

"All 4" = `anti-pattern-checker` + `ddd-reviewer` + `hexagonal-reviewer` + `clean-architecture-reviewer`.

## Arguments & target resolution (Step 0)

- `$ARGUMENTS`: feature description (optional). `--strict-da` forces subagent DA.
- If empty: read `Plan File Info:` from context → Read plan file. Fall back to conversation context.

## Workflow

1. **Step 1-2**: Run Q1-Q3 → pick reviewers from the matrix.
2. **Step 3 — Parallel Review**: Dispatch selected reviewers via `Task(subagent_type="general-purpose")` in parallel. Each Task reads the corresponding `agents/*.md` and applies it.
3. **Step 4 — Plan edit**: Integrate reviewer outputs. If issues found, **rewrite the plan file directly** with `Edit` (do NOT paste analysis summaries into the plan — modify the design itself). Do not emit a report here — flow into Step 5.
4. **Step 5 — Devil's Advocate (MANDATORY)**: Always run, even when all reviewers returned ✅. Reviewers see only their own lens; DA covers operations / scale / cross-team interface / rollback cost. Default mode is **inline default** (main agent self-critiques). Escalate to **subagent dispatch** under any of the 3 conditions in [references/reviewer-modes.md](references/reviewer-modes.md).
5. **Feedback loop**: If DA flags any "fatal" finding → Edit plan → re-run Step 2-4 → re-evaluate DA escalation. Repeat until all DA findings are "acceptable".
6. **Step 6 — Final report**: One-line-per-issue. See [references/final-report-format.md](references/final-report-format.md).

### Three execution modes (do not confuse)

| Mode | When | Final-report tag |
|---|---|---|
| **inline default** | DA escalation conditions NOT met (normal path) | none |
| **subagent dispatch** | DA escalation condition met (see below) | none |
| **in-context fallback** | Task tool unavailable (deferred / no dispatch perm) for reviewers OR DA | `(in-context fallback mode: <agent name>)` at report tail |

`inline default` ≠ `in-context fallback`. The tail tag is **only** for the environment-constraint fallback, never for normal inline DA.

### DA escalation conditions (machine-checkable)

Switch from `inline default` to `subagent dispatch` if **any** of:

1. Reviewers with `❌` ≥ 2 (across the 4 reviewer types)
2. **Single-trigger escalators** (any 1 hit forces escalation):
   - DB transaction boundary violation (external API in callback / multi-Aggregate write / missing saga)
   - Concurrency / idempotency defect (race condition / duplicate notify / multi-tab contention)
   - Security vulnerability (auth bypass / SQLi / XSS / CSRF / plaintext PII / IDOR / open redirect)
   - Existing contract breach (public API breaking change / SDK major version up)
3. `$ARGUMENTS` contains `--strict-da`

### Fatal vs single-trigger (separate concepts)

| Term | Used for | When |
|---|---|---|
| Single-trigger escalator | inline → subagent switch | after Parallel Review, before DA |
| **Fatal criteria** | DA classifying each finding as "fatal / acceptable" | during DA (inline or subagent) |

Fatal ⊇ single-triggers (4 above) **plus** `anti-pattern-checker` ❌ judgments. The latter is already surfaced by Step 3, so escalation handles it via the `❌ ≥ 2` route. Subjective preferences are "acceptable", not "fatal".

## Advanced features

- [references/reviewer-modes.md](references/reviewer-modes.md) — Mode definitions, DA prompts (inline & subagent), feedback loop details, in-context fallback rules.
- [references/final-report-format.md](references/final-report-format.md) — Problem-free / problem-found templates, "1-issue-1-line" granularity, fallback tag examples.
- [references/detailed-workflow.md](references/detailed-workflow.md) — When Quick Start does not resolve the design (directory placement, dependency direction, pattern selection).
- Reviewer specs: `agents/anti-pattern-checker.md`, `agents/ddd-reviewer.md`, `agents/hexagonal-reviewer.md`, `agents/clean-architecture-reviewer.md`.

## Quality standards

- **Consistency** with existing patterns
- **Simplicity** — minimum viable structure
- **Criticism first** — default verdict is "there is a problem"

## Companion skills

- `/define-acceptance-criteria` — define AC after design review, before implementation.
