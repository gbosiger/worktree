---
{
  "id": "T-2c08fd6d",
  "kind": "task",
  "title": "Commit accepted tickets with safe archive removal",
  "status": "done",
  "parent": "E-1a88a55f",
  "depends_on": [
    "T-0d73eaf7"
  ],
  "implementer": "agent",
  "reviewer": "agent",
  "branch": null,
  "base_branch": null
}
---
# Commit accepted tickets with safe archive removal

## Purpose and scope

Add explicit work commit, combining accepted records and selected ticket
removals with the already-staged implementation snapshot. No branch switch or
default push; explicit `--push` may publish to the configured upstream.

## Acceptance criteria

- [x] New archive messages are ordinary Markdown: a short subject, one ID/title list, no embedded JSON, escaped ticket prose, or repeated metadata/history.
- [x] Complete accepted bytes are recoverable from the archive commit's first-parent tree; create an ordinary snapshot commit first when selected bytes are not yet committed.
- [x] History lookup/reopen support both the old v1 envelope and new v2 file-history format; malformed or missing source records fail safely.
- [x] Preview shows both messages if a snapshot is required. Failures/interruption preserve any already-created snapshot and restore tickets rather than rewinding history or claiming no commit occurred.
- [x] Select only accepted done tickets eligible for the current branch: explicit branch wins, unset branch falls back to current, and other branches/states remain untouched.
- [x] Read-only --dry-run shows selected IDs, branch, staged changes, removals, and exact proposed message without changing files, index, history, or invoking write hooks.
- [x] Successful execution preserves complete archive records and commits only the already-staged snapshot plus authorized ticket removals; unrelated unstaged content remains unchanged.
- [x] Completed containers are removed only when safe for all descendants, including already archived children; active descendants cannot be swept away.
- [x] Empty selection, detached HEAD, missing identity, conflicts, unsafe ticket staging, and stale selection produce actionable errors before destructive writes.
- [x] Commit/hook failures preserve recoverable ticket content and the pre-command index/worktree state under the documented safety contract; report recovery steps for interruption and refuse ambiguous/concurrently changed state.
- [x] Define and test hook/signing compatibility; preserve configured policy for supported validation hooks/signing, without silently disabling hooks/signing or changing Git configuration; report unsupported modifying hooks and concurrency limits honestly.
- [x] Tests verify exact staged bytes, branch selection, multiple tickets, dry-run snapshots, container removal, and injected commit/hook failures.
- [x] Subjects derive from ticket titles/IDs by default (`feat:` for epic/story/group, `task:` for tasks), with optional `-m` override.
- [x] Optional explicit IDs limit selection; containers cannot silently sweep unselected descendants.
- [x] Opt-in `--push` targets only the configured upstream; dry runs have no network and push failure clearly preserves/reports local commit success.
- [x] Command/option help includes concise descriptions/examples and the canonical work-commit skill explains the archive workflow.
- [x] A full repository backup precedes an isolated real archive commit verifying exact accepted records and cleared done ticket files without mutating this checkout's history.

## Approach and decisions

Readable-message redesign requested by the maintainer (2026-11-06): replace the
local bc611b0 checkpoint, restoring its eight archived records losslessly and
retaining its source changes. The old commit is backed up in a Git bundle.
New v2 messages contain a short generated subject, a Markdown completed-ticket
list, and one small version trailer. Full records stay in ordinary Markdown
files in the first parent, never duplicated into the message. If those exact
files are not already in HEAD, commit the staged snapshot before deletion. Both
commits honor hooks/signing. If the second commit fails, retain/report the first
commit and restore ticket files; never rewind a published ref. Extend the durable
journal to recognize both phases. Keep the old v1 codec/history reader for
compatibility. This explicitly supersedes the earlier full-message archive
contract and requires preserving snapshot parents through squash/rebase.

Use the approved safety contract and shared codec/reader. Ship only after
T-0d73eaf7 so successful removal cannot break board lookup or validation.

Implementation notes (resolve and test here, not in a separate review document):

- Generate a short title-based subject (or batch count) unless a one-line `-m`
  overrides it; sort IDs into one Markdown list and use a `Ticket-Archive: 2`
  trailer. Preserve full records in parent-tree files, not the message. Preview
  both exact messages if a snapshot is needed, and all removal paths.
