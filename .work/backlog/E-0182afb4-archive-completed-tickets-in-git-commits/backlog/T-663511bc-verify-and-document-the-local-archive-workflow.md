---
{
  "id": "T-663511bc",
  "kind": "task",
  "title": "Verify and document the local archive workflow",
  "status": "backlog",
  "parent": "E-0182afb4",
  "depends_on": ["T-2c08fd6d"],
  "implementer": "agent",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Verify and document the local archive workflow

## Purpose and scope

Validate the complete accept/commit/lookup/reopen workflow and update user-facing
guidance. This is cross-feature verification, not a replacement for per-task tests.

## Acceptance criteria

- [ ] An end-to-end disposable-project test accepts multiple children, archives them, completes/archives their container, resolves dependencies, and reopens content with historical evidence intact.
- [ ] Exercise explicit/fallback branches, unrelated staged/unstaged work, failure recovery, missing history, and a squash carrying approved records; record results and limitations against the epic criteria.
- [ ] README, focused format/Git/lifecycle docs, CLI help, and canonical skills explain done queues, explicit archival, staged-snapshot semantics, history preservation, and recovery without claiming remote publication.
- [ ] Installed toolkit behavior is checked from an unrelated working directory; instructions remain self-contained and do not require a global service or third-party Python package.
- [ ] Full unit suite and dogfood check pass; provide evidence for human review without auto-checking acceptance or claiming reviewer approval.

## Approach and decisions

Keep durable guidance in docs/ and canonical skill sources in skills/. Replace
planned-feature disclaimers only for functionality actually implemented.

## Verification

Run python3 -m unittest discover -s tests -v and ./work --root . check,
plus the documented isolated end-to-end exercise.

## Handoff

Present epic acceptance coverage and any remaining gaps to the human reviewer.
