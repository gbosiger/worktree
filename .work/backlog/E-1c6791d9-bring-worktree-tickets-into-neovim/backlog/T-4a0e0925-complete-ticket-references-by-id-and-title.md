---
{
  "id": "T-4a0e0925",
  "kind": "task",
  "title": "Complete ticket references by ID and title",
  "status": "backlog",
  "parent": "E-1c6791d9",
  "depends_on": ["T-d8ea9e0a"],
  "implementer": null,
  "reviewer": null,
  "branch": null,
  "base_branch": null
}
---
# Complete ticket references by ID and title

Let a writer insert a ticket reference by typing part of its title or ID.

## Scope

Use the shared live-ticket model in the chosen completion adapter. In a buffer containing two tickets with the same title, the writer must be able to distinguish them by ID and preview. Check that accepting a suggestion in the middle of a sentence preserves the words on both sides.

## Acceptance criteria

- [ ] Suggestions show enough context to distinguish identical titles.
- [ ] Choosing a result inserts only its ID and preserves surrounding prose.
- [ ] A parent prompt offers valid parent kinds.

Requirements: [Reference completion](../../../../docs/requirements/neovim.md#reference-completion).
