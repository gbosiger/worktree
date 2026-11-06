---
{
  "id": "T-2c08fd6d",
  "kind": "task",
  "title": "Commit accepted tickets with safe archive removal",
  "status": "backlog",
  "parent": "E-0182afb4",
  "depends_on": ["T-0d73eaf7"],
  "implementer": "agent",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Commit accepted tickets with safe archive removal

## Purpose and scope

Add explicit work commit, combining accepted records and selected ticket
removals with the already-staged implementation snapshot. No push or branch switch.

## Acceptance criteria

- [ ] Select only accepted done tickets eligible for the current branch: explicit branch wins, unset branch falls back to current, and other branches/states remain untouched.
- [ ] Read-only --dry-run shows selected IDs, branch, staged changes, removals, and exact proposed message without changing files, index, history, or invoking write hooks.
- [ ] Successful execution preserves complete archive records and commits only the already-staged snapshot plus authorized ticket removals; unrelated unstaged content remains unchanged.
- [ ] Completed containers are removed only when safe for all descendants, including already archived children; active descendants cannot be swept away.
- [ ] Empty selection, detached HEAD, missing identity, conflicts, unsafe ticket staging, and stale selection produce actionable errors before destructive writes.
- [ ] Commit/hook failures preserve recoverable ticket content and the pre-command index/worktree state under the approved safety contract; report recovery steps for interruption.
- [ ] Tests verify exact staged bytes, branch selection, multiple tickets, dry-run snapshots, container removal, and injected commit/hook failures.

## Approach and decisions

Use the approved safety contract and shared codec/reader. Ship only after
T-0d73eaf7 so successful removal cannot break board lookup or validation.

## Verification

Use isolated repositories and local hooks; compare index, worktree, and HEAD
before/after dry runs and failures. Run all tests and board check.

## Handoff

Provide command examples, failure evidence, and any recovery limitations to the human reviewer.
