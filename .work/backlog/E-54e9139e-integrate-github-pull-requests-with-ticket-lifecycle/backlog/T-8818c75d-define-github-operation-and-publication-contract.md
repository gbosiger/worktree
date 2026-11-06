---
{
  "id": "T-8818c75d",
  "kind": "task",
  "title": "Define GitHub operation and publication contract",
  "status": "backlog",
  "parent": "E-54e9139e",
  "depends_on": ["E-0182afb4"],
  "implementer": "agent",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Define GitHub operation and publication contract

## Purpose and scope

Settle the remote operation boundaries using the accepted local archive format.
Keep GitHub optional; this preparation does not authorize any publication.

## Acceptance criteria

- [ ] Specify CLI/shortcut names, authentication mechanism/minimum permissions, and exactly which explicit operations may push, comment, review, clean up, or merge.
- [ ] Define repository/remote/default-branch discovery, task-to-epic targeting, grouped-epic behavior, and confirmation of ambiguous or unexpected targets; do not silently override existing branch policy.
- [ ] Define managed section/comment markers, source revision attribution, AGENT labels, comment location, idempotency keys, and full-record size handling without truncation.
- [ ] Resolve supported squash/merge-queue/auto-merge policies, required checks, cleanup/reapproval sequencing, and how archive-preserving messages are enforced or unsupported operations blocked.
- [ ] Define public-content/secret review and a recoverable prohibited-content failure path before publication, without promising automatic secret detection.
- [ ] Record approved decisions and remaining blockers in focused docs, reusing E-0182afb4 records rather than inventing a second format.

## Approach and decisions

The epic's human reviewer remains authoritative. Optional assigned-agent PR
review is a separate capability, not permission to replace that human review.

## Verification

Walk through the epic scenario table and map each remote side effect to an
authorization, preview, retry, and failure boundary.

## Handoff

Submit the bounded contract and unresolved decisions for human review before implementation.
