---
{
  "id": "T-7ff2dcbf",
  "kind": "task",
  "title": "Support epic integration into release groups and final group merging",
  "status": "done",
  "parent": "E-1a88a55f",
  "depends_on": [],
  "implementer": "agent",
  "reviewer": "agent",
  "branch": null,
  "base_branch": null
}
---
# Support epic integration into release groups and final group merging

## Purpose and scope

Resolve the group-release limitation found during the first-release convention
review. Maintainers need a long-lived release branch (for example release/0.2.0)
represented by a group, with independently developed epics landing there before
the whole release integrates into its final base.

Implement both integration levels in the local CLI, with regression tests and
maintained documentation. Keep the existing backlog/wip/review/implemented/done
hierarchy; do not add a merged status or a cross-worktree tracking service.
Exclude remote publication, release tags, branch deletion, and GitHub PR automation.

## Acceptance criteria

- [x] `work merge EPIC` integrates a committed done epic into its recorded parent-group branch while the group remains WIP and other epics remain unfinished.
- [x] The group branch retains integrated epics under its done folder, including their completed stories/tasks; intermediate integration performs no ticket cleanup or implicit parent acceptance.
- [x] `work merge GROUP` integrates an explicitly approved, committed done group into its recorded final base only when all descendants are committed done and the accepted epic revisions are present on the group branch.
- [x] Final group integration preserves the complete accepted group/epic/child ticket tree in an integration commit, then removes only that group tree in a separate cleanup commit. Previously archived descendants are materialized when needed for squash safety.
- [x] From a fresh final-base-only clone after feature branches are removed, `show`, `check`, dependency validation, and `reopen` still resolve completed tickets and restore their parent chain.
- [x] Both integration levels provide read-only dry runs and resumable conflict/hook/interruption recovery; retries do not duplicate successful integration or cleanup, and already-landed unchanged work is rejected clearly.
- [x] Follow-up work on a previously integrated epic can be reopened, re-approved, committed, and integrated again without losing other epics or repeating already-landed changes.
- [x] Standalone epic integration retains its existing integration-plus-cleanup behavior; unrelated board content and source checkouts remain protected, with no implicit push or branch deletion.
- [x] Automated tests cover the release workflow and failure cases below, and maintained documentation, CLI help, and relevant workflow skills describe both merge levels consistently.
- [x] Groups and epics share container lifecycle, validation, integration, recovery, and cleanup machinery rather than parallel implementations; documentation explains shared rules once and limits kind-specific guidance to actual differences.

## Approach and decisions

- Extend the existing container abstraction: both groups and epics have a
  README and the same lifecycle subfolders. Groups contain epics; epics contain
  stories/tasks. Preserve the one-optional-group hierarchy, not arbitrary nesting.
- Reuse generic tree traversal, accepted-record validation, journaling, and
  recovery. Choose retention/cleanup policy from the integration destination
  (parent group versus final base), not duplicated group/epic command bodies.
- Document shared container behavior once, using a small hierarchy/policy table
  and a release example instead of copying the epic guide into a group section.
  Reuse common test scenarios for both kinds and add focused nested-integration
  cases for genuine differences.

