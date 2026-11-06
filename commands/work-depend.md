---
description: Add or explicitly remove a ticket dependency
---

Use the work-prepare skill to handle this dependency request: $ARGUMENTS

Resolve the dependent ticket and prerequisite IDs; ask if missing or ambiguous.
Read the selected tickets and relevant lifecycle rules. Use the CLI's depend
command, with --remove only when removal is requested. Honor cycle validation;
do not rewrite unrelated dependencies to bypass rejection. Validate the board
and report the actual result. Do not start or implement any ticket.
