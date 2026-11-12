---
{
  "id": "T-266c67e6",
  "kind": "task",
  "title": "Explain what blocks an epic pull request",
  "status": "backlog",
  "parent": "E-54e9139e",
  "depends_on": ["T-dc9a8fcd"],
  "implementer": "agent",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Explain what blocks an epic pull request

Tell a maintainer whether the selected epic PR can leave draft and what still blocks it.

## Scope

Use the PR’s current revision and the selected epic’s board state. For a draft whose last backlog item moved to review, report the unfinished review. Once ready, adding a new child or changing the PR revision requires another check before merge.

## Acceptance criteria

- [ ] Unfinished children block the epic. Unrelated backlog does not.
- [ ] Reopening work or changing the PR head invalidates the earlier readiness result.
- [ ] Repeating the check is safe and never merges the PR.

Requirements: [Readiness and merge checks](../../../../docs/requirements/github.md#readiness-and-merge-checks).