- Example branch metadata: group branch release/0.2.0, base_branch master (or
  the project's actual default); child epic branches use release/0.2.0 as base.
  Support recorded branch names rather than requiring a naming convention.
- Use regular merge commits for epic-to-group integration to preserve ancestry
  for retries and follow-up changes; retain squash integration plus separate
  cleanup for group-to-final-base. Make the intermediate integration commit
  explicit even when Git could fast-forward.
- Status is branch-local: done means approved and committed on an epic branch;
  the accepted epic revision under done on the group branch shows it has landed.
  Mere presence of an older done epic must not hide newer unintegrated work.
- Preserve other epics' current lifecycle folders when merging branch-local
  board changes. Detect stale or conflicting ticket moves rather than silently
  restoring outdated sibling/group state.
- Extend merge journals and recovery deliberately, retaining recovery support
  for existing epic journals or documenting an actionable compatibility boundary.
- Read docs/GIT.md, docs/LIFECYCLE.md, docs/FORMAT.md and the existing merge/archive
  code and tests before implementation. Update those docs, relevant README/help,
  workflow skills, and draft compatibility notes where behavior changes.
- This task supersedes the initial epic's previous exclusion of automatic group
  release. It does not waive the current human review or release-readiness gates.

## Implementation notes (2026-11-08)

- Preflight passed on `/home/gbo/Projects/worktree-tickets`, branch
  `feature/E-1a88a55f-initial-toolkit`, base `master`, with a clean checkout,
  agent implementer/reviewer, and WIP parent E-1a88a55f. Started only this task.
- Extended the existing merge transaction for both container kinds. A retention
  policy selects explicit two-parent epic-to-group integration versus final-base
  squash integration and separate cleanup; no new status or metadata fields.
- Reconcile lifecycle files against the merge base before integration. Intermediate
  integration preserves the target's WIP group and sibling trees, refusing unrelated
  source board edits and divergent selected-tree changes. Final integration retains
  the existing nonconflicting unrelated-board merge behavior; cleanup is still scoped
  to the selected container. Staged board bytes are verified against the saved plan.
- Recursively materialize archived descendants through parent IDs. Group acceptance
  validates epic ancestry and accepted ticket contents, including archived descendants;
  deleted epic branches can be proven through retained merge parents. A newer local
  epic tip blocks release until integrated, including an unfinished follow-up tip
  (a conservative local safety gate, not cross-worktree tracking).
- Version-2 merge journals retain the version-1 field names for compatibility and
  add retention/board policy. Existing version-1 standalone-epic journals remain
  recoverable. Recovery covers regular merge parents, final cleanup, and interruption
  after an owned target worktree has already been removed. Unknown journals are kept.
- Maintained README, Git/lifecycle/format docs, canonical workflow skills, CLI help,
  and draft compatibility notes describe the shared rules and two destinations.

## Verification plan

- Build disposable repositories with two epic branches sharing a release group.
  Land one epic while its sibling is unfinished; land the second; explicitly
  complete the group and integrate it into the final base. Inspect ticket paths,
  statuses, integration history, and final cleanup boundaries at each step.
- Cover follow-up epic integration, unchanged duplicate attempts, divergent
  sibling board moves, wrong/missing branch metadata, unfinished descendants,
  unintegrated accepted revisions, dirty targets, and unrelated content.
- Exercise conflicts and failed hooks at intermediate integration, final
  integration, and cleanup; interrupt/resume without duplicating completed phases.
  Verify dry runs leave files, index, refs, objects, and worktrees unchanged.
- Verify archived descendant materialization and lookup/reopening of a leaf,
  epic, and group from a fresh base-only clone without feature history.
- Run `python3 -m unittest discover -s tests -v`, `./work --root . check`, and
  `git diff --check`; record results and limitations in the implementation handoff.

## Handoff

Implementation complete, awaiting separately requested agent review. Checkmarks
record implementation evidence, not reviewer acceptance. No acceptance, commit,
integration, branch setup, or publication was performed in this checkout.

Verification on 2026-11-08:

- `python3 -m unittest discover -s tests -v`: **192 tests passed** (153.732 s).
  Full output: `/tmp/opencode/T-7ff2dcbf-complete.log`.
- `tests/test_release.py`: 15 focused release regressions cover two independent
  epics, retained done trees with unfinished siblings, regular merge ancestry,
  final squash/cleanup, base-only clone show/check/dependencies and leaf/epic/group
  reopen, follow-ups, duplicate attempts, sibling conflicts, wrong/missing metadata,
  unfinished groups, unlanded accepted revisions, deleted epic branches, dirty
  targets, conflicts/hooks/recovery, cleanup interruption, post-worktree-removal
  recovery, recursive archived epic/leaf materialization, and dry-run snapshots.
- `tests/test_retained.py`: 26 regressions retain standalone behavior, including
  version-1 journal recovery, nonconflicting unrelated board additions, and
  re-approved follow-ups after final cleanup. These and the release tests reuse
  the same public-CLI fixture helpers and exercise the shared transaction.
- `./work --root . check`: 47 live tickets passed before handoff.
- `git diff --check`: clean before handoff. CLI `merge --help` lists group/epic IDs.

Actual context remains `/home/gbo/Projects/worktree-tickets`, branch
`feature/E-1a88a55f-initial-toolkit`, base `master`. Parent E-1a88a55f remains WIP;
its human convention/release gates are unchanged. Next action: review this task's
actual runtime/tests/docs diff and evidence, then record the review separately.
Tests use isolated disposable repositories; remote CI/publication was not run.

## Preparation record (historical)

Prepared from the maintainer's convention-review finding on 2026-11-08.
Backlog only: no implementation, acceptance, or Git integration is authorized
by ticket creation. Intended execution context is parent E-1a88a55f's recorded
feature/E-1a88a55f-initial-toolkit branch, based on master; recheck branch,
worktree, dirty-work ownership, and implementer/reviewer roles before starting.
The current review ticket remains unchanged so the maintainer can reference
T-7ff2dcbf in their own review remark.

## Acceptance record

2026-11-08T19:02:41+00:00 — agent: Independent agent review on 2026-11-08: read the full work.py merge diff plus test_release.py, test_retained.py additions, and doc/skill changes. Ran python3 -m unittest discover -s tests -v (192 tests OK), ./work --root . check (47 tickets OK), git diff --check (clean). All 10 acceptance criteria verified: group/epic shared machinery, retain-on-group vs squash-and-clean, recursive archived-descendant materialization, base-only clone show/check/reopen, dry runs and resumable conflict/hook/interruption recovery, follow-up integration, version-1 journal compatibility.
