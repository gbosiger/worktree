---
description: Reopen a ticket while honoring dependencies and ancestors
---

Use the work-execute skill to reopen the selected ticket: $ARGUMENTS

Ask for a missing or ambiguous ID. Inspect the ticket and affected prerequisites,
dependents, and ancestors. Use the CLI's reopen operation, respecting dry runs
and its completion/dependency gates. Preserve acceptance history. Do not silently
reopen unrelated work to bypass an error; explain any blocker. Report resulting
statuses and current paths. Do not implement, commit, or publish.
