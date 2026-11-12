---
{
  "id": "T-5e7187d5",
  "kind": "task",
  "title": "Design the ticket workflow in Neovim",
  "status": "backlog",
  "parent": "E-1c6791d9",
  "depends_on": [],
  "implementer": null,
  "reviewer": null,
  "branch": null,
  "base_branch": null
}
---
# Design the ticket workflow in Neovim

Give plugin implementers a design they can build against. Sketch how a developer finds a ticket and acts on it.

## Scope

Use the existing Markdown format and CLI lifecycle as inputs. Produce a maintained design note with a sketch of a reviewer finding a ticket and acting on it. Resolve the minimum editor version, first completion adapter, and how the plugin identifies its board before dependent tasks start.

## Acceptance criteria

- [ ] A reviewer can follow the picker, completion, and tree examples, including an empty board.
- [ ] The design names supported versions, adapters, target selection rules, and a way to measure responsiveness.

Requirements: [Editor design](../../../../docs/requirements/neovim.md#editor-design).
