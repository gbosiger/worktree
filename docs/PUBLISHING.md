# Local setup and publishing

This project can be opened directly in Codex as a local repository. No special
Codex project manifest or ChatGPT Project registration is required. AGENTS.md
provides development guidance and .agents/skills contains project skills.

## Put the prepared source on your computer

Extract the provided worktree-tickets.zip into ~/Projects, producing
~/Projects/worktree-tickets. If that directory already exists, extract elsewhere
and compare; do not overwrite it blindly.

```sh
mkdir -p ~/Projects
unzip ~/Downloads/worktree-tickets.zip -d ~/Projects
cd ~/Projects/worktree-tickets
python3 -m unittest discover -s tests -v
./work check
```

The ZIP excludes Git internals. Initialize a new local repository using your own
Git identity, then open this folder in Codex:

```sh
git init -b main
git add .
git commit -m "chore: bootstrap Worktree Tickets"
```

## Publish publicly on your GitHub

With GitHub CLI installed and signed in to the intended account:

```sh
gh auth status
gh repo create worktree-tickets --public --source=. --remote=origin --push
```

This command creates a PUBLIC repository and publishes the current committed
source. Review files and account before running it. If the name is already taken
in your account, select a different name. Alternatively create an empty public
repository in GitHub's web UI, use its exact URL as origin, and push main.

## Install into another project

```sh
~/Projects/worktree-tickets/work install ~/Projects/my-module
cd ~/Projects/my-module
git diff -- AGENTS.md
git status --short
```

Review then commit .workkit/, .work/, .agents/skills/, .opencode/commands/, and
the AGENTS.md addition.
The first release uses explicit reviewed updates, not a network bootstrap script
or automatic downloads. Keep each project's own tickets in its own repository.
