---
name: work-prepare
description: Create, split, or clarify backlog tickets in a project with .work. Use for reviewing a proposed assignment before implementation.
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

Use the kind-specific guidance in `docs/AUTHORING.md`. For an epic, outline
the problem, delivery slices, and integrated demonstration. For a story, try
a concrete user scenario and its significant exception. For a task, identify
the input, deliverable, and how its recipient will evaluate it. Preserve open
choices that affect scope. Read the draft as the next assignee before handing
it over and replace any remaining template prompts. Keep the outcome
and observable checks in the ticket. Link shared product requirements at the
relevant section. Leave out empty sections and repeated child lists. For a
human reviewer, name what to inspect and the decision they need to make.
Before handoff, read each checkbox as a separate acceptance decision. Move
test variations for the same outcome into verification prose or a linked matrix.
For each dependency on a design choice, check that the producer’s acceptance
criterion names the recorded choice and where the consumer will find it. If
deferred, leave it open and identify the blocked consumer tickets.
Preserve IDs, dependencies, ownership, and unchecked work when editing.
Run `check` and report the ID plus any decision blocking the next step.

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
