---
description: Record explicit reviewer acceptance and complete a ticket
---

Use the work-execute skill to complete the selected ticket: $ARGUMENTS

Require an unambiguous ID, review status, checked acceptance items, the recorded
reviewer's explicit acceptance, and nonempty evidence. Ask for missing reviewer
acceptance/evidence; never invent it or auto-check criteria. The --by value must
match the recorded reviewer. Honor the CLI's dependency/child gates and any
requested dry run. Report status and current path. This moves accepted work into
the temporary done queue; it does not authorize a Git commit or publication.
