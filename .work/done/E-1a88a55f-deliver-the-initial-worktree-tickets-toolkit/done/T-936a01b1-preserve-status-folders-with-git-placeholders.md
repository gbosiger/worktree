---
{
  "id": "T-936a01b1",
  "kind": "task",
  "title": "Preserve status folders with Git placeholders",
  "status": "done",
  "parent": "E-1a88a55f",
  "depends_on": [],
  "implementer": "agent",
  "reviewer": "agent",
  "branch": null,
  "base_branch": null
}
---
# Preserve status folders with Git placeholders

## Purpose and scope

Keep empty status folders visible after Git checkout, including implemented at
the board, group, and epic levels. Fill the existing board's missing placeholders
without moving tickets or changing their statuses.

## Acceptance criteria

- [x] The existing board and every live container have an empty .gitkeep in each status folder, including implemented.
- [x] Tests cover placeholders at board/group/epic levels and confirm Git retains their empty implemented folders.
- [x] Migration instructions explain adding placeholders to existing groups and epics without changing ticket content or status. Tests and board validation pass.

## Approach and decisions

Use the current epic branch feature/E-1a88a55f-initial-toolkit, based on master.
New boards/groups/epics already initialize all five folders. This is a missing
repository-asset/migration fix, not a new lifecycle state or an implicit repair
on read-only CLI commands. No real groups currently exist; test groups in a fixture.

## Verification

Run the complete unittest suite, board check, and diff whitespace check.

Implementation evidence: added seven empty placeholders across the board and
three existing epics. All five status folders now have .gitkeep files at each
live container. No existing ticket was edited or moved. There are no live groups
in this board; fixture tests cover grouped and standalone epics, and verify that
Git's committed tree contains implemented/.gitkeep at board/group/epic levels.

`python3 -m unittest discover -s tests -v`: all 154 tests pass (229.446 s).
`./work --root . check`: passes (27 tickets). `git diff --check`: clean.
Runtime code is unchanged; docs/MIGRATIONS.md now explicitly explains this
folder-only migration for existing groups and epics, without implicit repair.

## Handoff

Agent implementation, then separately requested agent review. The parent epic
remains WIP; no commit, publication, or sibling status change is authorized.

Ready for agent review on feature/E-1a88a55f-initial-toolkit (base master), in
/home/gbo/Projects/worktree-tickets. No branch/setup blocker. Review the seven
placeholders, docs/MIGRATIONS.md, and the three new tests in tests/test_work.py.
Acceptance remains unchecked for the reviewer; no approval or completion claimed.

## Review

Agent review (2026-11-07): verified all seven new empty .gitkeep files cover
the five status folders at the board root and in each of the three live epics;
no group exists in this board, so grouped behavior is covered by fixtures.
Confirmed no existing ticket content or status changed. `git ls-tree` test
proves committed trees retain empty implemented folders at board/group/epic
levels. 154 tests pass, board check passes, diff check clean. No blocking findings.

## Acceptance record

2026-11-07T11:51:55+00:00 — agent: Agent review: all seven .gitkeep placeholders verified across board root and three live epics; no ticket content/status changed. Tests prove committed trees retain empty implemented folders at board/group/epic levels. 154 tests, board check, and diff check all pass. No blocking findings.
