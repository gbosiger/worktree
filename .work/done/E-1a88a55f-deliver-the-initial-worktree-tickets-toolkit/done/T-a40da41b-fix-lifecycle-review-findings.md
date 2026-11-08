---
{
  "id": "T-a40da41b",
  "kind": "task",
  "title": "Fix lifecycle review findings",
  "status": "done",
  "parent": "E-1a88a55f",
  "depends_on": [],
  "implementer": "agent",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Fix lifecycle review findings

## Purpose and scope

Fix the three lifecycle defects found during the pre-release agent review.
Keep Git operations and human acceptance explicit; do not expand installation scope.

## Acceptance criteria

- [x] Reopening rejects completed dependents of affected ancestors before any writes, including dry runs.
- [x] Validation rejects cycles involving explicit dependencies and container completion prerequisites.
- [x] Completion rejects unchecked Markdown bullet and numbered checklist items.
- [x] Regression tests and the dogfood board pass; stricter draft behavior is documented.

## Approach and decisions

Preflight the complete set of tickets leaving done before reopening. Traverse
child prerequisites alongside explicit dependencies during cycle validation.
Recognize ordinary bullet/numbered checklist markers without adding a parser
dependency. Test rejection without mutations and successful neighboring cases.

## Verification

- `python3 -m unittest discover -s tests -v`: all 13 tests pass.
- `python3 work.py --root . check`: all 5 tickets validate.
- Added four regression tests covering ancestor dependents, direct and indirect
  completion cycles, allowed parent-to-child dependencies, and Markdown markers.
- CONVENTION.md documents the stricter draft compatibility rules.

## Handoff

Ready for human review of work.py, tests/test_work.py, and CONVENTION.md.
No human acceptance, Git commit, or publication is claimed.

## Acceptance record

2026-11-06T19:19:31+00:00 — human: The maintainer clarified in this conversation that moving these existing tickets to done was their approval, and requested staging, committing, and archival. This records that current confirmation for this already-done ticket; earlier handoff prose is retained as historical evidence, not backdated or replaced. No additional human test run is claimed.
