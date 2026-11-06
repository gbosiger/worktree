# OpenCode shortcuts

Project-local slash commands turn short requests into ticket actions. They use
the existing skills and CLI, not a separate board or a second set of rules.

```text
/work-epic Add search by title
/work-task E-a1b2c3d4 Cover empty search results; implementer agent, reviewer human
/work-story E-a1b2c3d4 Search titles without case sensitivity
/work-list review
/work-show T-1234abcd
/work-start T-1234abcd
/work-review T-1234abcd
```

Use real IDs from your board. A missing parent, ambiguous target, or unspecified
essential role results in a question, not an invented value. Creation writes a
backlog ticket; it does not also start implementation.

## Available commands

| Command | Purpose |
| --- | --- |
| `/work REQUEST` | General ticket request, including explicit implementation requests |
| `/work-group DESCRIPTION` | Create a group for a larger outcome |
| `/work-epic DESCRIPTION` | Create a feature epic |
| `/work-story EPIC_ID DESCRIPTION` | Create a behavioral story |
| `/work-task EPIC_ID DESCRIPTION` | Create a supporting task |
| `/work-list [STATUS]` | List tickets, optionally filtered |
| `/work-show ID` | Locate and summarize a ticket |
| `/work-check` | Validate without automatically repairing |
| `/work-start ID` | Start selected work, without implementing it |
| `/work-review ID` | Review actual work and prepare its handoff |
| `/work-done ID ACCEPTANCE_AND_EVIDENCE` | Record explicit reviewer acceptance |
| `/work-reopen ID` | Reopen while honoring dependencies/ancestors |
| `/work-assign ID IMPLEMENTER REVIEWER` | Set agreed roles |
| `/work-depend ID PREREQUISITE_ID` | Add a dependency; request removal explicitly |

These are natural-language prompt shortcuts, not a second strict argument parser.
You can append role choices, constraints, or `dry run`. Lifecycle gates still
apply: shortcuts never auto-check acceptance criteria or impersonate a human
reviewer. `/work-review` does not itself grant human acceptance. Git commits,
branch switches, and publication require separate explicit authorization.
The planned archive CLI is still unavailable.

## Installation and source of truth

`work install PROJECT` includes these commands. In installed projects,
`.opencode/commands/work-*.md` and `work.md` are relative links to canonical
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
