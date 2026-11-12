---
{
  "id": "T-420616c1",
  "kind": "task",
  "title": "Select and open tickets through Telescope",
  "status": "backlog",
  "parent": "E-1c6791d9",
  "depends_on": ["T-d8ea9e0a"],
  "implementer": null,
  "reviewer": null,
  "branch": null,
  "base_branch": null
}
---
# Select and open tickets through Telescope

Help a user open the right Markdown file from a searchable list or choose a ticket for an action.

## Scope

Use the shared model for the editor’s list command. A reviewer filtering to review should see matching titles and a preview, and be able to open a result by its immutable ID. The picker also supplies a target to action prompts. Leave executing the action to the CLI handler.

## Acceptance criteria

- [ ] Filtering to review and searching a title shows matching previews.
- [ ] Selecting a moved result opens its current file. Cancelling leaves the editor alone.
- [ ] Selection also works through the documented fallback without Telescope.

Requirements: [Picker](../../../../docs/requirements/neovim.md#picker).
