---
name: work-commit
description: Prepare or make ticket-linked Git commits, feature branches, and merge summaries in projects using Worktree Tickets, when Git actions are requested or authorized.
---

References are relative to `.workkit/` when installed, otherwise the toolkit root.
Read `docs/GIT.md`, project instructions, the selected ticket, and its epic/group
description. Read `docs/FORMAT.md` only when changing ticket metadata, and
`docs/LIFECYCLE.md` only when changing status or evaluating acceptance gates.
Do not preload the convention index, unrelated references, or changelog.

- Before branch setup, staging, or committing, run
  `./.workkit/work preflight ID --for commit` (toolkit: `./work preflight ID --for commit`)
  and inspect the diff. This shares the execution-context check without treating
  accepted tickets as implementation targets. Consult docs/GIT.md for setup
  decisions. Stop on blockers such as another epic's branch; report the mismatch
  and obtain an explicit branch/worktree plan before edits.
  Do not make a ticket-linked commit on the wrong branch to hide a setup mistake.
- Preserve unrelated work; never stage everything
  indiscriminately, reset user edits, force-push, or switch away from uncommitted
  work without handling it safely. Do not assume a commit request authorizes a push.
- Preflight resolves the selected ticket's execution branch/base; do not
  substitute the current branch for missing metadata. Optional group branches are integration
  targets, not automatically required for release groups. Record the actual
  branch/base in metadata only after authorized setup succeeds. Status commands
  do not create branches. Branch/worktree creation, switching, stashing, and moving
  dirty changes require explicit authorization; a commit request alone does not
  grant them. If work is already mixed across epics, preserve it and propose a
  scoped relocation plan rather than staging it all. Rerun preflight after setup,
  before staging and before committing; it never authorizes Git mutations.
- Verify relevant checks and that ticket evidence accurately describes results.
- Use `type(scope): description [TICKET-ID]`. For multiple items use a Tickets:
  footer with every ID. Preserve IDs through squash/merge and PR summaries.
- Stage only intended code, docs, and ticket changes; inspect the staged diff.
  Commit only when authorized. A plain Git commit does not record acceptance or
  change ticket status; `work commit` moves already-accepted work to done.
- Report the resulting commit and checks. Never fabricate review, test, or merge
  evidence, and never publish without the user's authorization.

## Commit or integrate accepted work

- Preview the selected IDs with `work commit ID --dry-run`. The command includes
  **all staged changes** and moves selected implemented tickets to retained done
  records. With no IDs it selects the eligible branch queue. Inspect the staged
  diff and the preview paths before committing.
- For an authorized integration, use the policy table in `docs/GIT.md` and
  preview with `work merge ID --dry-run`. A child epic lands on its WIP group
  with records retained. Final integration preserves the complete ticket tree
  in the base commit before a separate cleanup commit.
- For an interrupted commit use the recovery instructions in `docs/GIT.md`
  and `work commit --recover`. For an interrupted integration use the saved
  target worktree and `work merge ID --recover`. Preserve the journal and
  concurrent edits. After a successful local commit and failed authorized push,
  report the commit and retry publication separately.
