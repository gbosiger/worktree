---
{
  "id": "T-8818c75d",
  "kind": "task",
  "title": "Agree on how GitHub publishes and preserves tickets",
  "status": "backlog",
  "parent": "E-54e9139e",
  "depends_on": ["E-1a88a55f"],
  "implementer": "agent",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Agree on how GitHub publishes and preserves tickets

Agree with the maintainer on how to publish tickets and keep their records recoverable after both GitHub merges.

## Scope

Compare the current Git archive reader with the proposed two-level squash workflow. Deliver a decision note describing where records survive, which operations publish data, and which policies must be refused. Use one child merged early as the worked example for the human reviewer.

## Acceptance criteria

- [ ] The agreed policy states which command writes what, under whose identity, and with which permissions.
- [ ] The decision note records the merge policy chosen by the human reviewer. A fresh-clone example shows where to recover an earlier child after both merges.
- [ ] The note specifies the PR destination for a grouped epic or explains when to refuse publication.
- [ ] The note specifies which content must be withheld from publication.
- [ ] The note specifies how to preserve an oversized ticket in full or stop before deleting it.

If the reviewer defers a choice, record it alongside the affected child IDs and the work that must wait. Leave the corresponding criterion open until the policy is settled.

Requirements: [Publication decisions](../../../../docs/requirements/github.md#publication-decisions).
