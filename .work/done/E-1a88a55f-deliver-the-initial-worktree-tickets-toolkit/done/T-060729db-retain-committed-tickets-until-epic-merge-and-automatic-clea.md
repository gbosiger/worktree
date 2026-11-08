---
{
  "id": "T-060729db",
  "kind": "task",
  "title": "Retain committed tickets until epic merge and automatic cleanup",
  "status": "done",
  "parent": "E-1a88a55f",
  "depends_on": [],
  "implementer": "agent",
  "reviewer": "agent",
  "branch": null,
  "base_branch": null
}
---
# Retain committed tickets until epic merge and automatic cleanup

## Purpose and scope

Keep accepted tasks in the feature until the complete epic has been merged.
Preserve automatic commit messages by distinguishing accepted work awaiting a
commit (`implemented`) from committed records retained in the epic (`done`).
Merge and cleanup should be one explicit command, without a second user step.

## Acceptance criteria

- [x] Approval with `work done ID` puts reviewed work in `implemented/`; implemented and done prerequisites count as accepted, without accepting parents automatically.
- [x] `work commit` generates its message from selected implemented tickets, commits staged changes, and moves those tickets to retained `done/` without removing their content. Repeating it does not select already-committed tickets.
- [x] `work merge EPIC` requires a fully accepted and committed epic, squash-merges into its recorded base with ticket files present, then automatically creates a separate cleanup commit removing only that epic's completed records. It never pushes or deletes the source branch implicitly.
- [x] `show` and `reopen` find every task and its parents from the integration branch after cleanup, including when feature history is absent. Previously archived children are preserved during integration too.
- [x] Dry runs do not write; conflicts, failed hooks, interruption, dirty targets, and retries cannot lose files, redo a successful merge, or include unrelated work.
- [x] Back up this checkout before edits; test merging a copy of the current epic and verify the real checkout's HEAD/index/progress were not merged or reset.
- [x] Update lifecycle/format/Git guidance, skills, help, and regression tests. All tests and board validation pass.

## Approach and decisions

Use the existing epic branch `feature/E-1a88a55f-initial-toolkit`, base `master`.
The maintainer explicitly authorized implementing, reviewing, and testing without
another approval loop. This does not approve the unfinished parent epic or
authorize publishing. Real merge testing belongs in isolated copies only.

Verified full backup before edits:
`/tmp/opencode/worktree-tickets-before-retained-done-20261107-115421` (360 regular
files checked by SHA-256; includes .git, index, dirty files and untracked work).
Preserve all pre-existing work. Legacy archive readers/recovery stay compatible;
existing `done` records remain accepted/retained, not automatically requeued.

Implemented lifecycle: `work done` approves into implemented; `work commit`
selects that queue, writes a v3 recovery journal, and commits moves/content into
done without deletion. Messages still list only newly committed IDs/titles.
Completed containers carry already-committed children. Legacy v2 cleanup journal
recovery and the validated native/legacy history readers are retained.

`work merge EPIC` uses a clean recorded-base worktree (temporary when needed),
materializes older archived children, squash-integrates all records, then makes
the cleanup commit automatically. A Git-common-dir journal and per-epic/target
locks permit recovery without repeating a successful phase or moving source
refs. Unexpected hooks/concurrent changes leave data for inspection, never a
reset. No push or source-branch deletion. Intermediate group-branch cleanup is
refused rather than risking loss on a later squash; group-release orchestration
is not included in this epic-merge command.

The one accepted but uncommitted old done ticket, T-2e1b1dd2, was explicitly
migrated to implemented with its approval/history unchanged. Committed and
archived tickets were not requeued. Documentation, canonical skills and prompt
commands describe the new behavior; the stale commands/work.md claim from
T-d190ce5e is corrected, while that broader docs-audit ticket stays backlog.

## Verification

Use disposable repositories for normal/error/recovery tests and a separate copy
for the current-epic integration rehearsal. Never invent real human approval.

