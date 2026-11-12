---
{
  "id": "T-f7d4aef3",
  "kind": "task",
  "title": "Define a timestamped ticket state history format",
  "status": "backlog",
  "parent": "E-f44b10c1",
  "depends_on": [],
  "implementer": null,
  "reviewer": null,
  "branch": null,
  "base_branch": null
}
---
# Define a timestamped ticket state history format

Define a history entry a person can read and a future timeline can order.

## Scope

Record the agreed format in the maintained format and lifecycle docs so S-56c90e4f can implement it. Walk one story from creation through review, commit, archive, and reopen. Show how a reader distinguishes a missing old event from an observed transition and how events stay ordered when the clock repeats.

## Acceptance criteria

- [ ] Examples show ordinary transitions, a return from review, and reopening an archived ticket.
- [ ] The format explains tied timestamps, manual edits, old tickets, and partial writes.
- [ ] The format names the ticket kinds that record history and specifies the first entry, if any, for a newly created ticket.

Requirements: [History format](../../../../docs/requirements/terminal.md#history-format).
