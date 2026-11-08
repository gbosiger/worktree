---
{
  "id": "T-2e1b1dd2",
  "kind": "task",
  "title": "Find and reopen deleted tickets using Git file history",
  "status": "done",
  "parent": "E-1a88a55f",
  "depends_on": [],
  "implementer": "agent",
  "reviewer": "agent",
  "branch": null,
  "base_branch": null
}
---
# Find and reopen deleted tickets using Git file history

## Purpose and scope

Queue migration (T-060729db): this accepted record was not yet committed. It
moves from the old done queue to implemented under the new retained workflow;
the prior approval/evidence are unchanged, and no re-review is claimed.

Let maintainers read and reopen completed tickets deleted in an ordinary Git
commit, without special commit-message markers or manual recovery commands.
Keep the existing `show ID` and `reopen ID` interface and old archive support.

## Acceptance criteria

- [x] `show ID` reads a previously committed, accepted done ticket after an ordinary commit deletes it; the message needs no archive marker or ticket list.
- [x] `reopen ID` follows the saved parent IDs to restore missing epics/groups to WIP and the selected ticket to backlog, preserving content and acceptance history without overwriting current files.
- [x] Git-native history reads replace one Git process per historical commit; a repeatable benchmark records timings and process counts for thousands of commits and tickets.
- [x] Existing archive formats, dependency checks, ID uniqueness, re-archiving, branch isolation, and conflicting-history errors continue to work. Moves and unfinished deletions do not become accepted archives.
- [x] Documentation explains manual deletion, parent links, history requirements, and limitations. Full tests and the project board check pass.

## Review

Agent review (2026-11-07): read the full diff across `.work/tools/work.py`,
`tests/test_archive.py`, `tests/test_commit.py`, `tests/benchmark_archive.py`,
and the format/lifecycle/Git/README/CHANGELOG guidance. Verified against the
acceptance criteria and the supporting evidence recorded above.

Verified specifically: the `TicketFileHistory` interval index covers every
reachable commit (each commit's first-parent chain reaches a root, so the DFS
seeds all roots); the `at()` lookup reconstructs first-parent file state with
merges captured as first-parent diffs; the ancestry short-circuit is correct
(topological order places ancestors after descendants); deleted-entry parsing
distinguishes done removals from moves/renames; unfinished, invalid, and
duplicate-source deletions are rejected rather than becoming accepted records;
a later unfinished deletion cannot silently reuse an earlier approval. Legacy
v1/v2 archives remain readable and validated.

Independent evidence: `python3 -m unittest discover -s tests -v` passes all 131
tests (173.691 s); `./work --root . check` passes (24 tickets); `git diff --check`
is clean; `python3 tests/benchmark_archive.py --commits 3000 --tickets 2000
--batches 2000` reports median 0.613 s / 8 Git processes (previous reader 26.871 s
/ 7,025 processes on the same workload).

Non-blocking, out-of-scope observation: `commands/work.md` still states the
commit/archive CLI is not implemented, which predates this change and is
inaccurate. Left unchanged to preserve unrelated work; worth a separate ticket.

No blocking findings.

## Approach and decisions

Use Git's file history and batched object reads rather than a persistent database.
Only previously saved, accepted done files count as completed records; never
infer approval merely from deletion. Keep legacy markers readable, but make
markers unnecessary for ordinary file-history recovery. New `work commit`
messages omit the marker. Preserve existing writer safety and snapshot behavior;
changing publication or acceptance policy is out of scope.

Implementation uses one native `diff-tree --stdin` pass over the reachable
commit graph and `cat-file --batch` for messages and source blobs. A compact
per-ID file-change lookup preserves first-parent file states, including merges,
without copying the entire board for every historical commit. Existing full-DAG
archive conflict rules remain in effect. Parent restoration uses the existing
metadata links and lifecycle guards; no new linking format is introduced.

Execution belongs on the existing initial-toolkit epic branch
`feature/E-1a88a55f-initial-toolkit`, based on `master`. The epic is already WIP.
Existing authoring/ticket edits are unrelated and must be preserved.

## Verification

Test markerless child and parent deletion, moves, merges, conflicting versions,
old archives, incomplete history, and read-only lookup. Benchmark Git process
counts as well as elapsed time; do not claim constant-time history search.

Benchmark evidence (2026-11-07, this machine; three runs on disposable packed
repositories; history-reader time excludes CLI startup and board validation):

- `python3 tests/benchmark_archive.py --commits 3000 --tickets 2000 --batches 20
  --legacy-markers --baseline /tmp/opencode/work-history-baseline-n9pts0n0.py`:
  new reader median 0.328 s / 8 Git processes; previous HEAD reader median
  26.871 s / 7,025 processes. Both recover the same 2,000 records. The baseline
  is an unmodified copy of HEAD's runtime, not a committed project asset.
- `python3 tests/benchmark_archive.py --commits 3000 --tickets 2000 --batches
  2000`: final unmarked one-ticket-deletion run, median 0.613 s / 8 Git processes.
- New regressions cover ordinary deletions without IDs in messages, exact
  CRLF/unknown-field preservation, incomplete/invalid deletions, moves/renames,
  re-archiving, merged/unmerged branches, conflicting versions, duplicate IDs,
  legacy markers, and bounded subprocess counts. Lifecycle tests restore a
  task/epic/group deleted in separate commits, leave its sibling archived,
  preserve dry-run/index state, enforce dependent gates, and reject missing parents.
- An additional regression prevents a later unfinished deletion from silently
  reusing an earlier approval as current completion. A newly accepted, reconciled
  record clears that ambiguity.
- `python3 -m unittest discover -s tests -v`: all 131 tests pass (173.691 s).
- `./work --root . check`: passes with 24 live tickets after moving this ticket
  to review. `git diff --check` passes.

## Handoff

Implementation is ready for a separately requested agent review. Acceptance
checkboxes remain for that reviewer to verify; no reviewer approval is claimed.
Review `.work/tools/work.py`, `tests/test_archive.py`, `tests/test_commit.py`,
`tests/benchmark_archive.py`, and the updated format/lifecycle/Git/README guidance.

Actual checkout: `/home/gbo/Projects/worktree-tickets`, branch
`feature/E-1a88a55f-initial-toolkit`, recorded epic base `master`. The parent epic
remains WIP; siblings and pre-existing authoring/review-ticket edits are unchanged
by this task. No Git setup blocker, commit, publication, or epic acceptance.

Limitations: lookup still reads reachable history per command, not constant-time
storage. Manual deletion only preserves files already committed as accepted done
work. Older marker-only toolkit copies need updating before reading new archives;
existing v1/v2 history needs no rewrite. Missing parents/history are explicit
errors, never guessed completion.

Next action: request agent review of T-2e1b1dd2. Do not start that review or mark
done in this implementation run.

## Acceptance record

2026-11-07T10:22:12+00:00 — agent: Agent review: full diff read; 131 tests pass; board check passes; benchmark 0.613s/8 processes vs baseline 26.871s/7025. Verified interval index, ancestry short-circuit, move/rename vs deletion distinction, unfinished/invalid/duplicate rejection, stale-approval guard, and legacy v1/v2 readability. No blocking findings.
