---
{
  "id": "E-1a88a55f",
  "kind": "epic",
  "title": "Deliver the initial Worktree Tickets toolkit",
  "status": "done",
  "parent": null,
  "depends_on": [],
  "implementer": "agent",
  "reviewer": "human",
  "branch": "feature/E-1a88a55f-initial-toolkit",
  "base_branch": "master"
}
---
# Deliver the initial Worktree Tickets toolkit

## Outcome and value

A small open-source project can keep feature intent, stories, and human–agent
handoffs in Git, using an editor or dependency-free helper scripts. Maintainers
keep only active work as Markdown files, while accepted ticket definitions and
verification remain discoverable in Git history. Implemented folders queue
accepted work for commits; done folders retain it until full-epic integration.

## Scope

Include Markdown convention, lifecycle CLI, templates, project skills, tests,
copy-based adoption, publication instructions, execution-workflow fixes, and the
local commit archive described below. Exclude live cross-branch coordination,
automatic updates, automatic branch operations, and board UI. GitHub PR and
Neovim integrations remain separate backlog epics until this epic is closed.

Local archive scope:

- An explicit `work commit` command with a read-only `--dry-run` preview.
- Summarize eligible completed tickets in a readable Markdown commit message;
  move the implemented commit queue to retained done records without deletion.
  After an epic is fully accepted and committed, explicitly squash-merge it with
  all records present and automatically create a separate cleanup commit.
- Preserve ID-based lookup, completion dependencies, and reopening after archive.
- Exclude automatic staging of unrelated implementation files, acceptance of
  unfinished work, branch switching/creation, or implicit publication by the
  archive command. Explicit `--push` may publish only to the configured upstream;
  default operation stays local. No implicit commits from lifecycle commands or
  global service.

## Acceptance criteria

- [x] Create, start, review, complete, and reopen groups/epics/stories/tasks.
- [x] Validate IDs, hierarchy, dependencies, and completion evidence.
- [x] Adopt the toolkit in another project while preserving existing instructions.
- [x] Execution skills verify branch/worktree before edits, start backlog ancestors before the selected task without starting siblings, and preserve dirty work when setup is wrong.
- [x] Only accepted implemented tickets enter ordinary ticket commits; backlog, WIP, review, and already-committed done records are not selected as new work.
- [x] An explicit ticket branch selects that branch; an unset branch uses the current Git branch. Eligible tickets for the current branch are combined in one commit; tickets assigned elsewhere remain untouched.
- [x] `work commit --dry-run` previews selected IDs, branch, staged changes, retained done paths, and message without altering files, the index, or history.
- [x] The commit message is short readable Markdown listing IDs/titles; normal Git parent-tree files preserve complete metadata, prose, criteria, and acceptance evidence without embedding escaped payloads.
- [x] Ordinary commits retain completed ticket content in done. Explicit `work merge EPIC` integrates all records into the base before automatic cleanup, keeping the source checkout unchanged; no implicit push occurs.
- [x] Empty selections, detached HEAD, missing Git identity, merge conflicts, and commit/hook failures produce actionable errors. A failed commit leaves ticket content recoverable and preserves the pre-command index/worktree state.
- [x] Archiving children does not prematurely accept their parents or delete still-active descendants. Completed containers can be archived once all their children are complete, including children already archived.
- [x] `show`, `check`, dependency validation, and ID uniqueness understand archived tickets reachable in the current branch's history. Reopening restores archived content to backlog, preserves historical acceptance, and honors dependent/ancestor reopening rules.
- [x] Regression tests cover multiple tickets, explicit and fallback branches, dry runs, unrelated changes, failures, archived dependencies, container completion, and reopening. Focused docs, help, and skills describe the implemented workflow accurately.
- [x] Human reviews the draft convention, command interface, and example workflow.
- [x] Maintainer verifies the intended public repository contains the reviewed combined toolkit revision and records release-readiness evidence.

## Current delivery and remaining gates

The full scope is delivered and committed. Every child ticket is done — 16 live
done records plus 9 archived done records — including the two human reviews and
the public-revision check. GitHub CI passes on the public feature branch. The
epic is in review, awaiting the maintainer's explicit acceptance before local
integration into master.

