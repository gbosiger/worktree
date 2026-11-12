---
{
  "id": "E-1c6791d9",
  "kind": "epic",
  "title": "Bring Worktree Tickets into Neovim",
  "status": "backlog",
  "parent": null,
  "depends_on": [],
  "implementer": null,
  "reviewer": null,
  "branch": null,
  "base_branch": null
}
---
# Bring Worktree Tickets into Neovim

Today a developer who knows a ticket by title still has to find its Markdown path, and that path changes when the ticket moves. They should be able to find, edit, and advance that ticket without leaving Neovim.

## Scope and delivery

Start with a shared view of the live board in the current worktree. Use it to find and open a ticket, insert its ID in prose, or browse the board in Neo-tree. Then let a reviewer act on the open ticket through the project CLI. The picker and tree are optional. Archive browsing and Git publication fall outside this epic.

For the final demo, find a review ticket by title, open it after a status move, and attempt a lifecycle action. Show both the accepted action and the explanation for a rejected one.

## Acceptance criteria

- [ ] Searching by title opens the right ticket even after it moves.
- [ ] Choosing a title in completion inserts its ticket ID into the user’s text.
- [ ] A reviewer can open that ticket and request a lifecycle action from its buffer.
- [ ] The documented workflow works with optional integrations disabled.

Requirements: [Editor design](../../../docs/requirements/neovim.md#editor-design).

## Handoff

Confirm the execution branch, base, and roles, then start the Neovim workspace design in T-5e7187d5.
