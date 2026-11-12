---
{
  "id": "T-d8ea9e0a",
  "kind": "task",
  "title": "Build worktree-aware ticket discovery and refresh",
  "status": "backlog",
  "parent": "E-1c6791d9",
  "depends_on": ["T-5e7187d5"],
  "implementer": null,
  "reviewer": null,
  "branch": null,
  "base_branch": null
}
---
# Build worktree-aware ticket discovery and refresh

Give every editor view the same up-to-date list of tickets for its worktree.

## Scope

Use the editor design to build the lookup and refresh interface used by the picker, tree, and completion. Resolve a board from the active buffer. Verify with two linked worktrees and a ticket moved externally while an old search is still open.

## Acceptance criteria

- [ ] Two buffers in different worktrees show their own tickets.
- [ ] Edits and moves refresh the correct view without interrupting typing.
- [ ] An invalid ticket produces a diagnostic while other results stay available.

Requirements: [Board discovery](../../../../docs/requirements/neovim.md#board-discovery).
