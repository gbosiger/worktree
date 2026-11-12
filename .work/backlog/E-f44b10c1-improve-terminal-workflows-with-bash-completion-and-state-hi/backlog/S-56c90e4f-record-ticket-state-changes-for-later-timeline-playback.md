---
{
  "id": "S-56c90e4f",
  "kind": "story",
  "title": "Record ticket state changes for later timeline playback",
  "status": "backlog",
  "parent": "E-f44b10c1",
  "depends_on": ["T-f7d4aef3"],
  "implementer": null,
  "reviewer": null,
  "branch": null,
  "base_branch": null
}
---
# Record ticket state changes for later timeline playback

A reviewer reopening an old ticket needs to see when it changed state and which transitions actually happened, including an earlier return for changes.

## Behavior

For a story that goes from WIP to review and back, retain both moves in order. Moving the enclosing epic can change the story’s path without changing its state. That path change adds no event to the story. Use the event format agreed in T-f7d4aef3, including its rules for older tickets.

## Acceptance criteria

- [ ] A successful transition records the old state, new state, and time.
- [ ] Preview, refusal, and rollback leave no invented transition.
- [ ] Earlier history and acceptance evidence survive archive and reopen.

Requirements: [Recording transitions](../../../../docs/requirements/terminal.md#recording-transitions).
