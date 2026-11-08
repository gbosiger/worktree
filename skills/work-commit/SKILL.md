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

## Commit accepted work, retain records until integration

- Use `work commit [ID ...]` (toolkit: `./work`; installed: `./.workkit/work`)
  only for accepted `implemented` tickets. This is a Git action requiring explicit
  authorization, not part of acceptance. `work done` queues accepted work in
  implemented; `work commit` moves it to done without deleting it.
- Inspect staged changes first: the command commits ALL already-staged changes
  plus selected ticket moves to done. Stage only authorized work; never stage the whole
  board indiscriminately to bypass its unstaged-board guard.
- Without IDs it selects all eligible implemented tickets for the current branch;
  prefer explicit IDs for a bounded request. Containers include eligible queued
  descendants and retain already-done children, never implicit acceptance. An unset
  ticket branch uses the current branch, not the epic's branch.
- Preview with `work commit ID --dry-run`. A short subject (`feat:` for
  groups/epics/stories, `task:` for tasks) and one Markdown ID/title list replace
  embedded ticket payloads. Use `-m` only when an override is wanted. Exact
  accepted records stay in the feature's done folders. They are not selected again
  in later commit messages; never delete them during ordinary feature commits.
- Use `work merge ID` when explicitly authorized to integrate a fully approved,
  committed epic or group into its recorded local base. Both use an isolated/clean
  target worktree and leave the source unchanged. See docs/GIT.md's policy table:
  epic-to-WIP-group uses an explicit two-parent merge and retains done records;
  final-base integration squashes, then automatically commits separate cleanup.
  Do not accept unfinished containers to make merge proceed or clean up an
  intermediate group. Child integration does not accept its parent.
- Final integration and cleanup must remain two separate base commits. Never squash
  them together. Previously archived descendants are materialized recursively;
  lookup uses committed file history, not message payloads or markers.
  Before final group integration, ensure the accepted epic revisions have landed.
  Follow-up epic work requires reopening, re-approval, a new commit, and a WIP group;
  preserve sibling lifecycle state instead of restoring stale board copies.
- A failed merge/hook leaves its target worktree and journal for recovery. Resolve
  staged conflicts there, then use `work merge ID --recover`; never redo a
  successful integration or reset away its preserved tickets. Preview with
  `work merge ID --dry-run` before integration when useful. Existing standalone
  epic journals remain supported; do not delete an unfamiliar journal to retry.
- Never add `--push` without explicit publication authorization. It targets the
  configured upstream only. A failed push after local success is not a failed
  commit: report the OID and retry publication separately, not archival.
- For interrupted ticket commits, inspect the journal and use `work commit --recover` alone.
  Resolve a stale lock only after checking no command is running. Do not remove
  the journal or overwrite changed files/index to force recovery. Report any
  ambiguity for manual resolution; no automatic duplicate commit or ref rewind.
- After implementation, hand off into review per work-execute; neither archive
  availability nor a user's commit request authorizes acceptance or publication.
