---
name: work-commit
description: Prepare or make ticket-linked Git commits, feature branches, and merge summaries in projects using Worktree Tickets, when Git actions are requested or authorized.
---

References are relative to `.workkit/` when installed, otherwise the toolkit root.
Read `docs/GIT.md`, project instructions, the selected ticket, and its epic/group
description. Read `docs/FORMAT.md` only when changing ticket metadata, and
`docs/LIFECYCLE.md` only when changing status or evaluating acceptance gates.
Do not preload the convention index, unrelated references, migrations, or changelog.

- Inspect Git status and the diff. Preserve unrelated work; never stage everything
  indiscriminately, reset user edits, force-push, or switch away from uncommitted
  work without handling it safely. Do not assume a commit request authorizes a push.
- Use the epic's recorded branch/base. Optional group branches are integration
  targets, not automatically required for release groups. Record the actual
  branch/base in metadata. Status commands do not create branches.
- Verify relevant checks and that ticket evidence accurately describes results.
- Use `type(scope): description [TICKET-ID]`. For multiple items use a Tickets:
  footer with every ID. Preserve IDs through squash/merge and PR summaries.
- Stage only intended code, docs, and ticket changes; inspect the staged diff.
  Commit only when authorized. A commit does not itself mean accepted or done.
- Report the resulting commit and checks. Never fabricate review, test, or merge
  evidence, and never publish without the user's authorization.