- Require selected tickets to be staged regular files matching working bytes;
  reject untracked/partially staged board changes. Allow fully staged lifecycle
  moves. Validate the prospective staged board/archive, not just working files.
  Never substitute unstaged implementation content or recursively remove a
  container with active descendants or unknown ancillary files.
- Construct the commit using a private index, preserving the existing staged
  snapshot. Revalidate HEAD/branch/index/selected bytes; use an index lock during
  recovery. External Git/editor mutations are not serialized: do not run them
  concurrently. The original cross-process worktree/ref-lock proposal is not
  implemented and must not be claimed. Resolve supported
  index features, hooks, and signing during implementation; blanket rejection of
  hooks/signing is not an agreed product requirement. Document and test supported
  behavior and precise limitations. Retain journal/state on unexpected modifying
  hooks rather than bypassing configured policy or promising rollback of arbitrary external
  side effects. Surface material compatibility restrictions for human review.
- Keep a durable local journal of original and expected states before publication.
  Pre-publication failure retains original files/index/ref. After publication,
  report the commit OID even if cleanup fails; preserve concurrent edits and the
  journal. Block further mutations pending an explicit local recovery action.
  Recovery compares recorded states, never overwrites changed files/index or
  rewinds a published ref, and never creates a duplicate commit. Define the exact
  recovery interface, fault-injection tests, and honest concurrency limits here.
- Document implemented command/recovery behavior in docs/GIT.md before shipping.

## Verification

Implementation in `.work/tools/work.py`: `_git`/`_git_ok` helpers, `commit_branch`,
`commit_select`, `commit_prepare`, `commit_message`, `commit_preview`,
`commit_recover`, `commit_apply`, `commit_command`, and the `commit` subcommand
(`-m`, `--dry-run`, `--recover`). Regression tests in `tests/test_commit.py`
(17 tests). `docs/GIT.md` documents the command, selection, recovery, and
limitations; `CHANGELOG.md` records the feature.

- `python3 -m unittest discover -s tests -v`: all 87 tests pass (70 prior + 17
  new commit tests).
- `./work --root . check`: OK, 32 tickets. `git diff --check`: clean.
- Tests cover: dry-run shows branch/IDs/removals/staged/message with no writes;
  leaf archival syncs the board and records in history; exact staged bytes are
  committed while an unstaged edit is excluded; explicit-branch match/mismatch
  and unset-branch fallback; container kept with an open child and removed when
  all children done; multiple tickets in one commit; empty selection; untracked
  and unstaged board rejection; a failing pre-commit hook restores files and
  index and leaves HEAD unchanged; detached HEAD; missing identity fails before
  removal; and `--recover` both restores an interrupted removal and clears the
  journal after a published commit.

Known limitations for review:

- `git commit` runs with a private index seeded from the staged snapshot;
  hooks and signing are honored (never bypassed with `--no-verify`/
  `--no-gpg-sign`). The command is non-interactive (`GIT_TERMINAL_PROMPT=0`);
  interactive signing needs a preconfigured agent. Signing is not
  fault-injection tested beyond the hook test.
- Merge-conflict and stale-HEAD guards are implemented (unmerged-index and
  HEAD-revalidation checks) but are code-verified rather than fault-injection
  tested, because they need concurrent or conflicted index state.
- Recovery is best-effort and single-process: it serializes on `.work/.lock`
  and does not coordinate external `git commit` calls or recover arbitrary
  external side effects. The journal preserves original file bytes and
  restores them only when the commit did not publish.

## Handoff

Command examples:

```
work commit -m "feat(search): archive accepted work" --dry-run
work commit -m "feat(search): archive accepted work"
work commit --recover          # only after an interrupted commit leaves a journal
```

Review focus: `.work/tools/work.py` commit_* functions, `tests/test_commit.py`,
and the `docs/GIT.md` "Commit archive" section. Confirm the private-index commit
never mutates the real index on failure, hooks/signing are not bypassed, and the
recovery journal restores files only when the commit did not publish.

Next action: agent reviewer inspects the diff against the eight criteria and
records findings in this ticket.


## Human review remarks

