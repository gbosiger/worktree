---
{
  "id": "T-d87dad08",
  "kind": "task",
  "title": "Document concurrent epic work with Git worktrees",
  "status": "backlog",
  "parent": "E-f44b10c1",
  "depends_on": [],
  "implementer": null,
  "reviewer": null,
  "branch": null,
  "base_branch": null
}
---
# Document concurrent epic work with Git worktrees

Maintainers developing sibling epics in parallel need to keep each branch's work isolated without losing track of the shared group and its integration path. Add a practical guide for this workflow to `docs/GIT.md`.

## Scope

Build on the existing branch, preflight, and container-integration guidance. Use two sibling epics based on one WIP group branch as the worked example. Keep the focus on creating and using separate Git worktrees and coordinating branch-local ticket state; T-6bab2842 remains responsible for the broader terminal-workflow walkthrough.

## Acceptance criteria

- [ ] The guide gives runnable `git worktree` commands for two distinct epic branches based on the same group branch, and identifies which worktree to use for each epic's ticket and Git operations.
- [ ] The guide explains that a branch can be checked out in only one worktree and directs each epic's operations to its corresponding worktree.
- [ ] The guide explains that ticket state is branch-local, not live-synchronized between worktrees, and warns against concurrent edits to the same branch or ticket.
- [ ] The guide distinguishes `work start` from creating a Git worktree.
- [ ] The example shows how to check the selected epic's branch/base with `work preflight` and how accepted sibling epics flow back to the group through the documented integration process.
- [ ] Verify the commands in a disposable repository with two sibling epics and separate worktrees; record the checks performed and any limitations in the guide or handoff.

Requirements: [Branches and execution context](../../../../docs/GIT.md#branches-and-execution-context), [Integrate a container](../../../../docs/GIT.md#integrate-a-container).
