---
{
  "id": "T-683615e7",
  "kind": "task",
  "title": "Browse the ticket board as a Neo-tree source",
  "status": "backlog",
  "parent": "E-1c6791d9",
  "depends_on": ["T-d8ea9e0a"],
  "implementer": null,
  "reviewer": null,
  "branch": null,
  "base_branch": null
}
---
# Browse the ticket board as a Neo-tree source

Let users browse the board by status inside Neo-tree.

## Scope

Build the optional tree source on the shared board model. Exercise it with a group containing epics whose children have different statuses. A reviewer should be able to expand the group, find a child by title, and follow the same selection after its path changes.

## Acceptance criteria

- [ ] A keyboard user can find a child ticket, preview it, open it, and copy its ID.
- [ ] The tree follows a moved ticket and stays usable when it is removed.
- [ ] Status and kind remain readable without color or icons.

Requirements: [Tree navigation](../../../../docs/requirements/neovim.md#tree-navigation).
