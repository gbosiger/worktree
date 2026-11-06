# Worktree Tickets development

Read docs/FORMAT.md before format changes and docs/LIFECYCLE.md before lifecycle
changes. Use docs/AUTHORING.md for ticket preparation and docs/GIT.md for Git
work. CONVENTION.md is a reference index; do not preload all references or history.
This project is a small Python 3.10+ standard-library toolkit. Keep Markdown
editable without our CLI and avoid introducing mandatory external services.

Run `python3 -m unittest discover -s tests -v` before completing code changes.
Use `./work --root . check` to validate the dogfood board.
Canonical skill sources live in `skills/`; `.agents/skills/` contains relative
directory symlinks to them. Edit canonical sources only, not duplicate copies.
Installed projects link `.agents/skills/` to their local `.workkit/skills/`.
These are repository assets, not personal/global skill installations.
Canonical OpenCode prompt commands live in `commands/`; `.opencode/commands/`
links to them. Installed projects link to `.workkit/commands/`. Do not duplicate
templates or add shell interpolation of user-supplied command arguments.

Use ticket IDs in commits once a ticket exists. Preserve unrelated work, avoid
implicit Git mutations in CLI commands, and do not publish without authorization.
The current format is a draft; document incompatible changes explicitly.
