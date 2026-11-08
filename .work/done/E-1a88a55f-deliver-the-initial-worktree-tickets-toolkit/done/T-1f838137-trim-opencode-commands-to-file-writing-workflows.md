---
{
  "id": "T-1f838137",
  "kind": "task",
  "title": "Trim OpenCode commands to file-writing workflows",
  "status": "done",
  "parent": "E-1a88a55f",
  "depends_on": [],
  "implementer": "agent",
  "reviewer": "agent",
  "branch": null,
  "base_branch": null
}
---
# Trim OpenCode commands to file-writing workflows

## Purpose and scope

Maintainer direction: the LLM adds value to slash commands only when it writes
files — preparing tickets with descriptions, scope, and acceptance criteria.
Commands that merely execute a CLI verb duplicate `./work <verb>` in the
terminal and should not exist as LLM prompts.

Keep the four creation commands in `commands/` (with their `.opencode/commands/`
links): `work-group`, `work-epic`, `work-story`, `work-task`.

Remove `work-list`, `work-show`, `work-check`, `work-assign`, `work-depend`,
`work-start`, `work-done`, `work-reopen`, plus the general `work` dispatcher.
Each maps 1:1 to a terminal CLI verb; users run `./work <verb>` directly.
Docs replace removed shortcuts with the equivalent CLI form.

Out of scope: changing the CLI, skills, ticket format, or lifecycle itself.
Only the OpenCode command surface and its documentation/tests change.

## Acceptance criteria

- [x] `commands/` contains exactly `work-group.md`, `work-epic.md`, `work-story.md`, `work-task.md`; `.opencode/commands/` contains matching links and no dangling links to removed commands.
- [x] `work install` into a fresh target project creates only the four kept commands, without dangling links.
- [x] docs/OPENCODE.md lists only the four commands and shows the terminal CLI equivalent for every removed workflow (list, show, check, start, done, reopen, assign, depend).
- [x] No other doc, skill, or template references a removed slash command as an available shortcut.
- [x] Contract tests in tests/test_work.py expect the trimmed command set, and the full suite passes (`python3 -m unittest discover -s tests -v`).
- [x] `./work --root . check` passes after the changes.

## Approach and decisions

1. Delete the eight removed files from `commands/` and their links in
   `.opencode/commands/`.
2. Rewrite the `docs/OPENCODE.md` command table and examples; add a line that
   lifecycle actions are terminal commands (e.g. `./work start ID`).
3. Update the command-set assertions in tests/test_work.py (currently lines
   ~204–206 and 222–224 expect the full set).
4. Grep docs, skills, templates, and README for stale slash-command references.

Open question for the maintainer: `work-review` is removed per the stated
heuristic, but unlike the others it includes substantive analysis (reading
diffs against criteria), not just CLI execution. Restore it if the maintainer
prefers. `work` (general dispatcher) is removed because it routes lifecycle
requests back to CLI-only verbs; ask before restoring.

## Verification

Implementation checks (2026-11-07):

- `python3 -m unittest discover -s tests -v`: all 155 tests pass (91.331 s).
- `python3 -m unittest discover -s tests -p test_work.py -v`: 35 tests pass,
  including exact command/link inventory, fresh installation, relocation, and
  unchanged workflow contracts.
- `./work --root . check`: OK, 27 tickets.
- `git diff --check`: clean.
- Compared assignment/dependency examples against actual CLI `--help`.

Run `python3 -m unittest discover -s tests -v` and `./work --root . check`.
Verify `work install` output in a throwaway target project has only the four
commands. Confirm docs/OPENCODE.md matches the actual `commands/` directory.

## Handoff

Implementation (2026-11-07): removed ten canonical prompt files and their ten
repository links: the general dispatcher, eight query/lifecycle wrappers, and
the review shortcut. Kept the four creation templates unchanged. No CLI, skill,
format, or lifecycle behavior changed.

README.md now demonstrates only creation prompts and points board queries to
the terminal. docs/OPENCODE.md lists only the four kept prompts, gives terminal
examples for every removed workflow (including review handoff and dependency
removal), and distinguishes status transitions from actual implementation/review.
Its installation guidance now describes only the four canonical links.

tests/test_work.py asserts the exact repository command/link sets and verifies a
fresh installation contains exactly four valid relative command links. Removed
assertions that read deleted templates; skill/lifecycle preflight and review-pause
contract checks remain. Sweeps of docs, README, skills, and templates found no
removed slash commands advertised as available. Historical ticket records were
not rewritten. T-d190ce5e's separate documentation sweep should account for the
intentional removal of commands/work.md rather than recreate that dispatcher.

Execution context: /home/gbo/Projects/worktree-tickets on
feature/E-1a88a55f-initial-toolkit, matching the recorded epic branch; initial
checkout clean. E-1a88a55f remains WIP; no sibling statuses changed. No commit,
branch setup, publication, review, or acceptance is claimed.

Ready for separately requested agent review. Review the actual deletions,
README.md, docs/OPENCODE.md, and tests/test_work.py against the checked criteria
and verification above. Ticket handed off into review; parent remains WIP.

## Acceptance record

2026-11-07T13:27:38+00:00 — agent: Reviewed deletions of 10 slash commands and their 10 links; commands/ and .opencode/commands/ contain exactly the four creation templates. docs/OPENCODE.md lists 4 commands plus terminal equivalents for every removed workflow. Full suite: 155 tests OK; ./work --root . check OK (27 tickets). No stale slash-command references in docs/skills/templates/code. work-review guidance preserved in work-execute skill and LIFECYCLE.md.
