---
{
  "id": "T-7147e599",
  "kind": "task",
  "title": "Resolve archived records from reachable Git history",
  "status": "backlog",
  "parent": "E-0182afb4",
  "depends_on": ["T-4e1573f6"],
  "implementer": "agent",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Resolve archived records from reachable Git history

## Purpose and scope

Provide reusable local archive encoding and lookup so later removals do not
make ticket definitions inaccessible. This task does not remove tickets.

## Acceptance criteria

- [ ] Encode/decode the approved record format with lossless metadata/prose round trips and actionable malformed/unsupported-record errors.
- [ ] Resolve IDs using only history reachable from the current branch, including records carried forward in squash commits, without GitHub access.
- [ ] Apply the agreed precedence for repeated records and active reopened tickets; detect conflicting records rather than arbitrarily accepting one.
- [ ] Missing or incomplete history never implies a prerequisite is accepted; report recovery guidance for shallow clones and unavailable records.
- [ ] Tests cover multiple records, unknown metadata, Unicode/delimiter-like prose, corruption, unreachable commits, shallow history, and rearchiving.

## Approach and decisions

Use the T-4e1573f6 contract. Keep archive reads separate from mutable board paths
so downstream lifecycle and PR operations share one implementation.

## Verification

Use disposable Git repositories with controlled branch histories; run the unit suite.

## Handoff

Provide codec/lookup usage and test evidence to the human reviewer.
