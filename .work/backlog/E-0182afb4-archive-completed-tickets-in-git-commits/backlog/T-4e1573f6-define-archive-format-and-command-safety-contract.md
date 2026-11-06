---
{
  "id": "T-4e1573f6",
  "kind": "task",
  "title": "Define archive format and command safety contract",
  "status": "backlog",
  "parent": "E-0182afb4",
  "depends_on": [],
  "implementer": "agent",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Define archive format and command safety contract

## Purpose and scope

Specify the local archive contract before code starts removing completed tickets.
Keep the toolkit Python 3.10+ standard-library only and local Git operations explicit.

## Acceptance criteria

- [ ] Document a versioned, machine-readable commit-message record that round-trips IDs, all metadata including unknown keys, full prose, criteria, and acceptance records without delimiter ambiguity.
- [ ] Resolve commit-subject input, deterministic multi-ticket ordering, duplicate/reopened record precedence, and current-branch selection. Unset branch means current branch unless inheritance is explicitly agreed.
- [ ] Define safe handling of staged, partially staged, modified, and untracked ticket files, hooks, concurrent changes, and failure recovery without substituting unstaged implementation content.
- [ ] Define reachable-history lookup, squash/rebase record preservation, shallow/missing-history diagnostics, and the active-versus-archived identity model.
- [ ] Record resolved decisions in focused format/Git documentation; identify any remaining maintainer decision rather than declaring the contract ready with safety gaps.

## Approach and decisions

Start with docs/FORMAT.md, docs/GIT.md, and docs/LIFECYCLE.md. Include examples
usable by the later GitHub integration; do not introduce remote dependencies.

## Verification

Review representative single/multiple records, delimiter-like prose, Unicode,
reopening/rearchiving, and unsafe index states against the proposed contract.

## Handoff

Agent prepares the contract for human review. No implementation or acceptance claimed.
