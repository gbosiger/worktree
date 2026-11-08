---
{
  "id": "T-0d73eaf7",
  "kind": "task",
  "title": "Preserve board validation and reopening after archive",
  "status": "done",
  "parent": "E-1a88a55f",
  "depends_on": [
    "T-7147e599"
  ],
  "implementer": "agent",
  "reviewer": "agent",
  "branch": null,
  "base_branch": null
}
---
# Preserve board validation and reopening after archive

## Purpose and scope

Make archived tickets usable by existing board operations before an archive
writer can remove files. Preserve current acceptance and reopening rules.

## Acceptance criteria

- [x] show resolves an archived ID and displays its complete record with archive provenance instead of claiming it has an active file path.
- [x] check, dependency validation, cycle detection, and ID allocation account for archived records; missing evidence is not treated as completion and archived IDs are not reused.
- [x] Containers can complete with accepted archived children, but archiving a child neither accepts its parent nor hides active descendants.
- [x] reopen restores archived content to the correct backlog location with the same ID, unknown metadata, and historical acceptance; restore required ancestor structure without overwriting active files.
- [x] Completed ancestors reopen to WIP as required, completed dependents still block reopening, and dry runs leave files/index/history unchanged.
- [x] Regression tests cover mixed active/archived descendants, grouped epics, restored ancestors, collisions, dependencies, and repeated reopen/accept/archive cycles.

## Approach and decisions

Integrate T-7147e599 with records/get/check/create/transition behavior in work.py.
Do not weaken the explicit reviewer/evidence gate or introduce implicit Git writes.

Implementation notes:

- `Archives` wraps `archive_history` lazily: outside any Git work tree reads
  return `{}`, and unreadable history (shallow/missing objects) raises the
  codec's guidance only when an operation actually needs it. Routine commands
  on a fully live board never read history; `create` (ID uniqueness inside a
  Git work tree), `show`/`reopen` of archived IDs, non-live dependency checks,
  and reopen's dependent scan do read it and fail with guidance when shallow.
- `lookup` resolves live or archived tickets uniformly; archived records are
  complete by construction (the codec requires done status, a reviewer, and
  evidence), so archived dependencies never block start/done.
- `restore` recreates archived tickets from their validated provenance
  filename/slug under the current live ancestor paths. Leaves refuse to
  overwrite existing paths; a leftover container directory missing its README
  is completed in place. Unknown metadata and the whole body (including all
  historical acceptance records) round-trip unchanged.
- `check` tolerates a live ticket whose container is archived (directory
  agreement cannot be computed without a live parent); reopening the ticket
  restores the ancestor structure. The archive writer must not produce that
  state, and cycle detection walks dependencies through archived records.
- Reopen's dependent scan counts archived records only when no live copy
  supersedes them, matching resolve_archive's live-wins precedence.

## Verification

- `python3 -m unittest discover -s tests -v`: 64 tests pass (13 new archive
  lifecycle tests plus the existing 51).
- `./work --root . check`: OK, 32 tickets. `git diff --check`: clean.
- New regression tests in tests/test_archive.py (ArchiveLifecycleTests) cover:
  archived show with provenance, archived dependencies, mixed active/archived
  children at container completion, grouped-epic chain restore with metadata
  and acceptance history, reopen dry runs leaving board/HEAD unchanged,
  archived dependents blocking reopen, restore collision refusal at the API
  level, in-place container completion, repeated reopen/accept/archive cycles
  preserving both acceptance records, archived-ID non-reuse in create, shallow
  clones reporting guidance for history-consulting operations while routine
  commands keep working, forward commands refusing archived tickets, and the
  live-child-under-archived-parent state being tolerated and repaired.

## Handoff

Ready for review on feature/E-1a88a55f-initial-toolkit in
/home/gbo/Projects/worktree-tickets. Reviewer is `agent`; per docs/LIFECYCLE.md
execution pauses here — stop by default, do not self-review or mark done, and
wait for an explicit review request.

Review focus:

- .work/tools/work.py: Archives/lookup/restore, check/create/transition/reopen
  integration, and main() dispatch. Confirm the review gate (explicit reviewer
  + evidence) is untouched and no Git writes occur anywhere.
