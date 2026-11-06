---
{
  "id": "T-289852f6",
  "kind": "task",
  "title": "Simplify command setup and focused documentation",
  "status": "done",
  "parent": "E-1a88a55f",
  "depends_on": [],
  "implementer": "agent",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Simplify command setup and focused documentation

## Purpose and scope

Make the toolkit approachable without spelling out Python, reduce agent context
to operation-specific references, and introduce the workflow with short examples.
Do not claim that proposed commit-message archiving already exists.

## Acceptance criteria

- [x] Executable launcher works directly and can be explicitly linked as a command without overwriting existing commands.
- [x] Installed projects include a working launcher and all focused references their skills need.
- [x] Skills select operation-relevant references, not the complete convention or history; both skill copies match.
- [x] README introduces minimal structured work and its Git-history direction, with examples and help links.
- [x] Migrations/history live outside ordinary convention references; regression tests and board check pass.

## Approach and decisions

Add a standard-library launcher plus opt-in `setup --bin-dir` symlink creation;
do not change this user's PATH or global installation during development. Keep
copied project runtimes explicit. Split format, authoring, lifecycle, Git, and
installation references; make CONVENTION.md a small index. Move historical notes
to CHANGELOG.md and docs/MIGRATIONS.md. Clearly distinguish the planned archive
workflow from current completion behavior. Test direct, linked, and installed
launchers and safe conflict handling.

## Verification

Original implementation verification (historical; current results are below):

- `python3 -m unittest discover -s tests -v`: all 22 tests pass.
- `./work --root . check`: all 7 tickets validate.
- `./work --help`: direct executable displays the command help as `work`.
- Tests cover setup outside a board, repeated setup, command paths with spaces,
  refusing existing files/dangling links, launching through a symlink, copied
  runtime execution, installed references/version, and synchronized skill copies.
- No global setup was performed and no shell configuration was edited. Commit
  archiving remains planned and is explicitly labeled in README and docs/GIT.md.

## Handoff

Ready for human review: README.md, work, work.py, focused docs and convention
index, source/development skills, project instructions, and regression tests.
Find this task in the epic's `review/` folder, or run `./work show T-289852f6`.
To enable the global command explicitly, run `./work setup`; this was not run on
the user's home directory during implementation. No commit or publication made.

## Review remarks

- move work.py also to .work folder. Perhaps in a folder called tools
- do not forget to update the work script with the new location
- I do not think the tool works as it is.

## Review follow-up

Moved the canonical runtime from root-level work.py to `.work/tools/work.py`.
The executable `work` resolves its own location (including symlinks) before
loading that runtime. Template lookup, setup, and installation now resolve assets
from the toolkit root rather than the runtime's immediate directory.

Installed toolkits retain the same relative layout: `.workkit/work` loads
`.workkit/.work/tools/work.py`. Installation copies only the runtime, not this
repository's tickets. Updated docs/INSTALLATION.md describes both layouts.

Current verification:

- `python3 -m unittest discover -s tests -v`: all 28 tests pass.
- `./work --help`: succeeds with the relocated runtime.
- Regression coverage checks the absence of root-level work.py, ignores tools
  as board tickets, and exercises direct, symlinked, installed, and relocated
  launchers. A relocated installed launcher can create tickets, set up a linked
  command, check its host board, and install into another project.
- `./work --root . check`: final rerun succeeds, all 24 tickets validate.
  Earlier runs were blocked by T-0e7c2a61 (done/ path, review metadata); that
  mismatch was reconciled outside this change while work was ongoing. This
  task did not edit the unrelated ticket. Disposable-board lifecycle tests pass.

Returned this ticket to review using a direct Markdown status/path edit because
the unrelated board error prevents CLI transitions. Human reviewer: inspect
`.work/tools/work.py`, `work`, tests/test_work.py, and docs/INSTALLATION.md;
review the runtime relocation and installation behavior. Final board validation
now passes. No acceptance, global setup, commit, or publication is claimed.
