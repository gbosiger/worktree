---
{
  "id": "S-c382b0f8",
  "kind": "story",
  "title": "Create or check out the branch when starting an epic or group",
  "status": "backlog",
  "parent": "E-f44b10c1",
  "depends_on": [],
  "implementer": null,
  "reviewer": null,
  "branch": null,
  "base_branch": null
}
---
# Create or check out the branch when starting an epic or group

A maintainer starting a grouped release currently has to coordinate Git and board changes by hand. They should be able to preview both before starting.

## Behavior

For example, a release group is WIP on `release/next`. The maintainer wants to start its search epic on `feature/search`. Preview should show `release/next` as the base. After setup, the search epic records those two branches and moves to WIP. The other epic is still in backlog and can later start from the same release branch. Reuse an existing feature branch at its current tip.

## Acceptance criteria

- [ ] Preview shows the branch and base. Opting in creates or checks out the branch and starts only that container.
- [ ] Two sibling epics can start on distinct branches based on their WIP group.
- [ ] When another worktree holds the target branch, setup identifies the conflict and the epic stays in backlog.
- [ ] Plain start moves the ticket without switching branches.

Requirements: [Branch setup on start](../../../../docs/requirements/terminal.md#branch-setup-on-start).

## Handoff

Choose the opt-in command syntax first. Coordinate suggestions with S-5299cba3 and history with S-56c90e4f.
