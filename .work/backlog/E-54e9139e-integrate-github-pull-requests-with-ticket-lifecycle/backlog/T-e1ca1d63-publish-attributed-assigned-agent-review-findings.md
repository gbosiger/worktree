---
{
  "id": "T-e1ca1d63",
  "kind": "task",
  "title": "Publish attributed assigned-agent review findings",
  "status": "backlog",
  "parent": "E-54e9139e",
  "depends_on": ["T-dc9a8fcd"],
  "implementer": "agent",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Publish attributed assigned-agent review findings

## Purpose and scope

Support real assigned-agent PR review with revision-specific findings and actual
verification evidence, without pretending to be an independent human reviewer.

## Acceptance criteria

- [ ] Only an agreed assigned-agent reviewer follows the agent-review path after PR creation; a human assignment is not silently replaced or auto-accepted.
- [ ] Review guidance requires inspecting the current head and reporting actual findings, evidence, and limitations; generated output is not a canned approval or a claim that unrun tests passed.
- [ ] Published findings visibly include AGENT, ticket IDs, and reviewed revision, using the user's authenticated identity without credential exposure or authorship changes.
- [ ] When the same identity authored the PR, publish advisory comments if formal self-review is unavailable; explain independent-approval requirements and never count advisory output as satisfying them.
- [ ] Publishing is explicit/previewable and idempotent per ticket/revision; stale-head, permission, and network failures do not imply approval or alter local acceptance.
- [ ] Tests cover role selection, self-review fallback, attribution, duplicate retries, changed heads, and unavailable formal review without real publication.

## Approach and decisions

Coordinate canonical skill guidance with structured CLI publication. The command
records supplied review evidence; it cannot prove a review occurred or invent it.

## Verification

Exercise mocked identities, role assignments, head revisions, and review endpoints;
manually inspect the guidance for misleading approval claims.

## Handoff

Provide labelled examples and role/permission evidence to the human reviewer.
