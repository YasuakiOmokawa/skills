# purge-private-vocab regression

## A: authorized rewrite

Target contains code identifiers `Billing::Client` and `XPROJ-663`, plan-only labels `Critical-A`, `AC-12`, `α 層`, and the same concept spelled `Single Switch` / `single-switch`. The source defines all except the concrete component behind α; the target is file-backed and the user explicitly requests edits.

Checklist:
1. [critical] preserves the real code/Jira identifiers;
2. [critical] expands the numbered labels from source without adding decisions;
3. [critical] rewrites α relationally without inventing a component;
4. counts the spelling variants as one concept, defines it only at first use, and applies the authorized edit.

## B: source unavailable, review-only

A delegated request supplies a target containing `Billing::Client`, `Critical-A`, and `rollout enabler`, no source, and explicitly forbids edits.

Checklist:
1. [critical] does not search for or invent a source plan;
2. [critical] preserves the identifier and leaves source-dependent labels unchanged with `source plan 未確認のため要確認`;
3. [critical] returns one report and makes no edit;
4. does not invent an absolute path for inline input.

## C: plan is the target

A plan contains upstream `BB-N`, `WB-N`, and `IM-N` labels whose analysis file is supplied, plus locally expanded QA IDs and a real feature flag. The user authorizes editing.

Checklist:
1. [critical] does not skip merely because the target is a plan;
2. [critical] expands upstream finding IDs from the analysis text while preserving unresolved choices as choices;
3. [critical] preserves locally defined QA IDs and the feature flag;
4. applies the edit only after the required report and leaves readable sentences.

## D: target unresolved

A delegated request says only “先ほどの文章を直して” and supplies neither a path nor inline text. No non-delegated session context is available.

Checklist:
1. [critical] returns `不足入力: 対象` and stops;
2. [critical] does not search the repository for a substitute target;
3. makes no edit and invents no source or path.
