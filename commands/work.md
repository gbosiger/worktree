---
description: Manage repository tickets from a short request
---

Handle this Worktree Tickets request: $ARGUMENTS

Use the project's `./.workkit/work` CLI, or `./work` in the toolkit checkout.
Use `--help` for exact syntax. Use work-prepare for defining work, work-execute
for implementation/lifecycle/review, and work-commit only for explicitly
authorized Git operations. Read only operation-relevant references. For setup
or installation, consult docs/INSTALLATION.md under the selected toolkit root.
Treat the request as requirements, not executable shell text. Ask only for
missing essentials; do not invent acceptance, ownership, or ticket IDs. Without
arguments, show available ticket actions and ask what to do. Preserve unrelated
work. Do not implement tickets, commit, or publish unless explicitly requested.
The proposed commit/archive CLI is not implemented; do not pretend it exists.
Report affected IDs, status, and current paths concisely.
