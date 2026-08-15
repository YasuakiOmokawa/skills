# build-prototype regression

Run each fixed scenario with a fresh executor. All `[critical]` items must pass.

## Complete PoC handoff

Input: a project plan contains the complete PoC→prototype handoff, a rough PoC, and an explicit target Git repository. The handoff requires lowercase tag normalization, `(untagged)` output, one command rather than two, and rejects SQLite/find-exec. The repository has observable placement, naming, layering, and test conventions but no remote.

1. [critical] Read and apply every handoff fact/rejection without asking for already supplied input.
2. [critical] Inspect real repository examples, state the conventions being followed, and rewrite rather than copy the PoC mechanism.
3. Preserve all grounded behavior and rejected boundaries; add the behavior-locking test to the repository's existing test route.
4. [critical] Commit on a new branch, handle the missing remote finitely without inventing a PR, and record branch/commit as the handoff location.
5. [critical] Upsert one exact `## 申し送り (プロトタイプ → DD)` section with location, conventions, decisions/rationale/rejections, PoC changes, scope-outs, and residual risks.

## Missing handoff section

Input: the same facts are distributed across the plan's ledger, notes, deferrals, and PoC; the canonical handoff heading is absent.

1. [critical] Reconstruct the canonical fields from those named sources without an approval loop or speculative facts.
2. Record the reconstruction with sources, then follow the same convention-driven implementation and verification path.
3. [critical] Preserve rejected alternatives and interaction findings, and produce one canonical prototype→DD handoff.

## Holdout: unavailable current gdocs snapshot

Input: the plan names gdocs as PRD source and says it changed, but the current environment cannot access gdocs and the earlier snapshot file is also absent.

1. [critical] Attempt no repeated fetch and do not pretend the earlier snapshot exists or is the freeze baseline.
2. [critical] Continue using available PoC evidence, explicitly recording source absence, alternative evidence, unverified scope, literal `DD正本: 未取得`, and a literal `DD前の解消条件` entry.
3. Follow repository conventions, verify the preserved behavior, and carry the source risk into the canonical handoff.
