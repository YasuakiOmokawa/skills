---
type: llm
focus: {source: file, path: docs/design.md}
---
The document states that its evidence comes from the request text and local checks, and that no PoC or prototype result file exists. Pass if the document says its evidence source is not a PoC/prototype result file. Fail if it cites a poc.md or prototype file as its source, or says nothing about where the evidence came from.
