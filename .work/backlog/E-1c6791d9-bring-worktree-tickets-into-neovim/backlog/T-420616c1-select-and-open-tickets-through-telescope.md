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

## Purpose and scope

Provide a fast, optional Telescope front door to the local board: list, fuzzy
search, preview, and open a ticket without navigating its status directories.

## Acceptance criteria

- [ ] With Telescope configured, the plugin's list command opens a picker backed by the shared worktree-local model, not a separate scan or parsed terminal output.
- [ ] Rows show ID, title, kind, and status; fuzzy search matches IDs and titles, and status filters support workflows such as listing review tickets. Preview displays ticket Markdown and parent context.
- [ ] Selecting a row resolves its immutable ID to its current path and opens that Markdown buffer. A moved result opens the new path; a removed/invalid result reports the issue and refreshes without opening the wrong file.
- [ ] Cancellation changes no files or ticket state. Duplicate titles remain distinguishable by ID, and empty/no-match/error states are intentional.
- [ ] Expose a selection callback usable by no-ID action prompts; selecting an action target returns ID and board context to the action handler without running lifecycle logic inside the picker.
- [ ] Telescope is optional, loads only when needed, and is independent of Neo-tree. Without it, list/selection uses a documented core Neovim fallback; missing optional integration never breaks standalone commands.
- [ ] Tests cover filtering, preview, selected-ID lookup after moves, deletion, cancellation, separate worktrees, and missing Telescope. A real supported-version smoke test verifies selection opens the expected buffer.

## Approach and decisions

Follow T-5e7187d5's picker/command contract and use T-d8ea9e0a's model. Keep the
terminal CLI unchanged; this is the editor's presentation of list results.

## Verification

Demonstrate list filtered to review, search by title, preview, and open. Verify
that the resulting buffer provides the correct identity for a no-ID action.

## Handoff

Document registration/configuration, filters, supported versions, fallback, and
selection callback for action consumers. Record tests and integration evidence.
