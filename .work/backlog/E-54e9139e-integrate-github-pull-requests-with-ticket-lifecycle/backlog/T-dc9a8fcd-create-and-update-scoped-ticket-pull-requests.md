---
{
  "id": "T-dc9a8fcd",
  "kind": "task",
  "title": "Open or update a pull request for selected tickets",
  "status": "backlog",
  "parent": "E-54e9139e",
  "depends_on": ["T-8818c75d"],
  "implementer": "agent",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Open or update a pull request for selected tickets

Open or update one pull request for the selected work.

## Scope

Use the agreed publication policy to select the repository, branch, and tickets. An epic with two unfinished children may have a draft PR. Updating that draft after someone edits its description must refresh the managed section while retaining their own paragraphs.

## Acceptance criteria

- [ ] Preview identifies the selected tickets and destination before any write.
- [ ] Retrying updates the same PR and preserves the author’s own text.
- [ ] A maintainer can open a draft epic or a batch of accepted children while other children are unfinished.

Requirements: [Opening pull requests](../../../../docs/requirements/github.md#opening-pull-requests).
