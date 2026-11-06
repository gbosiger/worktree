---
{
  "id": "T-dc9a8fcd",
  "kind": "task",
  "title": "Create and update scoped ticket pull requests",
  "status": "backlog",
  "parent": "E-54e9139e",
  "depends_on": ["T-8818c75d"],
  "implementer": "agent",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Create and update scoped ticket pull requests

## Purpose and scope

Implement optional GitHub access and explicit, retry-safe PR creation/update
for selected epics or accepted done task/story batches.

## Acceptance criteria

- [ ] Task/story PRs target the recorded epic feature branch; epic PRs discover the selected repository's actual default branch. Ambiguous targets and unexpected defaults require clarification per the approved contract.
- [ ] Task selection is explicit, accepted, done, and scoped to one epic; unfinished/unrelated items are untouched and other unfinished children do not block a task PR.
- [ ] Create/update the matching PR idempotently, support draft epic PRs, and reconcile closed/reopened/merged or conflicting candidates without accidental duplicate PRs or merges.
- [ ] Managed descriptions include IDs, scope, criteria, evidence, source revision, and AGENT attribution while preserving user-authored content outside managed sections.
- [ ] Preview identifies local/remote targets, selected IDs, and proposed writes without mutation. Missing authentication/permissions or network errors preserve local/index state and explain completed versus pending actions.
- [ ] GitHub is not required for local commands; adapter tests cover targeting, retries, managed text, failures, and no-publication previews using fakes.

## Approach and decisions

Follow T-8818c75d for transport and authorization. No merge, archival cleanup,
workflow installation, or invented review is part of opening a PR.

## Verification

Use fake remote responses and isolated local repositories; never require a real
push or PR in automated tests. Run the full unit suite.

## Handoff

Provide supported target/state combinations and failure evidence for human review.
