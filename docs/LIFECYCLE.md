# Lifecycle and acceptance

`backlog -> wip -> review -> implemented -> done`. Review can return to WIP with `start`.
`work done ID --by REVIEWER --evidence TEXT` records acceptance into `implemented/`.
That is the queue used to generate the next commit message. `work commit` commits
selected implemented tickets and moves them to retained `done/`; it does not delete
them. Done tickets stay with their container until final-base integration by
`work merge ID`, followed by an automatic separate cleanup commit. Epic-to-group
integration retains all records and keeps the group WIP; see GIT.md's policy table.
`reopen` returns a WIP, review, implemented, or done item to backlog. Reopening completed work
reopens completed ancestors to WIP, preserving historical acceptance records.
Add a new acceptance record when the item is completed again.

The CLI moves files between status folders inside their parent. Moving a
container carries all descendants without changing their statuses. Starting a
parent does not start its children. Children being complete does not accept
their parent: each level needs explicit acceptance, and a completed container
must have all its children complete. Use `show ID` to locate tickets after moves
and `list --status review` to find review work in the current branch's epic.
Use `list --all --status review` for review work across epics. Plain `list`
selects the current epic's backlog stories/tasks; `--epic ID` selects an explicit
epic. `list --ready` filters that backlog by accepted dependencies (including
ancestor dependencies) and backlog/WIP ancestor statuses. Readiness is computed,
not another stored status, and does not replace authoring judgment or preflight.

## Dependencies

Starting/advancing requires explicit dependencies to be implemented or done. Completion
prerequisites must be acyclic, including both explicit dependencies and the
requirement to complete a container's children. A child cannot depend on its
own parent, even indirectly. Parentage describes scope, not execution order.
Work inside a backlog parent can start; parent status is deliberate.

This is a low-level CLI allowance, not the default agent execution workflow.
Before implementing a selected ticket (including a design/documentation task),
work-execute first verifies the intended Git branch/worktree per GIT.md, then
explicitly starts backlog ancestors outermost-first and starts the selected item.
Already-WIP ancestors and unrelated siblings keep their statuses. Resolve paths
again after each container move. Stop on ancestor review/implemented/done status, a blocked
ancestor start, or a branch mismatch; resolve the gate or obtain an explicit
workflow exception rather than silently leaving the board inconsistent with
active work. The CLI itself still does not cascade `start` upward or downward.

Reopen completed dependents before their prerequisites, including any completed
ancestor that would also reopen. Reopen rejects affected completed dependents
before writing, including in dry runs.

## Archived tickets

After final-base integration, `work merge ID` removes the complete container tree in a cleanup commit.
Its parent integration commit retains every done ticket, so squash merging does
not lose the records. Ordinary Git deletion commits also support manually
managed history; no message marker is required. Unfinished deletions are not
treated as completion. `show` resolves archived IDs and reports provenance;
`check`, dependency and cycle validation, and ID allocation treat archived done
records as complete without reusing their IDs. `reopen` restores archived
content to its backlog location with the same ID, unknown metadata, and
historical acceptance records: completed ancestors are restored to WIP first,
archived completed dependents still block reopening until reopened, and
existing live files are never overwritten. Operations that need history fail
with guidance in shallow or incomplete clones rather than guessing. A live
ticket whose container is archived is tolerated by `check`; reopening the
ticket restores the ancestor structure, including for an already-backlog child
whose ancestor needs restoration. Reopening an archived container also relocates
its leftover live children to the restored container, preserving their statuses
and content; moving a live child container carries its descendants. Destination
collisions are refused rather than overwriting existing files.

The saved `parent` ID links a ticket to its epic and an epic to its optional
group. Reopening follows those IDs even when the parent and child were removed
in separate commits. If a required parent was never saved as accepted work and
is no longer live, restoration fails before writing rather than inventing it.

## Acceptance gate

The `done` command (acceptance into implemented) requires review status, checked acceptance items, a recorded reviewer,
`--by` matching that reviewer, and nonempty `--evidence`. The CLI recognizes
unchecked list items using `-`, `*`, `+`, or numbered markers such as `1.` and
`1)`, including indented items. Checked items use `[x]` or `[X]`.

This records an assertion, not authenticated identity or proof that a test
passed. Humans and agents remain responsible for accurate evidence. Do not
auto-check criteria. A script cannot judge the value or completeness of a spec.

## Human–agent handoff

Read the selected ticket, ancestor READMEs, explicit dependencies, and relevant
code/docs, not the whole archive. Establish unset implementer/reviewer roles
once with `assign`; honor agreed ownership without repeated questions.

At a pause or change of owner, update the selected ticket using the
[handoff example](AUTHORING.md#leave-a-handoff-when-there-is-work-to-resume).
A returning assignee starts there.

Implementation ends with evidence and a handoff into review. Review checks
scope, acceptance criteria, tests, and documentation. Record limitations and
return to WIP when needed. The reviewer can be another agent if agreed; separate
human review is not universally mandatory. Never invent another person's review
or accept on their behalf.

Agent execution pauses after handing WIP work into review, even when
both implementer and reviewer are `agent`. Role assignment is not authorization
to self-review. Wait for an explicit review request, allowing the user to switch
models/sessions; do not mark done or start dependent implementation meanwhile.
Only an explicit request for the full implementation -> review -> completion
cycle waives this default pause. A model switch alone does not perform a review:
the reviewer still checks the actual diff, criteria, and verification evidence.
This is a skill/workflow rule, not a new metadata field or CLI-enforced approval.

Individual writes are atomic; multi-file moves are not transactional. After an
interruption, repair any path/status mismatch and run `check`.