- tests/test_archive.py ArchiveLifecycleTests: confirm the fixtures simulate
  the T-4e1573f6 writer contract (envelope commit + file removal) honestly.
- docs/FORMAT.md, docs/GIT.md, docs/LIFECYCLE.md, CHANGELOG.md updates.

Known limitations for the record:

- The history scan stays uncached (T-7147e599 note); create/reopen in large
  repositories pay a full rev-list + cat-file scan. The writer task can add
  caching.
- In a shallow or incomplete clone, any operation that must consult history
  (create, show/reopen of archived IDs, reopen's dependent scan) fails with
  guidance by design. Routine commands on a fully live board are unaffected.
- A live ticket under an archived container skips directory agreement in
  check; that state is produced only by interruption or hand-editing and is
  repaired by reopening the ticket.

Next action: agent reviewer inspects the diff against the six criteria and
records findings in this ticket.

## Review findings (2026-11-06, agent reviewer)

Scope comparison: the implementation matches the six criteria and all claimed
verification reproduced in review: 64/64 tests pass, `./work --root . check` OK
(32 tickets), `git diff --check` clean, `.work/tools/work.py` contains only
read-only Git plumbing (`rev-parse`/`rev-list`/`cat-file` with
`GIT_OPTIONAL_LOCKS=0` and `GIT_NO_LAZY_FETCH=1`; single `subprocess.run`
site), and the `done` gate still requires `--by`/`--evidence` matching the
recorded reviewer. The fixtures in tests/test_archive.py honestly simulate the
T-4e1573f6 writer contract (envelope commit + file removal).

Findings:

- **Medium (returns to WIP)**: `create` fails in a Git repository whose HEAD is
  unborn. Repro: `git init` + `work init` + `work create epic X` ->
  `Cannot read archive history (rev-parse --verify HEAD^{commit}): fatal:
  Needed a single revision`. `create` now reads history for ID uniqueness
  (.work/tools/work.py, `create` -> `Archives.read()` -> `archive_history`),
  and a repo with no commits has no HEAD to verify. Before this change
  `create` never consulted Git, so the standard fresh-project bootstrap
  (also the `work install` onboarding path) regresses; it also contradicts the
  claim that routine commands on a fully live board keep working. A board with
  no HEAD cannot contain archives; treat that state as empty history rather
  than an error, and add a regression test (the suite always commits before
  `work init`, so this state is untested).

- **Medium**: reopening an archived container strands its leftover live
  descendants and wedges the board. Repro: interrupted writer leaves a live
  (done, wip, or backlog) child in the archived container's leftover
  directory, then `work reopen <container>`: the container is restored, but
  the child stays in the orphaned directory; `check` then fails
  ("parent/directory/status disagree") and, because `main()` runs `check`
  before every command, no further CLI command can run. The documented repair
  "reopening the ticket restores the ancestor structure" (docs/LIFECYCLE.md)
  holds only when reopening the child, and only when the child is not in
  backlog (the "Cannot move backlog to backlog" guard in `reopen_tickets`,
  .work/tools/work.py, refuses that case). Suggest relocating live descendants
  when `restore` recreates a container (or reopening a container), and extend
  the tolerated-state regression test to cover reopening the container first.

- **Low**: cycle validation walks archived records (.work/tools/work.py
  `check` `visit`, `archived_children`), but tests/test_archive.py has no
  cycle-through-archive case. Behavior looked correct in review (a live child
  depending on its parent is still rejected), but criterion 2's cycle claim
  rests on untested code; add a regression case.

- **Info**: the working tree also carries unrelated uncommitted changes
  outside this ticket's scope (skills/work-execute, work-prepare,
  work-commit; commands/work-review, work-start; the execution-preflight and
  review-pause sections of docs/GIT.md and docs/LIFECYCLE.md; the
  prompt-contract tests in tests/test_work.py; T-7fba91a2's retitle/move; and
  several backlog ticket edits). Preserved, not part of this review; they
  belong to other in-flight work and should be attributed and handed off
  separately.

Disposition: returned to WIP for the two Medium findings. Criteria 1, 3, 4,
5, and 6 are verified; criterion 2's archived-dependency and ID-allocation
behavior is correct but the `create` integration above must be fixed before
re-review.

## Review-fix implementation and handoff (2026-11-06)

