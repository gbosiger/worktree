---
{
  "id": "T-cd66778b",
  "kind": "task",
  "title": "Move mechanical agent preflight checks into the CLI",
  "status": "done",
  "parent": "E-1a88a55f",
  "depends_on": [],
  "implementer": "agent",
  "reviewer": "agent",
  "branch": null,
  "base_branch": null
}
---
# Move mechanical agent preflight checks into the CLI

## Purpose and scope

Address the maintainer's T-5079b576 review finding: agents repeatedly spend
tokens collecting Git context and checking deterministic rules that the toolkit
can evaluate itself. Provide a compact, read-only execution-context check and
replace repeated mechanical skill instructions with that command.

Keep human/agent judgment about intent, dirty-work ownership, authorization,
and review separate from facts the CLI can establish. Do not add implicit Git
setup, lifecycle transitions, or acceptance.

## Acceptance criteria

- [x] One documented read-only CLI command accepts a selected ticket and reports actual checkout/worktree context, expected branch/base, ancestor statuses, dirty state, and concrete blockers in compact output.
- [x] Context resolution honors an explicit task/story branch, otherwise the epic branch/base, and the group branch for group-only work; it does not change ordinary commit-selection branch fallback.
- [x] Checks identify non-Git projects, detached HEAD, missing or mismatched targets, inconsistent hierarchy, and lifecycle/dependency blockers without modifying files, index, objects, refs, or worktrees.
- [x] Output distinguishes verified facts, blocking errors, and decisions still requiring the user/agent; it never infers dirty-work ownership or Git authorization from a successful check.
- [x] Canonical execution/preparation/commit skills and Git guidance use the shared check where appropriate instead of repeating shell inspections and deterministic validation, while retaining intent, authorization, review, and recheck safeguards.
- [x] An audit of similar repeated mechanical instructions records what was consolidated and what intentionally remains judgment-based; avoid an unrelated CLI redesign.
- [x] Regression tests and installed-toolkit verification cover the supported contexts, failure cases, output/actionable exit behavior, and read-only guarantees.

## Approach and decisions

Choose the command name and output contract during implementation; prefer one
small reusable context-resolution implementation over a separate agent-only
rules engine. Reuse existing hierarchy and dependency validation. A passing
preflight is a point-in-time observation, not a lock against later Git/editor
changes and not permission to stage, switch branches, commit, push, or accept.

Implemented interface: `work preflight ID`, with `--for commit` for branch
context without implementation lifecycle gates. Exit 1 reports blockers; exit 0
means mechanical checks passed, even if explicitly labeled decisions remain.
Target resolution is shared for groups/epics via their container metadata; it
does not modify commit selection. Explicit leaf branches use their own base
when recorded, otherwise the epic's base. No group-to-epic branch inheritance
is silently introduced.

Instruction audit: canonical work-execute and work-commit now delegate Git
status/branch/worktree collection and target/gate checks to preflight;
work-prepare delegates execution setup to the same command. docs/GIT.md owns
the output/exit contract. Board hierarchy, dependency/cycle validation, and
ancestor traversal reuse existing code. Remaining instructions intentionally
retain diff inspection/dirty ownership, intent and scope, role decisions,
authorized Git setup, outermost-first status actions, review/acceptance, and
rechecks after context changes. Staged-content inspection and commit dry runs
remain separate because context correctness does not establish commit eligibility.

Read docs/GIT.md, docs/LIFECYCLE.md, docs/FORMAT.md, canonical skills, and existing
CLI/install tests. Update canonical sources only. Coordinate with T-7ff2dcbf so
group/epic container context is shared rather than duplicated.

## Verification

Use disposable Git and non-Git projects. Cover explicit leaf overrides,
epic/group contexts, missing metadata/branches, detached HEAD, wrong checkout,
dirty tracked/untracked work, multiple worktrees, ancestor gates, and dependency
failures. Assert byte-for-byte state preservation and test the installed command.
Run `python3 -m unittest discover -s tests -v`, `./work --root . check`, and
`git diff --check`. Record evidence and remaining decisions before handoff.

## Review findings

Agent review (2026-11-08) — approved. Reviewed the working-tree diff
(`.work/tools/work.py`, `docs/GIT.md`, `README.md`, all three skills, and the
test changes), the new `tests/test_preflight.py` (9 tests), and the reused
helpers (`records`/`lookup`/`ancestors`/`check`/`Archives`/`_git`). Re-ran the
evidence independently:

- `python3 -m unittest discover -s tests -p test_preflight.py -v` — 9 tests OK.
- `python3 -m unittest discover -s tests -p test_work.py -v` — 36 tests OK,
  including the updated skill-contract assertions.
- `./work --root . check` — OK (44 live tickets); `git diff --check` — clean.
- `./work preflight T-cd66778b` and `--for commit` — correct branch/base, and
  dirty-work ownership surfaced as a Decision rather than an inferred fact.

All seven acceptance criteria are met with direct evidence; no blocking defects
found. Non-blocking observations: preflight runs outside the toolkit lock by
design and reports `.work/.lock`/commit journal as blockers; `execute` mode also
gates on unfinished dependencies of ancestors (stricter than `check`, and
deliberate); and the working tree also carries epic-level bookkeeping from the
convention review (T-5079b576 moved to WIP, new T-7ff2dcbf/T-fbcc26e0) that is
outside this task's scope and preserved intact. These three observations are
tracked for independent judgment in T-6824d1dc.

## Handoff

Backlog follow-up to human review T-5079b576, prepared 2026-11-08. Intended
execution branch/base are parent E-1a88a55f's
feature/E-1a88a55f-initial-toolkit / master; verify context and establish roles
before starting. No acceptance has occurred.

Implementation handoff (2026-11-08):

- Runtime: `.work/tools/work.py`; regression coverage: tests/test_preflight.py
  (9 tests) and updated skill-contract assertions in tests/test_work.py.
- Focused suite passed (9 tests, 10.441 s). Full command
  `python3 -m unittest discover -s tests -v` passed all 168 tests (250.336 s).
  The first full attempt hit the 120 s tool timeout; the complete rerun used
  a longer timeout and passed. No test failure was suppressed.
- `./work preflight T-cd66778b` passed on this actual dirty checkout and reported
  the correct epic branch/master base plus dirty-ownership decision.
- `./work --root . check` passed (44 live tickets); `git diff --check` passed.
- Read-only tests compare directory entries and file bytes, including Git index,
  refs, objects, and transaction artifacts. They cover non-Git and linked
  worktrees, explicit task/story overrides, group-only work, missing/invalid
  metadata/targets, detached HEAD, lifecycle/dependency gates, bad hierarchy,
  pending lock/journal refusal, and installed-runtime/skill usage.
- Limitation by design: observations are not a concurrency lock, and preflight
  does not decide ownership, approve work, or set up branches/worktrees.
- Context: /home/gbo/Projects/worktree-tickets on
  feature/E-1a88a55f-initial-toolkit, base master; parent E-1a88a55f stays WIP.
  Existing human review edits and unrelated backlog epics were preserved.
  No staging, commits, publication, or acceptance performed.

Next action: separate review of this task's runtime/docs/test diff. Pause here
per work-execute; T-7ff2dcbf and T-fbcc26e0 remain backlog and unimplemented.

## Acceptance record

2026-11-08T12:16:57+00:00 — agent: Agent review approved 2026-11-08: all seven criteria met; re-ran preflight (9) and test_work (36) suites plus board/diff checks, all clean.
