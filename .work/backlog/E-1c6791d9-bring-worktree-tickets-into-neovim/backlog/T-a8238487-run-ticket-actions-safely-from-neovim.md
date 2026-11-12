---
{
  "id": "T-a8238487",
  "kind": "task",
  "title": "Run ticket actions safely from Neovim",
  "status": "backlog",
  "parent": "E-1c6791d9",
  "depends_on": ["T-d8ea9e0a"],
  "implementer": null,
  "reviewer": null,
  "branch": null,
  "base_branch": null
}
---
# Run ticket actions safely from Neovim

Let developers run ticket actions from the current buffer, tree, or picker.

## Scope

Use the existing CLI for create, start, review, done, and reopen. The key decision is which board and ticket will receive the action. Test an open ticket with unsaved edits, a different ticket selected in the picker, and cancellation before a write.

## Acceptance criteria

- [ ] Done from an open review ticket asks for reviewer and evidence and uses that ticket.
- [ ] An explicit ID or selected entry targets the intended ticket in its own board.
- [ ] Cancelling preserves unsaved edits. A rejected command explains what to fix.

Requirements: [Ticket actions](../../../../docs/requirements/neovim.md#ticket-actions).
