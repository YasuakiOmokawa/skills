---
name: purge-private-vocab
description: Replaces private vocabulary in authorized reader-facing documents when supplied definitions make the intended meaning checkable for the target audience.
---

- Use the supplied definitions and document contents to identify every occurrence of every confirmed private term in scope, then submit all authorized replacements through the supplied document interface instead of stopping at replacement suggestions.
- Leave a term without a confirmed definition unchanged and report it as unverified rather than inferring its meaning.
- Verify each replacement in its surrounding sentence so the actor, condition, action, and domain meaning remain unchanged.
- Treat supplied editable fixtures, mock interfaces, and fixed write responses as observable task evidence. Distinguish a write submitted from content verified by its response or readback; a rejected or unobserved write is not a successful replacement.
- Limit replacements to authorized reader-facing documents. Leave code identifiers, public APIs, and other documents unchanged unless separately authorized.
- Report verified replacements, confirmed terms retained unchanged, undefined terms left unverified, and failed or unverified writes.
