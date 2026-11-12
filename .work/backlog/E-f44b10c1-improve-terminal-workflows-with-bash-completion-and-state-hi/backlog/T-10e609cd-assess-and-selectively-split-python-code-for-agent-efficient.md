---
{
  "id": "T-10e609cd",
  "kind": "task",
  "title": "Decide whether to split the Python module",
  "status": "backlog",
  "parent": "E-f44b10c1",
  "depends_on": [],
  "implementer": null,
  "reviewer": null,
  "branch": null,
  "base_branch": null
}
---
# Decide whether to split the Python module

Decide whether moving part of the Python module would make completion and history work easier to maintain.

## Scope

Compare the reading path for completion lookup, state writes, and archive preservation in the existing module and a plausible split. Use approximate lines or bytes and file crossings. Extract code only if the comparison justifies it. Hand the decision and any changed code locations to terminal workflow verification.

## Acceptance criteria

- [ ] The comparison shows how much code a contributor must read and which files they must cross.
- [ ] The decision explains why to keep or split the module. If code moves, installed and checkout entry points still work.

Requirements: [Python module layout](../../../../docs/requirements/terminal.md#python-module-layout).

## Handoff

Assess the layout alongside the completion and history changes. Pass the decision to T-6bab2842.
