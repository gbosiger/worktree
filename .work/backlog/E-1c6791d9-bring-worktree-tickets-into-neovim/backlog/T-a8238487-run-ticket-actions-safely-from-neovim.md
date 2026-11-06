---
{
  "id": "T-a8238487",
  "kind": "task",
  "title": "Run ticket actions safely from Neovim",
  "status": "backlog",
  "parent": "E-1c6791d9",
  "depends_on": ["T-d8ea9e0a"],
  "implementer": null,
  "reviewer": null,
  "branch": null,
  "base_branch": null
}
---
# Run ticket actions safely from Neovim

## Purpose and scope

Expose explicit ticket commands and reusable handlers for tree bindings without
reimplementing or bypassing toolkit lifecycle rules.

## Acceptance criteria

- [ ] Provide create, start, review, done, and reopen actions plus open/preview/copy-ID commands usable without Neo-tree; create validates the selected parent kind.
- [ ] Commands without an explicit ID infer the target from the current ticket buffer's validated metadata and board membership. For example, done from an open review ticket uses that ticket's ID without asking the user to retype it, while preserving every completion gate.
- [ ] Explicit IDs override buffer inference; actions invoked on a tree/picker entry use that entry, not the previously active ticket buffer. An ordinary source buffer or invalid/missing ticket identity requests selection or reports an actionable error, never silently uses the last ticket.
- [ ] Resolve board and target together, including an explicit ID from another buffer context; reject ambiguous or invalid targets rather than acting in a different worktree. Tests cover ticket README buffers, moved files, malformed/edited identity, and explicit overrides.
- [ ] Invoke the correct project CLI asynchronously with argument arrays, not shell interpolation; titles, evidence, spaces in paths, and shell metacharacters remain literal.
- [ ] Prompt for required input, reviewer identity, and completion evidence; preserve CLI acceptance/dependency gates and surface actionable stderr and exit failures.
- [ ] Resolve target IDs at execution time and explicitly save or cancel around affected unsaved buffers; never overwrite unsaved edits, auto-check acceptance items, or change another worktree.
- [ ] Cancellation performs no mutation; successful moves reconcile open buffers and refresh consumers, while failures retain recoverable state and visible diagnostics.
- [ ] Tests cover missing CLI, rejected transitions, unsaved edits, cancelled prompts, moved targets, malicious-looking arguments, and separate worktrees. No Git/publish actions are implicit.

## Approach and decisions

Follow docs/LIFECYCLE.md and the design's CLI-resolution policy. Expose handlers
that the optional tree can bind without coupling standalone actions to Neo-tree.

## Verification

Use a fake process runner for argument/failure tests and temporary real boards
for lifecycle integration, including completion denied by unchecked criteria.

## Handoff

Document commands, target precedence, prompts, buffer policy, and verified failure
behavior. Include the open-review-ticket → done-without-ID workflow.
