# OpenCode shortcuts

Project-local slash commands prepare ticket files with descriptions, scope, and
acceptance criteria. They use the existing skills and CLI, not a separate board
or a second set of rules. Board queries and lifecycle actions belong in the
terminal, not LLM prompt wrappers.

```text
/work-epic Add search by title
/work-task E-a1b2c3d4 Cover empty search results; implementer agent, reviewer human
/work-story E-a1b2c3d4 Search titles without case sensitivity
```

Use real IDs from your board. A missing parent, ambiguous target, or unspecified
essential role results in a question, not an invented value. Creation writes a
backlog ticket; it does not also start implementation.

## Available commands

| Command | Purpose |
| --- | --- |
| `/work-group DESCRIPTION` | Create a group for a larger outcome |
| `/work-epic DESCRIPTION` | Create a feature epic |
| `/work-story EPIC_ID DESCRIPTION` | Create a behavioral story |
| `/work-task EPIC_ID DESCRIPTION` | Create a supporting task |

These are natural-language prompt shortcuts, not a second strict argument parser.
You can append role choices, constraints, or `dry run`. Lifecycle gates still
apply: shortcuts never auto-check acceptance criteria or impersonate a human
reviewer. Git commits, branch switches, and publication require separate explicit
authorization.
Archive and integration remain terminal-only CLI verbs — `work commit` and
`work merge` — with no slash shortcut; see [Git workflow](GIT.md).

## Terminal workflows

Run these directly in the toolkit checkout; in installed projects replace
`./work` with `./.workkit/work`, or use `work` after PATH setup.

| Workflow | Terminal command |
| --- | --- |
| Find implementation candidates | `./work list --ready` (current branch's epic) |
| Find review work | `./work list --status review` (current branch's epic) |
| Resume work | `./work list --status wip` |
| Inspect another epic's backlog | `./work list --epic EPIC_ID` |
| List the whole live board | `./work list --all` (optionally `--status review`) |
| Show a ticket | `./work show ID` |
| Validate the board | `./work check` |
| Start selected work | `./work start ID` |
| Hand off into review | `./work review ID` |
| Record reviewer acceptance | `./work done ID --by REVIEWER --evidence "Verification evidence"` |
| Reopen work | `./work reopen ID` |
| Assign roles | `./work assign ID --implementer agent --reviewer human` |
| Add a dependency | `./work depend ID PREREQUISITE_ID` |
| Remove a dependency | `./work depend ID PREREQUISITE_ID --remove` |

These commands change status or metadata, not implementation or review quality.
Ask the agent in ordinary chat to implement or review a ticket using
`work-execute`; a status transition alone does not perform that work. The
general dispatcher and lifecycle/query slash commands are no longer supplied,
including the review shortcut. Existing lifecycle and acceptance gates still
apply; see [Lifecycle](LIFECYCLE.md).

## Installation and source of truth

`work install PROJECT` includes these commands. In installed projects,
the four `.opencode/commands/work-*.md` files are relative links to canonical
templates under `.workkit/commands/`. In this toolkit checkout they link to
`commands/`. Commit both the canonical templates and links. Moving/cloning the
repository keeps them valid without a global configuration change.

Installation refuses conflicting command files or links before copying the
toolkit and preserves unrelated commands/configuration. Older installations
need reviewed toolkit updates; they are not silently overwritten.

OpenCode V2 discovers `.opencode/commands/*.md` and reloads saved commands
automatically; use `/reload` if a manual refresh is needed. Templates use
`$ARGUMENTS`, do not interpolate requests into shell blocks, and do not force a
model, agent, or background session. See the
[OpenCode commands reference](https://opencode.ai/v2/docs/commands) for syntax.
