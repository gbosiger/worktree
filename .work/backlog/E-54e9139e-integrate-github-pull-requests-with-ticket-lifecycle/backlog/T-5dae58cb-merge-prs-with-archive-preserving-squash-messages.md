---
{
  "id": "T-5dae58cb",
  "kind": "task",
  "title": "Keep tickets recoverable after a squash merge",
  "status": "backlog",
  "parent": "E-54e9139e",
  "depends_on": ["T-266c67e6", "T-e769d578"],
  "implementer": "agent",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Keep tickets recoverable after a squash merge

Merge approved PRs so a maintainer can recover their tickets offline after both squash merges.

## Scope

Use readiness and cleanup evidence for the same PR revision. Demonstrate a child landing on its epic and that epic landing on the default branch. Inspect the resulting history in a fresh clone, then reopen the earlier child offline. Include the recovery path if a merge request times out.

## Acceptance criteria

- [ ] The preview shows the exact proposed message and records, including children merged earlier.
- [ ] A changed head, missing record, or outstanding required review blocks the merge.
- [ ] A fresh clone can resolve dependencies and reopen a merged child.

Requirements: [Merging](../../../../docs/requirements/github.md#merging).
