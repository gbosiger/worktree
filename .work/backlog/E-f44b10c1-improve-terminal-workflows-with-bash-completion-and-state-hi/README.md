---
{
  "id": "E-f44b10c1",
  "kind": "epic",
  "title": "Find, start, and track tickets from the terminal",
  "status": "backlog",
  "parent": null,
  "depends_on": [],
  "implementer": null,
  "reviewer": null,
  "branch": null,
  "base_branch": null
}
---
# Find, start, and track tickets from the terminal

A terminal user currently looks up ticket IDs, reconstructs state changes, and sets up epic branches in separate steps. They want relevant suggestions at the prompt, a readable history on the ticket, and a way to request branch setup when starting work.

## Scope and delivery

Bash completion is independently useful. History has its own first step: agree how events are written before recording them. The two opt-in actions cover starting on a branch and accepting eligible WIP directly. Exercise them with completion and history in the final walkthrough. A timeline viewer and support for additional shells are outside this epic.

Concurrent epic work on separate Git worktrees needs its own guide (T-d87dad08); branch setup on start is covered by S-c382b0f8.

Assess the Python module layout while touching these features. A documented decision to keep it intact is a valid result.

## Acceptance criteria

- [ ] Bash offers relevant IDs from the selected board.
- [ ] Opening a ticket shows when its recorded state changes happened.
- [ ] A maintainer can request branch setup when starting an epic or group and see the container move to WIP on the intended branch.
- [ ] An assigned reviewer can explicitly confirm acceptance of an eligible WIP ticket and see it move directly to implemented.

Requirements: [Verification](../../../docs/requirements/terminal.md#verification).

## Handoff

Confirm the dedicated branch, base, and roles. Bash completion and the history format can start independently.
