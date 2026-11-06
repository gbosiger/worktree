---
{
  "id": "T-8c250b3f",
  "kind": "task",
  "title": "Show child status in nested folders",
  "status": "done",
  "parent": "E-1a88a55f",
  "depends_on": [],
  "implementer": "agent",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Show child status in nested folders

## Purpose and scope

Make child lifecycle status visible in folders without separating children from
their epic or grouped epics from their group. Authorized by the maintainer's
selection of nested child status folders.

## Acceptance criteria

- [x] Create children in their parent's backlog folder and move them on every lifecycle transition.
- [x] Move containers with their descendants; reopening refreshes nested paths correctly.
- [x] Validation rejects status/path mismatches and legacy flat child layouts.
- [x] Migrate this board without changing existing ticket metadata or bodies.
- [x] Document the incompatible draft layout change and migration; regression tests and board check pass.

## Approach and decisions

Use the same status-directory rule at every parent level, including grouped
epics. Keep IDs and lifecycle gates unchanged. Add explicit migration guidance
rather than silently rewriting another project's board. Implement, test, and
hand off for human review; no Git or publication actions.

## Verification

- `python3 -m unittest discover -s tests -v`: all 19 tests pass.
- `python3 work.py --root . check`: all 6 tickets validate.
- Coverage includes story/task lifecycle moves, review-to-WIP, dry runs, grouped
  epic moves, reopening completed ancestors, move rollback/collision protection,
  missing status folders, legacy layout rejection, and installed runtime use.
- Existing tickets were moved to matching nested folders without rewriting their
  metadata or bodies. T-a40da41b remains in review; the original three tasks
  remain in backlog.
- Runtime/README/convention now identify draft v0.2.0/v0.2. Migration is explicit
  and documented in CONVENTION.md. Source/development skill copies match.

## Handoff

Ready for human review in this epic's `review/` folder. Review work.py,
tests/test_work.py, README.md, CONVENTION.md, the synchronized skill instructions,
and the board moves. Use `python3 work.py show T-8c250b3f` to locate the task.
No human acceptance, commit, or publication is claimed.
