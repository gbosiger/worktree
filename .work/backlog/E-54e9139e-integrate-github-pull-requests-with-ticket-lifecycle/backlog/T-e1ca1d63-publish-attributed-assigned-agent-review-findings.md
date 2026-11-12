---
{
  "id": "T-e1ca1d63",
  "kind": "task",
  "title": "Publish the assigned agent’s review on the pull request",
  "status": "backlog",
  "parent": "E-54e9139e",
  "depends_on": ["T-dc9a8fcd"],
  "implementer": "agent",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Publish the assigned agent’s review on the pull request

Show a maintainer what the assigned agent found when reviewing a specific PR revision.

## Scope

Use the assigned reviewer and exact revision to prepare a review with findings and actual checks. Show the human reviewer sample output for two cases: the account can formally review, or it authored the PR and can only leave advisory feedback.

## Acceptance criteria

- [ ] Published findings name the agent role, tickets, revision, and checks actually run.
- [ ] Self-review through the author’s account appears as advisory when independent approval is required.
- [ ] Retrying cannot duplicate findings or silently replace a human reviewer.

Requirements: [Agent review](../../../../docs/requirements/github.md#agent-review).
