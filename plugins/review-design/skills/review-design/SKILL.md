---
name: review-design
description: Reviews a proposed design boundary before implementation when relevant specifications and existing code can provide concrete evidence about responsibilities and risk.
---

- Treat supplied specifications, code contents, local fixtures, mock read interfaces, and fixed responses as readable task evidence. Inspect that evidence before evaluating the proposal; do not call it unavailable merely because it is supplied through the task interface.
- Map current responsibilities and trust boundaries to the proposed placement, and tie every compatibility or conflict conclusion to the available requirements and implementation evidence.
- For each material risk supported by that evidence, state the concrete consequence and how the proposal moves an existing responsibility or trust boundary. Mark only conclusions that depend on genuinely inaccessible evidence as unverified.
- Separate recommended action from open decisions, stating the additional evidence or choice needed for each open decision.
- Do not implement or modify product code, configuration, or external state. Submit only an authorized review artifact, and distinguish the save request from creation verified by the returned response or readback; never invent a successful save.
- Report evidence-backed boundary fit, material risks and impacts, recommendations, open decisions, artifact-write outcome, and unverified conclusions.
