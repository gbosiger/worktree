---
{
  "id": "T-cca996b5",
  "kind": "task",
  "title": "Focus work discovery on the current epic and requested action",
  "status": "done",
  "parent": "E-1a88a55f",
  "depends_on": [],
  "implementer": "agent",
  "reviewer": "agent",
  "branch": null,
  "base_branch": null
}
---
# Focus work discovery on the current epic and requested action

## Purpose and scope

Help users and agents find the next implementation or review without dumping
unrelated epics. Implement focused CLI discovery and teach the canonical skills
which queue to use. Execute on this epic's recorded branch/base; no Git setup,
commit, publication, or acceptance of existing work is authorized.

## Acceptance criteria

- [x] Plain `list` shows backlog stories/tasks in the current branch's unique epic; explicit leaf branch overrides are respected.
- [x] `--status review` selects review work in that scope; `--epic ID` chooses an explicit epic and `--all` preserves the full live board, with optional status filtering.
- [x] Missing, detached, non-Git, or ambiguous branch context asks for explicit scope rather than silently listing everything or choosing an epic.
- [x] `--ready` computes dependency/lifecycle-unblocked backlog stories/tasks, including ancestor gates and archived prerequisites, without adding a stored status or claiming authorization.
- [x] Help, maintained docs, and canonical skills explain implementation, resume, review, readiness, and whole-board discovery; regression tests cover filters, edge cases, and no persistent writes.
- [x] Full unittest suite and dogfood board check pass; implementation evidence is handed off for separate review.

## Approach and decisions

Use recorded execution branch inheritance rather than branch-name guessing.
Default to backlog leaves; explicit status can include the epic itself (an epic
can need review). `--all` without a status keeps the old complete live listing.
Readiness is a computed filter, not a new lifecycle state: requirements quality,
ownership, Git setup, and authorization still require ticket reading/preflight.
Keep CLI status transitions and commit selection unchanged.

## Verification

- `python3 -m unittest discover -s tests -v`: all 174 tests passed in 256.470s,
  including eight focused discovery tests and strengthened ancestor-gate checks.
- `./work --root . check`: passed, 46 live tickets.
- `git diff --check`: passed.
- Manual dogfood checks: default list now shows only the two backlog tasks in
  E-1a88a55f instead of the complete 46-ticket board; ready/status/WIP/whole-board
  filters and CLI help behave as documented.
- `tests/test_list.py` covers branch overrides, explicit/whole-board scopes,
  non-Git, unborn/detached/shared/unmapped branch contexts, grouped epics,
  dependency and ancestor gates, implemented/done/archived prerequisites, flag
  conflicts, empty queues, and byte-for-byte board/Git preservation.

## Handoff

Implementation complete on 2026-11-08; awaiting separate human review. Read the
CLI change in `.work/tools/work.py`, `tests/test_list.py`, and the discovery
guidance in README, docs, and canonical skills. Try plain `./work list`,
`./work list --ready`, `./work list --status review`, and `./work list --all`.
Decide whether the focused defaults and explicit scope errors match the intended
workflow. `--ready` deliberately does not assess requirements quality or roles.

Actual checkout: `/home/gbo/Projects/worktree-tickets`, branch
`feature/E-1a88a55f-initial-toolkit`, recorded base `master`. All dirty paths are
this task's changes. Parent E-1a88a55f remains WIP; no siblings were started or
accepted. No branch setup, commit, publication, or acceptance was performed in
this checkout. Next action: review T-cca996b5 explicitly; do not self-accept.

## Acceptance record

2026-11-08T13:28:23+00:00 — agent: Agent review 2026-11-08: verified all six acceptance criteria against the diff (.work/tools/work.py, tests/test_list.py, docs, skills); unittest suite 174/174 passed; ./work check OK (46 tickets); git diff --check clean; manual list/--ready/--status review/--all behavior confirmed. Acceptance authorized by the project owner.
