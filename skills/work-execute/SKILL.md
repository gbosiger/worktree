---
name: work-execute
description: Implement, test, review, resume, or hand off a Worktree Tickets item in a project using .work, preserving status and acceptance evidence.
---

References are relative to `.workkit/` when installed, otherwise the toolkit root.
Read `docs/LIFECYCLE.md`. Read `docs/FORMAT.md` only when editing metadata or
moving/creating ticket files; read `docs/GIT.md` only for Git integration work.
Do not preload the convention index, unrelated references, migrations, or changelog.
Use `./.workkit/work` (or `./work` in the toolkit); `--help` lists commands.
Read the selected ticket, ancestor READMEs, explicit dependencies, and relevant
project instructions/code. Do not recursively read all completed tickets.

1. Establish implementer/reviewer only if unset. Follow the agreed roles and
   authorization without repeated confirmation. Never claim someone reviewed work
   without evidence from them.
2. Confirm scope/criteria are actionable and dependencies complete. Write a short
   approach before coding. Start only the selected work; do not start all children.
3. Implement a bounded change. Run checks appropriate to its risk and scope;
   record commands, outcomes, and limitations. Update lasting documentation where
   needed. Check criteria only against evidence.
4. Hand off into review with a concise summary and a specific next action. Stop
   dependent work when the chosen reviewer must act. Do not impersonate a human
   acceptance record. Reviewer identity in metadata is a convention, not security.
5. When reviewing, compare actual changes against scope and criteria; record
   findings and return to WIP when needed. Complete only with legitimate reviewer
   evidence and all children accepted. Reopen work when criteria cease to hold.
6. Use CLI dry runs for status changes when useful. Children move between status
   folders inside their parent; container moves carry descendants. Locate tickets
   with `show ID` after moves and include the current path in review handoffs.
   Run `check` after structural edits/merges. Git actions remain explicit and
   follow project authorization.
