---
name: work-prepare
description: Draft, refine, split, or review Worktree Tickets groups, feature epics, stories, and tasks in a repository with .work.
---

References are relative to `.workkit/` when installed, otherwise the toolkit root.
Read `docs/AUTHORING.md` and `docs/FORMAT.md` for preparation. Read
`docs/LIFECYCLE.md` only when defining dependencies, transitions, or acceptance
gates, and `docs/GIT.md` only when planning branch/commit work. Do not preload
the convention index, other references, or changelog.
Use `./.workkit/work --help` (or `./work --help` in the toolkit) to locate
commands. Read the relevant parent description, code, and docs before proposing
requirements.

Use `list --epic ID --status backlog` to check the relevant epic for duplicate
work. Use `list --all` (optionally `--status backlog`) for repository-wide planning
or finding an epic, not as the default execution queue. Plain `list` is the current
branch's epic backlog, not the complete board. `--ready` is a computed dependency/
lifecycle filter, not an authoring approval or a new stored status. Execution and
review discovery are described in work-execute.

1. Explain the beneficiary, outcome, scope, and exclusions at epic level.
2. Write observable acceptance criteria. Identify material edge cases, unresolved
   decisions, dependencies, and a sensible verification approach.
3. Split stories by behavior/value; use supporting tasks for substantial research,
   testing, maintenance, or review deliverables. Do not require a fixed phase split.
4. Group epics by shared outcome, not merely dependency. Record dependency IDs.
5. Check for duplicated work, ambiguous criteria, excessive scope, and unresolved
   requirements before calling an item ready. Report gaps instead of inventing
   answers. Establish implementation/review roles if they affect the next action.
6. Create/update Markdown using the templates and preserve immutable IDs. Place
   children in status folders inside their parent, matching metadata status.
   Keep durable docs in their proper location. Run `check` after structural edits.

## Write for the person doing the work

- Use plain language for the intended implementer/reviewer. Explain necessary
  technical terms on first use; avoid packing several checks into one sentence.
- Make each acceptance item a concrete outcome or decision. For human reviews,
  say what to read or try, where to find it, and what decision is needed. Name
  prerequisite reviews by ID and readable title, not "both final reviews."
- Separate agent verification from human judgment. Have the agent collect test
  results, version comparisons, and other technical evidence in a short summary
  with links and limitations before asking the human to approve it. Do not make
  the human decode raw logs or perform specialist checks an agent can prepare.
- Keep implementation details, rare technical safeguards, and authorization
  warnings in approach/verification/handoff sections or linked maintained docs,
  not buried in the human checklist. Preserve safeguards without making every
  reviewer learn their internals. Avoid adding sections that serve no real need.
- Before handing off, read the ticket from the assignee's perspective: can they
  tell what to do next, where to look, and what counts as success without asking
  for a translation? Rewrite jargon or vague references rather than explaining
  them only in chat. Mark missing evidence or decisions explicitly; never invent
  results or check criteria merely because the ticket was rewritten.

## Preparation-to-execution boundary

Preparing a backlog ticket does not start its epic or authorize implementation
on the current branch. Before handing off, identify the intended epic branch/base
and whether setup decisions remain open; do not invent actual branch metadata or
copy another epic's branch merely because this checkout uses it. Repository-wide
planning may happen on the current branch, but report that location and keep it
distinct from feature execution. A design/contract document that is itself a
selected implementation task uses work-execute, not a preparation loophole.

When asked to start or implement the prepared work, load work-execute and pass its
branch/worktree preflight before any execution edits/status changes using
`./.workkit/work preflight ID` (toolkit: `./work preflight ID`). Do not duplicate
its mechanical checks during preparation or treat it as Git setup permission. Then start
backlog ancestors outermost-first and the selected ticket, leaving siblings alone.
Unresolved branch/base or dirty-work relocation needs an explicit plan and Git
authorization via work-commit; "ready" does not mean checkout/setup already ran.