- I do not like the command where you need to write the commit message, it should be autogenerated and take the ticket(s) content.
- It should use some autgenerated message that takes the ticket names instead of feat(search) with a feat() for epics and task() (or something more appropriate) for tasks
- Test this feature by first backing up everything somewhere safe and then execute a commit. We should see a commit with the tickets and done folder cleared.
  We want to provide optional list of which tickets so that not all are taken from the done folder.
- Consider also pushing when flag is set
- Provide more information for work commands and subcommands in help menu - it is not clear what means what. Also some exampels there would be cool (but do not overdo with complexity to make the help display too overwhelming)
- If a commit is not possible, make sure that things fail safely - commit does not carry out and files stay
- Consider integration with opencode (skills)

## Review findings (2026-11-06, agent reviewer)

Verification reproduced: `python3 -m unittest discover -s tests` passes 87/87,
`./work --root . check` OK (32 tickets), `git diff --check` clean. The eight
criteria are met as implemented: selection, dry-run, staged-only commit,
container safety, pre-write guards, hook/commit-failure recovery, hook/signing
honoring, and the regression matrix in tests/test_commit.py all check out.

Findings:

- **Medium (data loss on re-archive recovery)** — `.work/tools/work.py`,
  `commit_recover`: publication is detected with
  `all(identity in archive_history(...) for identity in ids)`. After a ticket is
  archived once, reopened, and completed again, its ID is already present in
  reachable history from the first archive, so an interrupted second commit that
  did NOT publish is reported as "already published". The journal is cleared and
  the removed file is never restored, losing the re-completed content. Repro:
  archive -> reopen -> re-done -> write a journal with `"commit": null` and
  remove the file -> `work commit --recover` reports "already published" and the
  content is gone. Fix: record the pre-commit HEAD OID in the journal and detect
  publication from HEAD advancement (or the recorded commit OID) rather than
  history membership, and add a re-archive + interrupted-commit regression test.

