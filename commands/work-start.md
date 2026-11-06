---
description: Move a selected ticket into work in progress
---

Use the work-execute skill to start the selected ticket: $ARGUMENTS

Resolve the ID, read its parent and dependencies, and honor agreed ownership.
Ask if the ID or required roles are missing or ambiguous. Start only the selected
ticket, not all its children. Respect a requested dry run. Report the resulting
status, current path, and next action. Do not begin implementation, create
branches, commit, or publish unless separately requested.
