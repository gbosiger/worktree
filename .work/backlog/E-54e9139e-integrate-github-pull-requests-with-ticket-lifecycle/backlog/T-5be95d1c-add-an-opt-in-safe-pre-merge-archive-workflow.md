---
{
  "id": "T-5be95d1c",
  "kind": "task",
  "title": "Add an opt-in safe pre-merge archive workflow",
  "status": "backlog",
  "parent": "E-54e9139e",
  "depends_on": ["T-5dae58cb"],
  "implementer": "agent",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Add an opt-in safe pre-merge archive workflow

## Purpose and scope

Provide an explicitly installed workflow/action for scoped archive validation
and pre-merge cleanup using the same contracts as the CLI.

## Acceptance criteria

- [ ] Installation is opt-in, previews changes, and preserves existing workflows/protection rules; neither local adoption nor PR creation installs it implicitly.
- [ ] Workflow validates selected ticket IDs, repository/head, and scoped paths before any cleanup; arbitrary paths and unrelated ticket removals are rejected.
- [ ] Untrusted PR code is never executed with write credentials; document trust boundaries, minimum permissions, fork handling, and safe refusal paths.
- [ ] Cleanup is committed before merge and changes the checked head, triggering required checks/reapproval. A post-merge action is not represented as pre-merge removal.
- [ ] Document required branch-protection/check configuration and limitations for UI merges, edited squash messages, queues, or other unsupported policies; do not claim enforcement where none is installed.
- [ ] Tests/fixtures exercise malicious paths, untrusted fork inputs, insufficient permissions, duplicate runs, and stale heads without real GitHub writes.

## Approach and decisions

Reuse CLI archive/gate primitives rather than a second archive implementation.
Do not weaken repository protection or use privileged execution of PR scripts.

## Verification

Review workflow event/permission boundaries and exercise the trusted validator
against adversarial fixtures; run the unit suite.

## Handoff

Provide the threat-boundary review and explicit installation instructions for human review.
