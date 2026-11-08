# Worktree Tickets

A minimalistic approach to structured work: **epics, stories, and tasks as
editable Markdown in your repository**, with explicit human–agent handoffs.
No service, database, or third-party Python dependencies.

Work connects to Git through ticket IDs. Approved work waits in `implemented/`.
`work commit` generates its message from that queue and moves tickets to `done/`
without deleting them. `work merge ID` integrates an approved, committed container:
an epic lands on its WIP release group with records retained; a standalone epic
or completed group lands on its final base with all records present, followed
by a separate cleanup commit. `work show ID` and
`work reopen ID` still recover tickets and their parents after squash merging,
without archive markers. See [Git workflow](docs/GIT.md).

## Get started

Requires Python 3.10+ on a Unix-like system. From this toolkit checkout:

```sh
./work setup             # Link the command into ~/.local/bin
work --help
```

If setup reports that its directory is not on PATH, add it to your shell's PATH.
You can also use `./work` directly, without setup. See
[installation](docs/INSTALLATION.md) for details and updates.

## Use in your project

```sh
work install ~/Projects/my-project
cd ~/Projects/my-project
work create epic "Search"
```

Installation adds a self-contained `.workkit/`, a `.work/` board, and links to
three agent skills—one copy each—preserving existing instructions. Commit them
with your project.
Use `work` for the linked toolkit version, or `./.workkit/work` for the project's
pinned copy—no global setup is needed for that local launcher.

## A small workflow

Use the real IDs printed by `create` in place of the example IDs below:

```sh
work create task "Search by title" --parent E-a1b2c3d4
work show T-1234abcd       # Locate the Markdown; edit its criteria
work preflight T-1234abcd  # Read-only context/gates; resolve blockers and decisions
work start T-1234abcd
# Implement and verify the change, then hand it off:
work review T-1234abcd
work list --status review
```

Tickets move through status folders inside their parent: for example,
`epic/review/task.md`, then `epic/implemented/task.md` after acceptance, and
`epic/done/task.md` after an explicit ticket commit. The feature
stays together when its epic moves. Agent skills guide preparation, execution,
review, and ticket-linked Git work.

For commands and options, use `work --help` or `work COMMAND --help` (or the
project's `./.workkit/work`). For rules, choose a focused reference from the
[convention index](CONVENTION.md)—there is no need to read every document.

### Find the next work

```sh
work list                        # Current branch's epic: backlog stories/tasks
work list --ready                 # Same queue, with dependency/lifecycle blockers removed
work list --status review         # Review queue (including an epic needing review)
work list --status wip            # Resume active work
work list --epic E-a1b2c3d4        # Explicit epic, independent of checkout branch
work list --all                   # Complete live board, all statuses
work list --all --status review   # Review work across epics
```

Automatic scope uses recorded epic/leaf execution branches, not branch-name
guessing. An explicit leaf branch overrides its epic. Missing, detached, non-Git,
or ambiguous context requires `--epic ID` or `--all`; an empty queue stays empty.
`--epic` and `--all` are mutually exclusive. Explicit `--status` includes matching
containers; scoped defaults show backlog stories/tasks only. `--all` keeps the
old whole-board listing unless filtered. This is an incompatible CLI default
change: scripts expecting every live ticket must now use `list --all`.

`--ready` selects only backlog stories/tasks whose own and ancestor dependencies
are implemented/done (including archived prerequisites), with all ancestors in
backlog/WIP. It can combine with either scope and `--status backlog`, but not
another status. It is not a new lifecycle status or a guarantee of authoring
quality, ownership, Git setup, or execution permission. Read the ticket and run
`work preflight ID` before starting.

## Short prompts in OpenCode

```text
/work-epic Add search by title
/work-task E-a1b2c3d4 Test empty search results
```

Project commands prepare ticket files using the same skills and CLI. Run board
and lifecycle actions in the terminal, for example `work list --status review`.
See the [OpenCode shortcuts](docs/OPENCODE.md) for the full list.

## Develop

```sh
python3 -m unittest discover -s tests -v
./work check
```

This checkout already has a `.work/` board. See [contributing](CONTRIBUTING.md),
[publishing](docs/PUBLISHING.md), and the [changelog](CHANGELOG.md).

Version 0.1.0. [MIT licensed](LICENSE).
