---
{
  "id": "T-10a78e4e",
  "kind": "task",
  "title": "Fix portable temporary directories in CI preflight tests",
  "status": "done",
  "parent": "E-1a88a55f",
  "depends_on": [],
  "implementer": "agent",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Fix portable temporary directories in CI preflight tests

## Purpose and scope

Unblock GitHub Actions and the release-readiness review T-7fba91a2 by removing
the preflight test fixture's dependency on a local OpenCode temporary directory.
Reconcile the duplicate release-readiness ticket without losing user edits.
No runtime behavior, CI matrix, or release acceptance changes are included.

## Acceptance criteria

- [x] Preflight tests use Python's default temporary directory rather than requiring `/tmp/opencode`.
- [x] All nine preflight tests and the complete unit-test suite pass locally.
- [x] T-7fba91a2 has one valid WIP record preserving the maintainer's checkmarks and roles.
- [x] Board validation passes and remote CI verification remains explicitly outstanding.

## Approach and decisions

Created retrospectively on 2026-11-08 at the maintainer's request to give the
already-implemented fix its own ticket. The failure log for 22ef5ba shows nine
setup errors: the GitHub runner does not have `/tmp/opencode`. Removed the
explicit `dir` argument in `tests/test_preflight.py`, matching other fixtures.
Reconciled T-7fba91a2 into its WIP path, preserving human checkmarks and agent
implementer/human reviewer roles. No new human approval is asserted.

Actual worktree: `/home/gbo/Projects/worktree-tickets`, branch
`feature/E-1a88a55f-initial-toolkit`, base `master`; parent E-1a88a55f is WIP.
The maintainer explicitly authorized staging, committing, and pushing all current
changes, including the existing T-7ff2dcbf agent-role assignment. Publication
is a review checkpoint, not acceptance; do not move this ticket to done merely
to publish a CI repair.

## Verification

Against 22ef5ba plus the one-line test fix:

- `python3 -m unittest discover -s tests -v`: 174 tests pass (273.276 s),
  including all nine preflight tests. An initial 120-second tool timeout was
  followed by this successful complete rerun.
- `./work --root . check`: 46 live tickets passed before creating this ticket.
- `git diff --check`: clean.

Ticket creation adds documentation only; rerun board validation before commit.
Remote success is not established by local results. The maintainer will inspect
GitHub Actions after the authorized push.

## Handoff

Review the one-line fixture change and the verification evidence, then record
acceptance separately. T-7fba91a2 and E-1a88a55f remain WIP until their own gates
are satisfied. No release approval or integration is included.

## Acceptance record

2026-11-08T18:07:40+00:00 — human: n/a
