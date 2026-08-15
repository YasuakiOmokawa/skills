# mece-plan-review regression

Run each fixed scenario with a fresh blank-context executor in an isolated fixture. Score written artifacts and dispatch inputs. All `[critical]` items must pass. Run the hold-out only after tuning and do not tune against its result.

## Standard: no Critical candidate

Input: complete AC/MECE analysis for a non-risk CSV formatting change, with upstream tier `lite`; code and specification support every AC.

1. [critical] Upstream lite is treated as standard, and BB/WB are executed inline with separated evidence sources.
2. [critical] Fresh Red Team is skipped because neither view finds a Critical candidate.
3. The analysis records `Critical: 0` and `漏れ件数: 0件 (Red Team skip のため未検出)`.
4. The plan receives only the canonical one-line MECE summary; findings and finding IDs remain in the analysis.
5. [critical] A rerun replaces the existing MECE result and summary rather than appending duplicate canonical sections or lines.
6. [critical] Tagged ACs that existed before the rerun retain tag metadata and receive normal three-value BB/WB judgments; only rows created after that run's analyst pass use synthesized `未判定` cells.

## Deep: auth change

Input: complete analysis for an authentication-state change with code available, at least one invariant AC, and at least one insufficient AC.

1. [critical] Risk forces deep; BB and WB run independently, then Fresh Red Team runs.
2. [critical] Red Team input contains only BB/WB findings and AC-judgment JSONL, never plan or AC text.
3. BB uses no code as evidence; WB uses no plan/specification claim as implementation evidence.
4. [critical] Expected `AC-1..N` IDs must each occur exactly once. After the shared retry, a role with at least one expected row drops unknown IDs and maps missing or duplicated expected IDs to one `言及なし` row each; a role with no expected rows becomes empty. Synthesis receives exactly N unique rows per usable role. With one empty role, it creates no synthetic JSONL, shows that role as `未取得`, derives every total from the usable role, and never classifies the absence as a gap. Both empty roles terminally stop the current pass before synthesis/write; a user-selected manual review starts a new pass.
5. [critical] Fenced JSONL with invalid JSON, missing required fields, invalid enums, or invalid ID formats shares the same one-retry-per-role budget as an AC-ID mismatch; a valid retry proceeds, while a second invalid result takes the finite fallback.
6. Output uses the canonical coverage, classification, severity, and one-line plan summary formats; the invariant AC remains categorized as `不変条件`.
7. A new AC is written only inside one of the five canonical categories and uses that category's upstream syntax after the `[MECE追加]` tag, including invariant and non-impact forms; an unclassifiable proposal remains Unknown and no out-of-section AC heading is created.
8. [critical] With one missing role, Red Team keeps usable-role findings but creates no gap X-row from the absent counterpart, records the exhausted role once in `AC マージ検証`, and requests no second retry.

## Fresh Red Team: Unknown boundary

Input: BB/WB JSONL has concrete billing findings and complete AC judgments. It contains no observability or unrelated-domain involvement signal. One billing classification lacks evidence needed to decide severity.

1. [critical] The billing item with missing necessary evidence is reported as Unknown with a reason, not assigned fabricated class or severity.
2. [critical] Observability and other uninvolved general areas are not emitted as Unknown, M, or T findings; they may be summarized once as review scope outside.
3. Cross-reference rows use only supported BB/WB relationships and the canonical JSONL fields.
4. Unknown is excluded from leak and Critical counts and is shown separately in the summary.

## Delegated input without analysis

Input: a noninteractive delegated run receives an explicit plan path, but the derived `<plan>.analysis.md` either does not exist or has no enumerable checkbox AC rows.

1. [critical] Return `不足入力: 受け入れ条件 (<absolute analysis path>) — /define-acceptance-criteria を先に実行`, then stop.
2. [critical] For either missing or zero-row input, do not fabricate ACs, dispatch reviewers, or write an analysis or plan summary.

## Hold-out: standard discovers billing risk

Input: upstream tier is standard, but WB code evidence shows that a display path overwrites a confirmed invoice cache and changes billed totals.

1. [critical] The standard result is discarded and the entire review is rerun as deep.
2. [critical] Billing involvement is the recorded escalation reason; BB/WB run independently and Fresh Red Team runs after them.
3. The billing defect is classified against the Critical contract without inventing evidence.
4. No stale standard summary remains in either artifact.
