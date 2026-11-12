---
{
  "id": "T-e769d578",
  "kind": "task",
  "title": "Archive tickets before removing their files",
  "status": "backlog",
  "parent": "E-54e9139e",
  "depends_on": ["T-dc9a8fcd"],
  "implementer": "agent",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Archive tickets before removing their files

Preserve every selected ticket before removing its file from a PR.

## Scope

Start from the archive policy chosen in T-8818c75d. Prepare the scoped deletion on the PR branch only after the full record can be recovered. Demonstrate a retry after a comment was published but local cleanup failed, including what the maintainer sees on the second attempt.

## Acceptance criteria

- [ ] The preview shows exactly which records will be published and which files will be removed.
- [ ] A failed or oversized archive leaves the ticket recoverable.
- [ ] Retrying after a comment succeeds resumes cleanup without duplicating the comment.

Requirements: [Archive and cleanup](../../../../docs/requirements/github.md#archive-and-cleanup).
