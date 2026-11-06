---
{
  "id": "E-0182afb4",
  "kind": "epic",
  "title": "Archive completed tickets in Git commits",
  "status": "backlog",
  "parent": null,
  "depends_on": [],
  "implementer": "agent",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Archive completed tickets in Git commits

## Outcome and value

Maintainers and coding agents keep only active work as Markdown files, while
accepted ticket definitions and verification remain discoverable in Git history.
The done/ folders become temporary queues, not permanent archives.

## Scope

Included:

- An explicit `work commit` command with a read-only `--dry-run` preview.
- Combine eligible completed tickets into one commit-message body, commit
  already-staged implementation changes plus selected ticket removals, and
  archive the ticket content without leaving completed Markdown files behind.
- Preserve ID-based lookup, completion dependencies, and reopening after archive.

Excluded:

- Automatically staging unrelated implementation files, accepting unfinished
  work, switching/creating branches, pushing, or publishing.
- Implicit commits from lifecycle commands or a global archive service.
## Acceptance criteria

- [ ] Only accepted done tickets are eligible; backlog, WIP, and review tickets are never swept into an archive commit.
- [ ] An explicit ticket branch selects that branch; an unset branch uses the current Git branch. Eligible tickets for the current branch are combined in one commit; tickets assigned elsewhere remain untouched.
- [ ] `work commit --dry-run` previews selected IDs, branch, staged changes, removals, and the proposed message without altering files, the index, or history.
- [ ] The commit message preserves each selected ticket's ID, metadata, full prose, acceptance criteria, and acceptance evidence in a documented machine-readable format.
- [ ] Successful execution commits the already-staged changes and selected ticket removals together. Unrelated unstaged files and tickets remain unchanged, and no push or branch switch occurs.
- [ ] Empty selections, detached HEAD, missing Git identity, merge conflicts, and commit/hook failures produce actionable errors. A failed commit leaves ticket content recoverable and preserves the pre-command index/worktree state.
- [ ] Archiving children does not prematurely accept their parents or delete still-active descendants. Completed containers can be archived once all their children are complete, including children already archived.
- [ ] `show`, `check`, dependency validation, and ID uniqueness understand archived tickets reachable in the current branch's history. Reopening restores archived content to backlog, preserves historical acceptance, and honors dependent/ancestor reopening rules.
- [ ] Regression tests cover multiple tickets, explicit and fallback branches, dry runs, unrelated changes, failures, archived dependencies, container completion, and reopening. Focused docs, help, and skills describe the implemented workflow accurately.

## Stories and dependencies

Backlog tasks, ordered by explicit dependencies:

1. T-4e1573f6 — Define archive format and command safety contract.
2. T-7147e599 — Resolve archived records from reachable Git history.
3. T-0d73eaf7 — Preserve board validation and reopening after archive.
4. T-2c08fd6d — Commit accepted tickets with safe archive removal.
5. T-663511bc — Verify and document the local archive workflow.

Archive reading and lifecycle support precede writing/removal so archiving cannot
break board validation. Contract decisions remain review gates, not assumed answers.

## Decisions and open questions

- Roles explicitly requested: implementer agent, reviewer human.
- Keep the existing done transition and its acceptance gate; done/ is a staging
  queue until an explicit archive commit succeeds.
- Decide the exact message encoding, commit-subject input, and handling of
  pre-staged or partially staged ticket files before implementation. Never
  silently substitute unstaged implementation changes for the staged snapshot.
- Branch fallback currently means the current branch when the ticket has no
  explicit branch. Confirm whether inheritance from an epic/group is wanted
  before adding it; do not silently change selection semantics.
- Define required archive-record preservation through squash/rebase and the
  behavior of shallow clones or missing archive history. Report incomplete
  history rather than treating missing prerequisites as accepted.
- Current Git conventions and limitations: docs/GIT.md. Update lasting docs
  with approved archive-format and recovery decisions during implementation.

## Verification and handoff

Prepared in backlog only. No implementation, commit, or human acceptance is
claimed. Next action: agent prepares T-4e1573f6 for human review, then follows
the dependent implementation tasks. Child roles are agent implementer/human reviewer.
