# Worktree Tickets

A minimalistic approach to structured work: **epics, stories, and tasks as
editable Markdown in your repository**, with explicit human–agent handoffs.
No service, database, or third-party Python dependencies.

Work connects to Git through ticket IDs and commit messages explaining what
changed and how it was verified. The next step is to put accepted ticket content
directly into commit-message bodies and remove the completed files—keeping active
work in the tree and completed work in Git history. **That automatic archiving is
planned; the current draft still keeps completed tickets in `done/`.**

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
work start T-1234abcd
# Implement and verify the change, then hand it off:
work review T-1234abcd
work list --status review
```

Tickets move through status folders inside their parent: for example,
`epic/review/task.md`, then `epic/done/task.md` after acceptance. The feature
stays together when its epic moves. Agent skills guide preparation, execution,
review, and ticket-linked Git work.

For commands and options, use `work --help` or `work COMMAND --help` (or the
project's `./.workkit/work`). For rules, choose a focused reference from the
[convention index](CONVENTION.md)—there is no need to read every document.

## Short prompts in OpenCode

```text
/work-epic Add search by title
/work-task E-a1b2c3d4 Test empty search results
/work-list review
```

Project commands use the same skills and CLI. See the
[OpenCode shortcuts](docs/OPENCODE.md) for the full list.

## Develop

```sh
python3 -m unittest discover -s tests -v
./work check
```

This checkout already has a `.work/` board. See [contributing](CONTRIBUTING.md),
[publishing](docs/PUBLISHING.md), and the [changelog](CHANGELOG.md).

Draft v0.2.0. Project name is provisional. [MIT licensed](LICENSE).