Required changes from the human review remarks (## Human review remarks):

1. Autogenerated commit subject: make `-m` optional and generate the subject
   from the selected ticket(s) — `feat(<scope>)` for epics and a task-appropriate
   type (e.g. `task(...)`) for tasks, with scope/description derived from the
   ticket title/slug; use a sensible combined subject for multiple tickets. Keep
   `-m` as an explicit override.
2. Optional ticket selection: add an explicit subset selector (e.g. `--tickets
   ID [ID ...]` or positional IDs) so not every done ticket is swept.
3. Optional `--push` flag (opt-in only). This amends the epic scope ("exclude
   pushes") and T-4e1573f6 rule 4 ("never push automatically"); record the
   amendment in the epic README and docs/GIT.md and keep push strictly explicit.
4. Richer help: give every command/subcommand and option a one-line description
   plus a small set of examples (epilog), without overwhelming the output. Today
   most subcommands and the `commit` options have no help text.
5. OpenCode integration: extend the work-commit skill and/or add a `work
   commit` OpenCode command describing the archive command, consistent with the
   existing skills/commands.
6. End-to-end verification before final acceptance: back up the repository, run
   a real `work commit`, and confirm the commit plus a cleared done/ folder,
   recording the result as evidence.

Docs to update with the fixes: docs/GIT.md "Commit messages" (generated-message
convention), CHANGELOG, and the epic README scope for `--push`. docs/FORMAT.md
only if the envelope/message format changes.

Disposition: returned to WIP for the recovery fix and the six human-requested
changes. Criteria remain met for the current behavior; the ticket's acceptance
criteria and approach will be amended by the implementer to cover the new
behavior.

## Review-fix approach (2026-11-06)

Preserve the v1 envelope and existing staged-only interface; add deterministic
title-based subjects, positional IDs, and strictly opt-in upstream publication.
Replace ID-membership recovery with a v2 journal containing exact pre/post states;
compare parent/tree/message to prove this transaction published. Refuse changed
state rather than reset staging or overwrite files. Test failure/interruption,
re-archive, selection, signing failure, and local-remote push. Update help and the
canonical work-commit skill (no extra OpenCode command needed). Back up the full
dirty checkout and run the real commit in an isolated copy; do not publish it.

Correction to the earlier review: passing the old 87 tests did not prove all
safety criteria. The original recovery overwrote changed paths and used a broad
mixed reset; unknown ancillary files could also be swept. These are addressed
in this fix, with explicit concurrency/modifying-hook limitations in docs/GIT.md.
The original promise to pre-detect arbitrary unsupported modifying hooks cannot
be guaranteed; the amended compatibility criterion requires honest reporting and
retained recovery evidence instead. Human/agent review of that limitation remains
required; this is not an acceptance record.

## Review-fix implementation evidence (2026-11-06)

- Generated `feat:` / `task:` subjects include normalized ticket titles and IDs;
  `-m` remains an override. The body retains a readable title/ID list and the
  unchanged complete v1 envelope.
- Positional IDs restrict selection. Selecting a container without every live
  descendant fails instead of implicitly sweeping unselected work. Removal units
  are deduplicated; unknown ancillary files/symlinks are refused. Selected ticket
  bytes must match staged blobs, including CRLF preservation.
- Optional `--push` requires an upstream before local mutation, refuses mirror
  remotes, suppresses automatic follow-tags/submodule pushes, and reports local
  success separately from remote failure. Only disposable local bare remotes
  were used for push tests; this checkout was not published.
- Journal v2 atomically records/fsyncs pre-HEAD, branch, expected tree/message,
  pre/post index bytes, original file bytes/modes. Recovery proves the exact
  direct-child commit; it never uses old ID membership, mixed reset, or blind
  overwrite. Ambiguous HEAD, changed files/index/branch, or legacy journals fail
  with the journal retained. Pending recovery blocks further board mutations.
- Help describes all subcommands/options and includes short examples. The
  canonical `skills/work-commit/SKILL.md` now explains selection, preview,
  authorization, staged-only behavior, publication failures, and recovery. No
  additional prompt-command template was needed.

Backup-backed real commit verification:

- Full dirty checkout (including `.git`, untracked files, and symlinks) copied
  before edits to `/tmp/opencode/worktree-tickets-backup-20261106-195131`.
  This is local temporary storage, not a permanent off-machine backup.
- Updated checkout copied to
  `/tmp/opencode/archive-smoke-20261106-195904/checkout`. Only in that disposable
  copy: stage its snapshot, preview and run
  `./work commit T-0d73eaf7 T-7147e599`. Commit
  `c4d7bf1598bed986b15804633bf3af06774bc40c` contains both exact original accepted
  records; both selected done files are gone; other done files stay. `work check`
  passes (30 live tickets), index/worktree clean. Preview/output retained beside
  the copy. This uses genuine recorded acceptance without inventing evidence.
- Separate synthetic fixture at
  `/tmp/opencode/archive-smoke-20261106-195904/all-done-fixture` ran actual
  `work commit` for all accepted tasks. Commit
  `2979b753aca8f99c9e5891677e21237c8c71986e` contains both complete fixture records,
  no done Markdown files remain, `work check` passes (one live epic), and Git is
  clean. Acceptance there is explicitly synthetic `test-fixture`, not a claim of
  human acceptance. Legacy dogfood done files without codec-compatible evidence
  were not rewritten/accepted merely to clear the real board.
- Signing was disabled only in disposable smoke repositories with a synthetic
  Git author; the actual checkout's identity/configuration was not changed.
  No commit, staging, branch operation, or push occurred in the actual checkout.

Compatibility requiring reviewer attention: ordinary validation hooks are
honored with the private index; configured signing failure preserves the original
HEAD/index/files. Successful cryptographic signing has not been integration
tested. Hooks that rewrite the message/index and concurrent external Git/editor
mutations are unsupported; an unexpected commit is reported with HEAD and the
journal retained for manual reconciliation. There is no cross-process ref lock
or promise to roll back arbitrary hook effects. See docs/GIT.md. The wider
original pre-detection/locking proposal is not claimed as implemented.

Final verification: `python3 -m unittest discover -s tests -v`: **104/104 pass**
(34 commit tests, 39 archive tests, 31 workflow tests). `git diff --check` clean;
`./work --root . check` OK (32 tickets). The final suite includes re-archive
interruption, recovery on both sides of publication, changed-file/index/HEAD
refusal, signing failure, validation/modifying hooks, CRLF, stale selected bytes,
subset/container behavior, local-bare-remote push, mirror refusal, and suppression
of unrelated branches/tags. No remote CI or successful crypto-signing result is
claimed. The compatibility criterion stays unchecked for reviewer assessment of
the documented unsupported-hook/concurrency limitations; do not auto-accept it.

Handoff: return T-2c08fd6d to **review** and stop. Current review path:
`.work/wip/E-1a88a55f-deliver-the-initial-worktree-tickets-toolkit/review/T-2c08fd6d-commit-accepted-tickets-with-safe-archive-removal.md`.
Execution context remains `/home/gbo/Projects/worktree-tickets` on
`feature/E-1a88a55f-initial-toolkit` (epic base `master`); epic E-1a88a55f stays
WIP, prerequisite T-0d73eaf7 stays done, dependent T-663511bc stays backlog.
No branch/setup blocker. Preserve all unrelated dirty work. Next action: an
explicit agent/human re-review of the fixes and compatibility decision, not
acceptance or dependent implementation in this run.

## Requested re-review and commit checkpoint (2026-11-06, agent)

Read the actual commit selection/prepare/message/apply/publication/recovery and
CLI code, changed skills/commands, board-consolidation diff, and current tests.
Re-ran `python3 -m unittest discover -s tests -v`: 104/104 pass. The re-archive
regression now proves this exact transaction's direct-child commit instead of
old ID membership; refusal tests preserve concurrent file/index/HEAD changes.
Subset/container guards, staged-byte preservation, ordinary hook failure,
signing failure, and upstream-only push tests pass. No blocking finding for the
planned hook-free, single-process local archive of the eight already-done tasks.

This is an agent re-review, not independent human acceptance. The existing
compatibility caveat remains: unsupported modifying hooks can publish a changed
commit, leaving the journal for manual reconciliation; successful crypto signing
is untested and external Git/editor operations are not serialized. No executable
Git hooks or signing override are configured in this checkout. Keep the
compatibility criterion unchecked and this ticket in review for the human
decision; do not equate committing this checkpoint with accepting this writer.

The maintainer requested the commit/archive operation and clarified that moving
the older tickets to done was approval. Timestamped confirmation is appended to
six legacy done records without rewriting their historical handoffs/dates. The
other two already contain valid recorded acceptance. All eight are to be archived
via `work commit` with their full records; this review ticket stays live.
The broader staged snapshot includes the initial-toolkit consolidation and its
reference-only updates in future backlog epics, not implementation of those
epics. Existing skill/preflight changes, tests, and publication-task retitle are
preserved as part of the authorized checkpoint. No push or epic completion.

## Readable v2 implementation and replacement handoff (2026-11-06)

At the maintainer's explicit request, backed up bc611b0 in
`/tmp/opencode/readable-archive-20261106-202820/before.bundle`, reset only that
local commit with `git reset --mixed HEAD^`, and restored all eight accepted
records byte-for-byte from its validated archive. No source edits were discarded,
no other branch changed, and no remote operation occurred. Returned this task
from review to WIP before implementation.

Implemented v2 writer/reader under this ticket:

- Generated subjects are capped at 72 characters; batches use a concise count.
  Each ID/title appears once in a Markdown completed-ticket list. One short
  version trailer enables reliable discovery; there are no JSON payloads,
  embedded acceptance logs, repeated ID footers, or unbounded joined subjects.
- Full records are read from normal Git blobs in the archive commit's first
  parent. A readable staged-snapshot commit precedes archival only when needed
  to preserve exact accepted bytes/modes. Both commits honor hooks/signing.
- The journal recognizes pre-snapshot, snapshot-only, and final-archive states.
  A snapshot-only interruption/failure restores files, retains/reports that
  commit, and permits retry without a duplicate snapshot or ref rewind. Changed
  state still fails closed. In-progress merge/cherry-pick/revert/rebase operations
  are refused before publication.
- V1 codec/history compatibility remains; v2 corruption, duplicate IDs, records
  not actually removed, or missing source files are rejected. Installed CLI,
  grouped-container restoration, CRLF, re-archive precedence, selection, staging,
  failed hooks/signing, and both publication boundaries have regression coverage.
- docs/FORMAT.md, docs/GIT.md, CHANGELOG.md, epic scope, and the canonical
  work-commit skill explain the incompatible writer change and the requirement
  to retain snapshot/archive parent trees through history rewrites. No automatic
  migration or claim that v2 survives deleting its only source tree.

Verification actually performed:

- `python3 -m unittest discover -s tests -v`: **116/116 pass** (46 commit tests,
  39 archive tests, 31 workflow tests). `git diff --check` clean; board check OK
  (32 tickets before archival).
- Full dirty checkout copied to
  `/tmp/opencode/readable-v2-smoke-yg_9c14f/checkout`; staged and ran actual
  `work commit` there. Snapshot dc1f48b087ca and archive 04675d06c3cd preserve
  all eight accepted contents exactly, clear all done Markdown files, and leave
  the isolated Git index/worktree clean. Board check OK (24 live tickets);
  reopening T-0d73eaf7 and rechecking succeeds in that copy.
- Its archive message is **555 characters**, down from 42,598; its subject is
  `task: archive 8 completed tickets`, down from 474 characters. The original
  file content/history remains recoverable without viewing it in `git log`.

Ready for human review; return this task to review before the authorized local
replacement commit. Preserve the eight already-approved done tasks and use the
new writer to archive them again. No writer acceptance or epic completion is
claimed; the hook/concurrency compatibility criterion remains the human decision.
Actual context is `/home/gbo/Projects/worktree-tickets`, branch
`feature/E-1a88a55f-initial-toolkit`, base `master`; epic remains WIP and dependent
T-663511bc remains backlog. No setup blocker or push authorization.

## Final review, findings, and resolution (2026-11-06, agent)

The maintainer removed human from this ticket's reviewers and explicitly
authorized review, findings/fixes, completion, and a local commit in this run.
This supersedes the earlier pending human compatibility decision for this task
only; epic acceptance and other human-owned tasks remain unchanged.

Reviewed the actual v2 reader and commit selection, preparation, message,
snapshot, publication, recovery, and push code against all criteria and the
regression suite, plus canonical work-commit guidance and the accepted
T-0d73eaf7 prerequisite. Findings resolved before acceptance:

- Low: recovery compared existing file bytes but not permission modes, so a
  recreated file with changed permissions could clear the journal as unchanged.
  Recovery now refuses either difference, preserving the file and journal.
  `test_recovery_preserves_concurrent_mode_edit_and_journal` covers this case.
- Coverage gap: signing failure was tested but successful signing was not.
  A disposable repository now generates an ephemeral Ed25519 SSH key, enables
  Git SSH signing, archives a task, and verifies BOTH snapshot and archive
  signatures with `git verify-commit`. Signing configuration stays enabled and
  unchanged, archive lookup works, and the fixture ends clean. The test skips
  when ssh-keygen is unavailable; it ran successfully on this machine.
- Documentation: corrected stale v1/one-commit and planned-feature statements
  in CHANGELOG.md; docs/GIT.md now states precisely which signing was tested.

Re-review of the fixes and full verification: 118/118 tests pass via
`python3 -m unittest discover -s tests -v` (48 writer, 39 archive, 31 workflow),
`./work --root . check` passes (24 live tickets), and `git diff --check` is clean.
The existing backup-backed real-archive evidence above remains applicable.
No blocking findings remain within the documented contract. Supported validation
hooks and SSH signing are verified; modifying hooks and concurrent external
mutations remain unsupported and fail closed with recovery evidence where
detected. OpenPGP and interactive hardware/agent signing are not claimed tested.
These honest limits satisfy the compatibility criterion; no arbitrary hook
rollback or cross-process serialization is claimed.

Execution context: /home/gbo/Projects/worktree-tickets on
feature/E-1a88a55f-initial-toolkit, epic base master. E-1a88a55f stays WIP;
T-0d73eaf7 is accepted/archived; T-663511bc stays backlog and becomes available
after this acceptance. No branch/setup blocker, publication, or epic acceptance.

Reviewer metadata was normalized from the maintainer's single-element
`["agent"]` array to the CLI's scalar `"agent"` via `assign`, preserving the
requested agent-only ownership. The first completion attempt refused the array
without writing; no acceptance gate was bypassed.

## Acceptance record

2026-11-06T20:06:17+00:00 — agent: Agent final review and fix re-review authorized by maintainer: all criteria verified; recovery mode-change guard regression and verified SSH signatures for snapshot/archive added; 118/118 tests pass; board check and diff check pass. Documented modifying-hook/concurrency and untested OpenPGP limits retained.
