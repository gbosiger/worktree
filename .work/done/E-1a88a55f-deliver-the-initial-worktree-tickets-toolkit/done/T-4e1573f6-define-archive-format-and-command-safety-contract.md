---
{
  "id": "T-4e1573f6",
  "kind": "task",
  "title": "Define archive format and command safety contract",
  "status": "done",
  "parent": "E-1a88a55f",
  "depends_on": [],
  "implementer": "agent",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Define archive format and command safety contract

## Purpose and scope

Agree on what happens to completed tickets before implementing file removal.
This ticket is the human review document; implementation details belong to the
dependent tasks, not a separate design document.

## Acceptance criteria

- [x] State when completed files are removed and what the commit preserves.
- [x] Define branch selection, preview, staged-change safety, and failure behavior.
- [x] Require history lookup, dependency checks, and reopening after removal.
- [x] Put implementation and verification responsibilities in dependent tasks.

## Proposal for review

1. `done/` is a temporary queue. Only accepted tickets can be archived; review,
   WIP, and backlog files stay. A child can leave without completing its parent.
2. An explicit `work commit -m SUBJECT` combines eligible completed tickets into
   one commit. A ticket's explicit branch must match the current branch; an unset
   branch means current branch, without inheriting from its parent.
3. The commit message preserves each ticket's full content, ID, metadata,
   criteria, and acceptance evidence in a versioned, machine-readable record.
   Successful archival removes those ticket files in that same commit.
4. Commit only already-staged implementation changes plus ticket removals.
   Preview IDs, staged changes, removals, and the message with `--dry-run`, without
   writes. Never stage unrelated work, switch branches, or push automatically.
5. Refuse unsafe or ambiguous states rather than guess. Failed commits preserve
   ticket content and the original index/worktree. If a commit succeeds but
   cleanup is interrupted, report that truthfully and provide safe recovery.
6. `show`, validation, dependencies, and reopening must understand records in
   reachable Git history before removals ship. Reopening keeps the same ID and
   past evidence; the live reopened ticket overrides its old completed status.
7. Preserve records through squash/rebase. Conflicting records or missing history
   are errors, never proof of acceptance. Keep everything local and dependency-free.

## Verification

Implementation order: codec/history (T-7147e599), lifecycle (T-0d73eaf7), safe
writer/recovery (T-2c08fd6d), end-to-end verification/docs (T-663511bc).
Encoding, conflicts, staging, hooks, concurrent edits, and crash recovery must be
tested by those tasks. Archive behavior is not implemented or runtime-verified.

2026-11-06: 30 unit tests pass; board validation passes with 31 tickets;
`git diff --check` passes. These validate the repository, not the planned writer.

## Handoff

Review the seven rules above and approve or request changes in this ticket.
No separate design-document review is needed. Epic E-1a88a55f stays WIP on
feature/E-1a88a55f-initial-toolkit; this task returns to review, with dependent
implementation paused. No human acceptance, archive implementation, or commit
is claimed.

## Acceptance record

2026-11-06T19:19:31+00:00 — human: The maintainer clarified in this conversation that moving these existing tickets to done was their approval, and requested staging, committing, and archival. This records that current confirmation for this already-done ticket; earlier handoff prose is retained as historical evidence, not backdated or replaced. Subsequent writer changes and compatibility limitations remain subject to T-2c08fd6d's separate review. No additional human test run is claimed.
