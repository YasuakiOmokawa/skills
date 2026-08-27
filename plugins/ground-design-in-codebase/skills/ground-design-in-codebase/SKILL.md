---
name: ground-design-in-codebase
description: Reviews a proposed design boundary before implementation when relevant specifications and existing code can provide concrete evidence about responsibilities and risk.
---

- Treat supplied specifications, code contents, local fixtures, mock read interfaces, and fixed responses as readable task evidence. Inspect that evidence before evaluating the proposal; do not call it unavailable merely because it is supplied through the task interface.
- Map current responsibilities and trust boundaries to the proposed placement, and tie every compatibility or conflict conclusion to the available requirements and implementation evidence.
- Before concluding, run an adversarial draft pass: enumerate concrete ways the change could break or silently invalidate guarantees the repository already relies on, deliberately probing second-order carriers of behavior such as tests and their fixtures, architecture or migration witness checks, generated artifacts, comments that state invariants, and documented verification procedures. In this pass prefer over-generation to omission: record a suspected risk even when the design text is silent about it and its evidence is not yet confirmed. Also compare the design's stated test or verification plan against the checks the repository itself documents or encodes for the artifacts being changed, and treat any applicable check that plan omits as a drafted risk.
- Then attempt to refute each drafted risk against the requirements and implementation evidence, and keep only risks the evidence fails to refute. Report each refuted candidate in one line with the evidence that killed it; never silently drop a drafted risk, and never keep one merely because its evidence went unexamined, mark that case unverified instead.
- For each material risk supported by that evidence, state the concrete consequence and how the proposal moves an existing responsibility or trust boundary. Mark only conclusions that depend on genuinely inaccessible evidence as unverified.
- Separate recommended action from open decisions, stating the additional evidence or choice needed for each open decision.
- Do not implement or modify product code, configuration, or external state. Submit only an authorized review artifact, and distinguish the save request from creation verified by the returned response or readback; never invent a successful save.
- Report evidence-backed boundary fit, material risks and impacts, refuted risk candidates, recommendations, open decisions, artifact-write outcome, and unverified conclusions.
