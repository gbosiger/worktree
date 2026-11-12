---
{
  "id": "S-8ce9abfb",
  "kind": "story",
  "title": "Let a reviewer confirm acceptance from WIP",
  "status": "backlog",
  "parent": "E-f44b10c1",
  "depends_on": [],
  "implementer": null,
  "reviewer": null,
  "branch": null,
  "base_branch": null
}
---
# Let a reviewer confirm acceptance from WIP

An assigned reviewer may have finished a review task while the ticket itself is still in WIP. They need to see exactly which handoff they are skipping before accepting it.

## Behavior

When the reviewer opts in, show the target and ask for confirmation. On confirmation, recheck eligibility, record evidence, and move the ticket to implemented. If the ticket changed while waiting for input, its earlier eligibility cannot authorize the move. The opt-in waives only the review-state requirement.

## Acceptance criteria

- [ ] Ordinary acceptance refuses WIP. Opting in names the ticket and asks for confirmation.
- [ ] Declining or cancelling leaves the ticket unchanged.
- [ ] Missing evidence or a mismatched reviewer still blocks acceptance after confirmation.
- [ ] A successful confirmation records the move from WIP directly to implemented.

Requirements: [Direct acceptance from WIP](../../../../docs/requirements/terminal.md#direct-acceptance-from-wip).

## Handoff

Decide eligible ticket kinds and noninteractive confirmation before implementing the shortcut.
