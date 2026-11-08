---
name: work-execute
description: Implement, test, review, resume, or hand off a Worktree Tickets item in a project using .work, preserving status and acceptance evidence.
---

References are relative to `.workkit/` when installed, otherwise the toolkit root.
Use the preflight below; consult `docs/LIFECYCLE.md` and `docs/GIT.md` for gate
decisions or Git setup, rather than reloading their mechanical checks. Read
`docs/FORMAT.md` only when editing metadata or moving/creating ticket files.
Do not preload the convention index, unrelated references, or changelog.
Use `./.workkit/work` (or `./work` in the toolkit); `--help` lists commands.
Read the selected ticket, ancestor READMEs, explicit dependencies, and relevant
project instructions/code. Do not recursively read all completed tickets.

## Find the requested work

When no ticket ID is given, select the queue matching the request, not the whole
board. Use `./.workkit/work` (toolkit: `./work`):

- Implement new work: `list --ready` for mechanically unblocked backlog stories/tasks
  in the current branch's epic; `list` shows that epic's backlog including blocked work.
- Review: `list --status review`. Do not pick backlog work for a review request.
- Resume: `list --status wip`; inspect existing work before starting another item.
- An explicitly named epic: add `--epic ID` to the relevant queue. This selects its
  work regardless of branch; run preflight before execution, not on the wrong branch.
- Cross-epic discovery or planning: `list --all` (optionally `--status review` or
  `--status backlog`). Do not use it as the default implementation/review queue.

Automatic scope requires a unique epic mapped to the current branch by recorded
execution targets. If missing/ambiguous, choose explicit scope from the user's
intent or ask; do not silently broaden the search or pick another epic. An empty
queue is not permission to switch scope. Multiple candidates still require reading
their scope, ownership, and dependencies; ask when the user's priority is unclear.
`--ready` is computed, not a stored status: it checks accepted dependencies and
ancestor lifecycle gates, not requirements quality, roles, Git setup, or permission.
Read the selected ticket/ancestors and run preflight before edits. Discovery does
not authorize starting work, reviewing a human-owned item, or Git mutations.

## Execution preflight (before any ticket or deliverable edits)

Apply this gate on start, resume, review edits, and implementation, including
documentation/design tasks. A read-only question or board listing is not execution.

- Run `./.workkit/work preflight ID` (toolkit: `./work preflight ID`). It checks
  the board, branch/worktree, ancestor gates and dependencies, reports dirty
  paths and start order, and explicitly identifies non-Git projects. Do not
  repeat those mechanical inspections by hand. Read ticket/ancestor intent,
  not just the command's status summary.
- Stop on reported blockers, including another epic's branch. Report the
  actual/expected context and propose a concrete setup plan; use work-commit
  for authorized Git setup. A request to implement does not authorize branch
  creation, checkout, worktree creation, stash, commit, or relocation.
- Preserve dirty work. Never relabel ticket metadata to match a wrong checkout,
  silently carry changes across epics, or commit mixed-epic work to get unstuck.
  If work already began on the wrong branch, stop further ticket execution and
  propose safe, explicitly authorized relocation of the relevant changes.
  Do not claim the branch problem is fixed merely because skills were edited.
- Resolve required decisions: inspect the diff for dirty-work ownership and
  establish unset roles. Passing mechanical checks is not authorization.
  Rerun preflight after setup or context changes and before resuming execution.

## Execution and handoff

1. Establish implementer/reviewer only if unset, after preflight. Follow the agreed
   roles and authorization without repeated confirmation. Never claim someone
   reviewed work without evidence from them.
2. Confirm scope/criteria are actionable and dependencies complete. Write a short
   approach before coding. Before deliverable edits, start backlog ancestors
   outermost-first (group, then epic), then start the selected ticket. Leave
   already-WIP ancestors unchanged; do not start siblings or all children.
   Re-resolve paths with `show ID` after each container move. Dry-run the planned
   transitions when useful; a requested dry run must not perform any writes.
   If an ancestor is in review/implemented/done or a dependency/ownership gate blocks its
   start, stop and resolve the return-to-WIP/reopen or explicit workflow exception;
   do not silently work beneath a backlog/review/implemented/done ancestor. These are agent
   orchestration steps, not an automatic cascade in the CLI.
3. Implement a bounded change. Run checks appropriate to its risk and scope;
   record commands, outcomes, and limitations. Update lasting documentation where
   needed. Check criteria only against evidence.
4. Hand off into review, then stop by default, even when both implementer and
   reviewer are `agent`. Do not begin the review, mark done, or start dependent
   implementation in that run. Wait for an explicit review request so the user
   can switch models/sessions first. Role assignment is not review authorization.
   Skip this pause only if the user explicitly authorized the full
   implementation -> review -> completion cycle for the selected work; an
   implementation request, `reviewer: agent`, or generic "continue" is not that
   authorization. Honor narrower instructions to stop at review.
   Provide a concise summary and a specific next action. Include
   actual branch/worktree, selected and ancestor statuses, and any branch/setup
   blocker, not just the child ticket's status. Keep active ancestors in WIP;
   child review/completion does not accept or finish their parent. Stop
   dependent work when the chosen reviewer must act. Do not impersonate a human
   acceptance record. Reviewer identity in metadata is a convention, not security.
5. When reviewing, compare actual changes against scope and criteria; record
   findings and return to WIP when needed. Complete only with legitimate reviewer
   evidence and all children accepted. A resumed reviewer must read the actual
   diff, ticket, and verification evidence rather than treating the implementer's
   handoff or model change as proof of correctness. Changing models does not
   change recorded ownership or fabricate an independent review. Reopen work
   when criteria cease to hold.
   Acceptance via `work done` queues the ticket in implemented. Do not remove it:
   explicit `work commit` moves it to retained done, and only post-integration
   cleanup by `work merge ID` removes completed records. Epic-to-group integration
   retains done records and leaves the group WIP; only final-base integration
   cleans up a complete group or standalone epic. Both implemented and
   done prerequisites count as accepted; neither accepts their parent implicitly.
6. Use CLI dry runs for status changes when useful. Children move between status
   folders inside their parent; container moves carry descendants. Locate tickets
   with `show ID` after moves and include the current path in review handoffs.
   Run `check` after structural edits/merges. Git actions remain explicit and
   follow project authorization.
