---
{
  "id": "E-54e9139e",
  "kind": "epic",
  "title": "Review and merge tickets through GitHub pull requests",
  "status": "backlog",
  "parent": null,
  "depends_on": [
    "E-1a88a55f"
  ],
  "implementer": "agent",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Review and merge tickets through GitHub pull requests

Today the toolkit can retain accepted tickets locally. Maintainers also want pull requests for discussing a change, with enough history left on the default branch to reopen a child after its feature branch is gone.

## Scope and delivery

First settle how an approved ticket survives GitHub merges. Then open or update a draft and demonstrate one accepted child landing while its siblings remain open. Epic readiness, assigned reviews, and final cleanup build on those decisions. Installing the remote workflow is optional. Local-only users must still be able to work offline.

The design decision in T-8818c75d matters to every cleanup task. Earlier plans put full records in squash messages, while the current reader recovers committed files. The reviewer needs a fresh-clone demonstration before choosing the archive policy.

## Acceptance criteria

- [ ] A maintainer can preview and update the intended PR without overwriting discussion.
- [ ] A finished task can land while siblings remain open. The epic waits for completion and required reviews.
- [ ] A fresh clone can show and reopen every accepted ticket after final integration.

Requirements: [Publication decisions](../../../docs/requirements/github.md#publication-decisions).

## Handoff

Next decision belongs to the human reviewer of T-8818c75d. Ask the implementer to show where the earlier child’s file is recoverable after both merges.
