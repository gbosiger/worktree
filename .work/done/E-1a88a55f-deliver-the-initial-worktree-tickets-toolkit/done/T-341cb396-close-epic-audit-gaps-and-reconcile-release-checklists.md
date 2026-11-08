---
{
  "id": "T-341cb396",
  "kind": "task",
  "title": "Close epic audit gaps and reconcile release checklists",
  "status": "done",
  "parent": "E-1a88a55f",
  "depends_on": [],
  "implementer": "agent",
  "reviewer": "agent",
  "branch": null,
  "base_branch": null
}
---
# Close epic audit gaps and reconcile release checklists

## Purpose and scope

Close the two technical gaps found in the initial-toolkit epic audit and make
its current status understandable without interpreting superseded progress notes.
One ticket covers CI, retained-path previews, regression tests, and reconciliation
of the epic and its human review/release checklists.

Exclude new features, human acceptance, commits, publication, and real epic
integration. Preserve historical decisions and acceptance records.

## Acceptance criteria

- [x] CI validates the board using the existing launcher rather than removed work.py.
- [x] Ticket commit dry runs list each selected ID and its planned retained done path, including nested container moves, without changing files/index/history.
- [x] Regression tests cover the CI entrypoint and exact retained paths for leaf, subset, and container selections.
- [x] The epic distinguishes evidenced implementation completion, historical decisions, and remaining human/release gates; review checklists describe retained commits and post-merge cleanup, not removed prompts or old queues.
- [x] The full test suite, board validation, and whitespace checks pass; remote CI/publication limitations are recorded honestly.

## Approach and decisions

User requested one ticket for all audit follow-up. Use the existing clean
feature/E-1a88a55f-initial-toolkit checkout, base master, at d4d5cde. Parent is
already WIP; no branch setup or sibling status changes. Agent implementation,
then separately requested agent review.

Print retained paths from the existing retained_plan entries rather than
recomputing paths. Keep the current queue/selection and transaction semantics.
Use full Git history in CI because archived board dependencies require it.

## Verification

Run python3 -m unittest discover -s tests -v, ./work --root . check, and
git diff --check. Inspect human checklists without checking their approval items.
Local success does not establish a successful GitHub run for unpublished changes.

Implementation evidence (2026-11-07):

- python3 -m unittest discover -s tests -v: 159 tests pass (93.040 s).
- ./work --root . check: OK, 28 tickets; git diff --check: clean.
- tests/test_retained.py adds three public CLI regressions: exact leaf path,
  explicit subset isolation, and group/epic/task destinations after selected
  ancestor moves. Each compares all fixture file bytes, including .git/index,
  refs, and object files, before/after preview.
- tests/test_work.py adds a CI contract check for the launcher and fetch-depth 0.
  .github/workflows/tests.yml now runs ./work --root . check with full history;
  the same board command passes locally. No remote run of these unpublished
  changes is claimed.
- Dry-run printing uses existing retained_plan entries; selection, staging,
  commit transactions, and merge behavior are unchanged. docs/GIT.md explains
  planned retained paths versus already-staged changes.
- Epic README records delivered work/evidence, checks evidenced technical
  criteria, and isolates older handoffs as historical. Human/release criteria
  remain unchecked. T-5079b576 and T-b5d61768 checklists now describe canonical
  skills, implemented queues, retained commits, and post-merge cleanup.
- T-7fba91a2 records the audit's actual public d4d5cde baseline and failed CI
  URL, distinguishes that from these unpublished fixes, and states what new
  remote evidence is required. No human-task status or ownership was changed.

## Handoff

Stop in review; human review ownership and epic acceptance remain unchanged.

Implementation ready for separately requested agent review. Review this task's
code/tests/docs and the epic/human-checklist reconciliation as one bounded diff.
Actual checkout: /home/gbo/Projects/worktree-tickets on
feature/E-1a88a55f-initial-toolkit, recorded base master. Parent remains WIP;
this task hands off into review. No commit, push, merge, or human acceptance was
performed. Next action: request review of T-341cb396, then obtain the existing
human decisions; verify remote CI only after explicitly authorized publication.

## Acceptance record

2026-11-07T15:39:35+00:00 — agent: Reviewed CI (fetch-depth 0 + ./work --root . check launcher), dry-run retained-path printing in commit_command via retained_plan entries, 3 new retained regressions (leaf/subset/container, byte-for-byte dry-run preservation) + CI contract test, docs/GIT.md, and epic/human-checklist reconciliation. 159 tests OK; ./work --root . check OK (28 tickets); git diff --check clean. Selection/transaction semantics unchanged.
