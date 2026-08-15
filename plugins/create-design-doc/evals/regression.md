# create-design-doc regression

Run each fixed scenario with a fresh executor. All `[critical]` items must pass.

## Complete handoff and template

Input: a plan with `## 申し送り (プロトタイプ → DD)`, a prototype Git repository, and a DD template. The handoff includes one chosen design with rationale, one rejected alternative, one scope-out, and one unresolved prototype contradiction.

1. [critical] Read the handoff and implementation evidence before writing; do not invent missing facts.
2. [critical] Preserve every template heading, order, and number.
3. Put the grounded decision/rationale, rejection, scope-out, and unresolved contradiction in their owned sections without changing the plan.
4. Apply the named text-quality checks or their explicit fallback without changing template structure.
5. [critical] Save `dd_<project-directory-name>.md`, report its path and unresolved items, and finish at the DD boundary without waiting for human LGTM or starting downstream work absent a separate request.

## Missing handoff and template

Input: a prototype Git repository and project plan have no handoff section, and the configured template is absent.

1. [critical] Declare the template fallback and use exactly the six fallback sections.
2. [critical] Reconstruct decisions, rationale, rejection, and scope-out only from implementation/diff/history evidence; keep unavailable facts unresolved.
3. Do not write the reconstruction back to the plan.
4. Save and report the canonical DD path, then finish without an approval loop.

## Holdout: unavailable prototype PR

Input: the handoff names a remote PR, but network access and local prototype code are unavailable. The handoff itself contains a decision, rationale, and rejected option.

1. [critical] Continue from the handoff instead of stopping or fabricating PR evidence.
2. [critical] Mark code-dependent schema/details unverified and preserve the handoff's grounded decision and rejected option.
3. Preserve the supplied template structure and report the saved path plus missing evidence.

## Holdout: unresolved pre-DD condition

The canonical handoff contains `DD前の解消条件: current PRD snapshot required`, and available evidence cannot resolve it.

1. [critical] Return `不足入力: DD前の解消条件 (current PRD snapshot required)` and create no DD file.
2. [critical] In the paired resolved case, use the artifact that resolves the condition as PRD truth; use PR/diff/prototype only as implementation evidence.
3. [critical] Do not downgrade the gate to an ordinary unresolved DD section or start downstream work.
