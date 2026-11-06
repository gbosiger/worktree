---
{
  "id": "T-e769d578",
  "kind": "task",
  "title": "Publish archive records and prepare safe PR cleanup",
  "status": "backlog",
  "parent": "E-54e9139e",
  "depends_on": ["T-dc9a8fcd"],
  "implementer": "agent",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Publish archive records and prepare safe PR cleanup

## Purpose and scope

Prepare durable records and eligible ticket-removal commits on the selected PR
branch, with recoverable and idempotent GitHub archive comments.

## Acceptance criteria

- [ ] Each selected task/story has a complete, attributed managed archive comment and the shared Git record; already archived files resolve through local history without duplicate deletion/archival.
- [ ] Comments are idempotent per ticket/revision, preserve full content under the agreed size strategy, and never silently truncate or publish prohibited content.
- [ ] Remove files only after archive verification; cleanup includes only eligible scoped ticket paths in the PR head and preserves unrelated local/index changes.
- [ ] Epic cleanup archives the epic and collects all prior child records for the final squash message, including tasks merged earlier and no longer present as files.
- [ ] Preview shows comments, records, removals, cleanup commits, and messages without writes. Authentication/network/comment-size/cleanup failures preserve content and distinguish completed from pending actions.
- [ ] Tests cover comment-success/cleanup-failure retries, altered or missing records, oversized content, archived children, and cleanup-head changes requiring fresh checks/reviews.

## Approach and decisions

Reuse the E-0182afb4 codec/history lookup and safety contract. This task prepares
cleanup; it does not merge or claim GitHub comments replace local Git durability.

## Verification

Use disposable branches and a fake GitHub adapter with injected partial failures.
Verify complete record recovery and unchanged unrelated work.

## Handoff

Provide cleanup/retry evidence and recovery instructions to the human reviewer.
