---
{
  "id": "T-5be95d1c",
  "kind": "task",
  "title": "Offer ticket cleanup before GitHub merges a pull request",
  "status": "backlog",
  "parent": "E-54e9139e",
  "depends_on": ["T-5dae58cb"],
  "implementer": "agent",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Offer ticket cleanup before GitHub merges a pull request

Offer an optional GitHub workflow that removes verified ticket files before merge.

## Scope

Supply an opt-in workflow and installation instructions for maintainers who want cleanup enforced before a GitHub merge. Demonstrate that the workflow verifies ticket paths and PR identity before writing, including on a fork where write credentials cannot safely be used.

## Acceptance criteria

- [ ] Installation shows the proposed changes and preserves existing protections.
- [ ] A second review is required when the cleanup changes the head and branch rules require reapproval.
- [ ] An out-of-scope path or unsafe fork is refused without privileged execution.

Requirements: [Optional pre-merge workflow](../../../../docs/requirements/github.md#optional-pre-merge-workflow).
