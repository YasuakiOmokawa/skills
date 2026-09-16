---
type: llm
---
The reply says that calling the store or building the index directly from handlers (the form shown in the PoC handoff) does not fit this codebase's layering, and that persistence access was placed in the service layer instead. It is fine if the agent chose the service layer from the start, as long as the reply gives the layering rule as the reason. Pass if both the misfit and the chosen placement are stated.