| Work | State |
| --- | --- |
| Retained commits and automatic merge cleanup | T-060729db done |
| Markerless lookup and parent restoration | T-2e1b1dd2 done |
| End-to-end workflow and installation verification | T-663511bc done |
| Status-folder preservation | T-936a01b1 done |
| Four creation-only OpenCode prompts | T-1f838137 done |
| Maintained documentation audit | T-d190ce5e done |
| CI entrypoint, retained-path previews, reconciliation | T-341cb396 done |
| Convention/handoff judgment (human) | T-5079b576 done |
| CLI/adoption usability judgment (human) | T-b5d61768 done |
| Public revision and release readiness | T-7fba91a2 done |
| Group/epic integration and final merging | T-7ff2dcbf done |

Earlier accepted archive-contract/reader/lifecycle/writer records retain IDs
T-4e1573f6, T-7147e599, T-0d73eaf7, and T-2c08fd6d; resolve them with `work show`.

## Decisions and open questions

Current workflow: acceptance queues in implemented; explicit commits retain done
files; epic merge integrates the complete tree before a separate cleanup commit.
Lookup uses markerless file history; prototype message-only formats are not
part of the first-release contract (T-fbcc26e0). Older
dated decisions below document evolution, not requirements to restore obsolete
snapshot-first writers, message trailers, or removed slash commands.

- On 2026-11-07 the maintainer requested T-060729db: keep the message-generation
  queue as implemented, retain committed records in done, and automate a separate
  post-integration cleanup with `work merge`. This supersedes pre-merge removal.
  Backup and a current-epic merge rehearsal are required in isolated copies only;
  unfinished human gates in this real epic are not waived.
- On 2026-11-07 the maintainer requested T-2e1b1dd2: use Git file deletions
  rather than required archive markers, keep `show`/`reopen`, follow saved parent
  IDs to restore epics/groups, and measure lookup efficiency. New writer messages
  omit the marker; existing v1/v2 records remain readable. This authorizes local
  implementation, not Git commits, publication, or acceptance of the epic.
- On 2026-11-06 the maintainer rejected bc611b0's 474-character subject and
  escaped JSON payload and authorized undoing that local commit, restoring its
  tickets, fixing T-2c08fd6d, and committing again. The original is saved in
  `/tmp/opencode/readable-archive-20261106-202820/before.bundle`. The then-current readable v2 used
  a short subject, one ID/title list and one version trailer; full accepted files
  lived in the archive commit's parent tree. A normal snapshot commit was required
  when those exact files are not already in HEAD. This supersedes the earlier
  full-message archive design and was later superseded by T-060729db. Preserve
  old snapshot parents unless integration materializes their accepted records.
- On 2026-11-06 the maintainer requested generated commit subjects, explicit
  ticket subsets, clearer help, skill integration, backup-backed end-to-end
  testing, and consideration of opt-in push in T-2c08fd6d. The subsequent "do it"
  authorizes implementing those changes, not publication of this checkout.
  `--push` explicitly amends T-4e1573f6's local-only scope; no default push or
  implicit publication is introduced. Historical acceptance evidence is retained.
- On 2026-11-06 the maintainer requested consolidation of the two WIP epics.
  E-0182afb4 (Archive completed tickets in Git commits) was absorbed into this
  epic, retaining E-1a88a55f and feature/E-1a88a55f-initial-toolkit based on master.
  Its requirements and all five child IDs/statuses/dependencies are preserved;
  the former epic is retired, not marked accepted or available as a CLI alias.
  External references/dependencies now use this surviving epic. No Git merge,
  branch switch, commit, or acceptance is implied by the board consolidation.
- Roles remain agent implementer/human reviewer. Finish and review this combined
  initial-toolkit epic before beginning the later feature epics.
- Keep the acceptance gate: `work done` queues in implemented; `work commit`
  retains committed records in done until post-integration cleanup.
- T-4e1573f6 contains the short archive behavior proposal for human review.
  Encoding and recovery details belong to the reader/writer implementation tasks;
  never substitute unstaged implementation changes for staged bytes.
- Archive selection still falls back to the current branch for a ticket with no
  explicit branch. Do not silently add epic/group inheritance to that command;
  the execution skill's branch-context check is a separate policy.
- Preserve archive records through squash/rebase. Report shallow/missing history
  rather than treating missing prerequisites as accepted. See docs/GIT.md and
  update lasting docs with approved format/recovery decisions during implementation.

## Current verification and handoff

Verification (2026-11-08): 192 tests pass, `./work --root . check` validates the
board, and GitHub CI passes on the public feature branch at commit 767a56f. The
epic is in review awaiting the maintainer's acceptance; acceptance (`work done`),
the retained commit (`work commit`), local integration into master
(`work merge E-1a88a55f`), and any publication remain separate, explicitly
authorized Git actions.

