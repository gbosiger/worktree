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

## Purpose and scope

Add an optional ticket-board source switchable alongside Neo-tree filesystem and
Git sources, using the agreed cockpit layout.

## Acceptance criteria

- [ ] Render status lanes, optional groups, epics, and child status lanes with stories/tasks; define empty-board and empty-lane presentation.
- [ ] Provide keyboard navigation, title/ID search or filtering, preview, open Markdown, and copy ID; labels remain intelligible without icons or color.
- [ ] Refresh preserves expansion/selection by ID where possible, follows moved nodes, and handles removal of the selected ticket without errors.
- [ ] Source setup coexists with existing Neo-tree sources/mappings; missing Neo-tree does not prevent completion or standalone commands from loading.
- [ ] Tests and a real Neo-tree smoke test cover nested groups, mixed child statuses, duplicate titles, external moves, filtering, and narrow windows.

## Approach and decisions

Use Neo-tree's supported source API and the shared board model. Keep lifecycle
logic out of the renderer; action bindings can be added by T-a8238487.

## Verification

Compare the working source with the approved sketch and record the tested
Neo-tree version and navigation/refresh evidence.

## Handoff

Document source registration, mapping configuration, and action extension points.