Current-epic rehearsal and restoration verified at
`/tmp/opencode/retained-epic-rehearsal-744bkgpb/report.json`:

- Copied the complete current checkout to before/merge-test/restored directories.
  The real unfinished epic first fails the merge readiness check as intended.
- Synthetic approval/completion exists only in merge-test, never this real board.
  Its feature snapshot includes all copied progress; no remote operation occurs.
- The copied master gets exactly two commits: integration f763637f687e61d0b4236cf2657ac9d54427f17d,
  then cleanup 13767db8541c3a4acd1dbd320488fe4d5e4c5470.
- All 18 live/previously archived epic records match the saved bytes and are
  readable in a fresh master-only clone, with no feature branch history.
  Reopening T-060729db restores its parent epic to WIP and itself to backlog.
- The restored copy matches the pre-test copy by SHA-256/symlink manifest.
  Real HEAD, master ref, exact index bytes, and working-file manifest are unchanged
  by the rehearsal. Real review gates and ticket ownership are not waived.

New public-CLI tests cover queue selection, retained content, message generation,
container moves, read-only dry runs, normal/failed/interrupted commits, concurrent
edit/index protection, merge conflicts and hook failures, phased recovery,
base-only clone restoration, legacy children, dirty targets, and duplicate merge
prevention. Historical archive-transaction regressions now live in
tests/test_cleanup.py, explicitly exercising the shared cleanup backend; they
are not assertions that the new public commit command deletes tickets.

`python3 -m unittest discover -s tests -v`: all 151 tests pass (228.976 s).
`./work --root . check`: passes (26 live tickets). `git diff --check`: clean.
Final safety comparison also confirms HEAD, master, exact .git/index bytes, and
.git/config still match the initial full backup. The pre-existing T-1f838137,
T-7fba91a2, docs/AUTHORING.md, and work-prepare skill edits are byte-for-byte
unchanged from that backup.

## Review

Agent review (2026-11-07), under the maintainer's explicit no-additional-loop
authorization: checked the actual queue selection/path planning, v3 file/index
recovery, source/base/acceptance gates, target-worktree ownership, legacy-child
materialization, ticket-byte preservation, exact integration/cleanup provenance,
phase retries, duplicate integration rejection, and canonical docs/skills/help.
Existing cleanup safety tests remain explicit backend tests, not claims about
the new public commit CLI. The public workflow is exercised end-to-end separately.

Resolved during verification: Git's diff auto-refresh initially changed index
stat bytes in a dry run; disable that optional behavior per invocation without
altering user configuration. Recovery handles interruption before merge and
after cleanup, and never resets an unexpected modifying-hook commit. Target
locks and pending-merge checks prevent overlapping toolkit merges on one base.

No blocking findings after fixes. Limitations remain explicit: arbitrary external
Git/editor races are not cross-process locked; conflicting/manual hook changes
require inspection rather than destructive automatic recovery. Intermediate group
integration cleanup is deliberately refused; automatic group release is not
implemented. Real parent-epic human review/publication requirements are unchanged.

## Handoff

Agent implementation and review authorized for this task only. Parent epic and
unrelated siblings retain their existing status and review requirements.

Actual checkout remains `/home/gbo/Projects/worktree-tickets` on
`feature/E-1a88a55f-initial-toolkit`, base `master`. This task's accepted work
queues in implemented for a later explicit commit. Parent E-1a88a55f stays WIP.
No real checkout commit, merge, reset, branch switch, or publication was performed;
all integration/recovery experiments were isolated fixtures/copies.

## Acceptance record

2026-11-07T11:29:49+00:00 — agent: Authorized agent implementation/review: all 151 tests pass; board and diff checks pass. Verified implemented-to-retained-done commits, automatic squash integration plus cleanup, exact recovery and conflict guards. Isolated current-epic rehearsal preserves all 18 records in a master-only clone and verifies restoration; real HEAD/master/index/config and prior progress are unchanged. No blocking findings; documented group-release limitation.
