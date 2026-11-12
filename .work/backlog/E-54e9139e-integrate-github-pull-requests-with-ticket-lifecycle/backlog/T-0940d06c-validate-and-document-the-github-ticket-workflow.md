---
{
  "id": "T-0940d06c",
  "kind": "task",
  "title": "Validate and document the GitHub ticket workflow",
  "status": "backlog",
  "parent": "E-54e9139e",
  "depends_on": ["T-5dae58cb", "T-e1ca1d63", "T-5be95d1c"],
  "implementer": "agent",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Validate and document the GitHub ticket workflow

Give maintainers a repeatable walkthrough of publishing, reviewing, merging, and recovering a ticket.

## Scope

Use the finished CLI and installed OpenCode shortcuts in a disposable repository. Record an end-to-end task and epic merge, a rejected operation after the head changes, and recovery of an earlier child. Identify any remote protection that the local simulation cannot verify.

## Acceptance criteria

- [ ] Tests demonstrate both merge levels and recovery from a fresh offline clone.
- [ ] A reviewer can see which protections were exercised and which scenarios remain untested.
- [ ] The installed shortcuts and CLI help match the documented workflow.

Requirements: [Verification](../../../../docs/requirements/github.md#verification).
