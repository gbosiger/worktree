---
{
  "id": "S-5299cba3",
  "kind": "story",
  "title": "Complete work commands with relevant board ticket IDs",
  "status": "backlog",
  "parent": "E-f44b10c1",
  "depends_on": [],
  "implementer": null,
  "reviewer": null,
  "branch": null,
  "base_branch": null
}
---
# Complete work commands with relevant board ticket IDs

A contributor working several directories below the board wants to send a ticket to review without opening a second terminal to look up the ID.

## Behavior

After typing a prefix for the review command, they see matching WIP tickets from the nearest board. When the ticket enters review it disappears from those suggestions and becomes eligible for the ordinary done suggestions. An explicit root selects a different board. A missing or unreadable board should leave the shell usable.

## Acceptance criteria

- [ ] From a nested directory, review suggests WIP tickets. An explicit root changes the board.
- [ ] After a ticket moves, the next completion reflects its new status.
- [ ] Users can enable or disable completion in both supported installations.

Requirements: [Bash completion](../../../../docs/requirements/terminal.md#bash-completion).
