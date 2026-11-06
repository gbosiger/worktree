---
name: work-prepare
description: Draft, refine, split, or review Worktree Tickets groups, feature epics, stories, and tasks in a repository with .work.
---

References are relative to `.workkit/` when installed, otherwise the toolkit root.
Read `docs/AUTHORING.md` and `docs/FORMAT.md` for preparation. Read
`docs/LIFECYCLE.md` only when defining dependencies, transitions, or acceptance
gates, and `docs/GIT.md` only when planning branch/commit work. Do not preload
the convention index, other references, migrations, or changelog.
Use `./.workkit/work --help` (or `./work --help` in the toolkit) to locate
commands. Read the relevant parent description, code, and docs before proposing
requirements.

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