Implemented the two Medium findings and the Low test-coverage finding at the
user's request. Historical review findings above are retained, not an acceptance
record for these fixes.

- `archive_history` returns empty history only for a symbolic HEAD whose branch
  ref does not exist (unborn HEAD). Existing refs still require readable commit
  objects; shallow-history checks remain. Added direct and installed-runtime
  bootstrap tests for epic and task creation before the first commit.
- `restore` preflights live-child destination collisions and containment before
  moving children into the restored container's status folders. Child bytes and
  statuses are preserved; moving an epic carries its nested tasks. Existing
  matching placements remain in place. A backlog child can use `reopen` to
  restore archived ancestors, but ordinary backlog-to-backlog remains refused.
- Added regressions for container-first restore with children in all four
  statuses (both group/epic and epic/task), backlog-child repair, dry-run board/
  index/HEAD preservation, collision refusal without changing existing bytes,
  and a dependency cycle closed through an archived record.
- Updated docs/GIT.md and docs/LIFECYCLE.md for unborn HEAD and orphan repair.
  Unrelated working-tree changes were preserved.

Verification actually run:

- `python3 -m unittest discover -s tests -p test_archive.py -v`: 37 tests passed
  before the final two regression tests were added.
- `python3 -m unittest discover -s tests -v`: all 70 tests passed, including the
  final two regressions (39 archive tests, 31 other tests).
- `git diff --check`: clean.

Handoff transition: `review T-0d73eaf7 --dry-run` previewed WIP -> review,
then `review T-0d73eaf7` performed it. `./work --root . check` passed afterward
(32 tickets). Current path:
`.work/wip/E-1a88a55f-deliver-the-initial-worktree-tickets-toolkit/review/T-0d73eaf7-preserve-board-validation-and-reopening-after-archive.md`.

Execution context: /home/gbo/Projects/worktree-tickets on
feature/E-1a88a55f-initial-toolkit, epic base master. Epic E-1a88a55f remains WIP;
T-7147e599 remains done; dependent T-2c08fd6d remains backlog. No branch changes,
commits, publication, or acceptance performed.

Next action: agent reviewer re-reviews these fixes and regression evidence after
an explicit review request. Stop at review; do not mark done or start dependents.

## Re-review (2026-11-06, agent reviewer)

Reviewed the fix diff against the three raised findings. No blocking findings.

- Unborn-HEAD `create` (Medium, resolved): `archive_history` returns `{}` only
  when HEAD is symbolic and its branch ref is absent; detached HEAD and existing
  refs still require readable commit objects, and shallow-history checks are
  unchanged. Verified directly: `git init` + `work init` + `work create epic`
  now succeeds (rc 0), and the installed-runtime path is covered by
  test_create_and_install_in_repository_with_unborn_head.
- Stranded descendants on container reopen (Medium, resolved): `restore`
  preflights live-child target collisions and `.work` containment before moving
  each child container/file into the restored container's status folder; bytes
  and statuses are preserved. Verified the original wedging repro: an interrupted
  writer with a done child under an archived container now reopens cleanly, the
  child relocates under the restored container, and `check` passes afterward.
  Backlog-child repair via `reopen` is covered by
  test_reopen_backlog_child_repairs_archived_parent; ordinary backlog-to-backlog
  remains refused.
- Cycle-through-archive coverage (Low, resolved): test_cycle_detection_follows_
  archived_dependencies exercises a live dependency closing a cycle through an
  archived record and asserts `check` rejects it.

Checks performed: `python3 -m unittest discover -s tests -v` (70/70 pass, incl.
39 archive tests), `./work --root . check` (OK, 32 tickets), `git diff --check`
(clean), and independent reproductions of both original failure scenarios. No
new Git write verbs: the only new plumbing is read-only `symbolic-ref` and
`for-each-ref` through the existing `_archive_git` wrapper. The `done` gate is
untouched.

Disposition: no changes required; criteria remain met and the fix regressions
pass. The ticket stays in review; acceptance (`done`) is not performed here and
awaits explicit authorization. The dependent T-2c08fd6d remains blocked until
this ticket is accepted.

## Acceptance record

2026-11-06T15:40:54+00:00 — agent: agent re-review 2026-11-06: six criteria verified, fixes confirmed via 70/70 tests, board check, independent repros