## Historical verification and handoffs (superseded)

The notes below preserve earlier evidence and decisions. Their test counts,
statuses, pending-review requests, and next-task instructions are historical;
use the current summary above and `work show ID` for present status.

Latest update (2026-11-07): T-060729db implements the implemented commit queue,
retained done files, and explicit squash integration with automatic cleanup.
Agent implementation/review is authorized without another maintainer loop; its
approval queues in implemented, not a real Git commit. All 151 tests pass and
board/diff checks pass. The current-epic rehearsal preserved all 18 records in a
master-only clone and verified restoration with real HEAD/master/index/progress
unchanged. This real epic stays WIP and its human gates are not waived. See the
task for backup/rehearsal paths, recovery evidence, and group-release limitations.

Implementation update (2026-11-07): T-2e1b1dd2 implements markerless Git-native
deleted-ticket lookup and parent restoration, retaining legacy archive support.
All 131 tests pass; benchmark evidence and compatibility limits are in that task.
It is handed off for a separately requested agent review, not accepted. This epic
stays WIP; existing final human review/publication gates remain in place.

Latest review (2026-11-06): the maintainer changed T-2c08fd6d to agent-only
review and authorized its full review/fix/completion cycle and local commit.
The final agent review resolved a recovery file-mode guard gap, verified actual
SSH signatures on snapshot and archive commits, and corrected stale changelog
claims. All 118 tests pass; board check passes (24 live tickets). T-2c08fd6d is
accepted by agent under the documented hook/concurrency contract;
T-663511bc remains backlog as the next task. Epic acceptance and the other human
review/publication gates remain unchanged. Earlier pending-human notes below
are historical for T-2c08fd6d, not a current task-level gate.

Current update (2026-11-06): T-0d73eaf7 is accepted; T-2c08fd6d remains in
review after its fixes and requested agent re-review. The readable-v2 follow-up
under the same task passes 116 tests and replaces the rejected local checkpoint;
new messages contain only a short subject/list, with complete records in Git
parent-tree files (and a snapshot commit when needed). The
maintainer authorized a local checkpoint commit and archival of the eight
already-done tasks, clarifying that moving the older tasks to done was approval.
Six legacy records now include a timestamped confirmation without backdating
their reviews. Use `work show ID` for records after archival. Writer compatibility
limitations still require the human decision in T-2c08fd6d; a checkpoint commit
does not accept that task or this epic. All existing dirty changes were reviewed
as toolkit work/consolidation and associated backlog-reference/preflight updates;
later epic implementation is not included. Final acceptance/publication gates
are unchanged. The older progress notes below are historical, not current status.

The local suite passes 70 tests, including workflow prompt-contract checks,
ancestor-start sequencing, 20 archive codec/history tests, and 13 archive
lifecycle tests plus six review-fix regression tests. The read-only archive APIs are implemented and accepted
(T-7147e599), and the history-aware CLI lifecycle is implemented for T-0d73eaf7
and handed off into review; the archive writer command is not implemented. CI
is configured for Python 3.10, 3.12, and 3.13; no new remote CI run or
acceptance is claimed.

After consolidation, `./work --root . check` passes. Consolidation checks
confirmed one WIP epic on its recorded branch, all five moved child
IDs/statuses/dependencies preserved, and downstream dependencies retargeted.
Reader/writer implementation notes now live in their tasks; the human proposal
is in T-4e1573f6. The only remaining reference to the retired epic is the
consolidation note above.

Actual checkout: /home/gbo/Projects/worktree-tickets on
feature/E-1a88a55f-initial-toolkit. This surviving epic is WIP. T-7147e599 was
accepted by the human reviewer on 2026-11-06 (see its acceptance record).
T-0d73eaf7's agent review (2026-11-06) found two Medium issues (unborn-HEAD
`create` failure and stranded live descendants when an archived container is
reopened). The requested fixes and archived-cycle regression coverage are now
implemented and handed back into review, with 70 passing tests; see its review-fix
handoff. No re-review or acceptance is claimed. Do not start its dependent
T-2c08fd6d meanwhile. Remaining archive tasks stay in
backlog. Final human reviews and publication verification follow the release
gates above. No additional task acceptance, commit, or publication is claimed.

## Acceptance record

2026-11-08T19:44:14+00:00 — human: usage of the tool for the tool developement
