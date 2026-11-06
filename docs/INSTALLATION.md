# Installation

## Make the command available

Python 3.10+ is required at runtime; no third-party Python packages are needed.
From a toolkit checkout:

```sh
./work setup
work --help
```

`setup` links `~/.local/bin/work` to this checkout's executable launcher. It
refuses to overwrite another command, and can safely be repeated for the same
checkout. Keep the checkout in place. If the directory is not on PATH, setup
prints a reminder; it does not edit shell configuration. Add the directory to
your shell's PATH, or run the printed full command path.

Use `./work setup --bin-dir /your/bin` to choose another command directory.
No files outside the chosen directory are changed. To uninstall the command,
remove only the symlink that setup created. `./work` always works directly from
the toolkit checkout without setup.

The launcher loads `.work/tools/work.py` relative to its own resolved location,
not the current directory. Keep that runtime with the checkout; there is no
root-level `work.py`. Templates and references remain at the toolkit root.

## Adopt in another project

```sh
work install ~/Projects/my-project
cd ~/Projects/my-project
./.workkit/work create epic "Search"
./.workkit/work --help
```

The installer copies runtime, launcher, convention index, focused references,
templates, skill sources, license, and version into `.workkit/`. It links three
repository skills under `.agents/skills/` to `.workkit/skills/`, creates `.work/`
if absent, and appends a short section to `AGENTS.md` without replacing content.
It refuses an existing `.workkit` or conflicting skills.

The copied runtime uses the same relative layout:
`.workkit/work` loads `.workkit/.work/tools/work.py`. Only the runtime is copied
from the toolkit's `.work/`, never its tickets. The host project's `.work/`
remains the ticket board; tooling outside status folders is not scanned as tickets.

There is one authoritative skill copy per project: `.workkit/skills/`. The
discovery entries in `.agents/skills/` are relative directory symlinks, so edits
are visible immediately and a normal Git clone or directory move keeps them
valid. They never point to a developer's home directory or global installation.
In the toolkit's own source repository, the links point to `skills/` instead.
Git clients must preserve symlinks (the supported Unix-like environment does).

OpenCode shortcuts are installed the same way: canonical templates live in
`.workkit/commands/` with relative file links under `.opencode/commands/`.
Existing conflicting command files or links are refused before toolkit writes;
unrelated commands and OpenCode configuration are preserved. See
[OpenCode shortcuts](OPENCODE.md) for usage. These remain optional: the CLI and
Markdown workflow do not require OpenCode.

Commit these files in the host project. Contributors need only a regular clone
and Python. `./.workkit/work` uses that project's copied version. The global
`work` command uses the toolkit checkout to which setup linked it; it does not
automatically choose a project's pinned runtime. Tickets always belong to the
project's own `.work/`, not the shared toolkit repository.

## Updates

Updates are explicit reviewed changes: compare upstream with the installed
runtime and local customizations, then replace selected toolkit/skill files in
a normal project commit. VERSION identifies the copied release. Never replace
the project's `.work/` or overwrite its `AGENTS.md`. Consult
[migrations](MIGRATIONS.md) only when upgrading an older layout.

For older installations with duplicate skill directories, follow the
[skill-link migration](MIGRATIONS.md#duplicate-skill-copies-to-canonical-links).
The installer refuses conflicts rather than deleting custom skills.

Copying is the default so ordinary clones contain everything. Git subtree or
submodules are optional, not necessary. Multi-file installation is not
transactional; interruptions can require manual repair.
