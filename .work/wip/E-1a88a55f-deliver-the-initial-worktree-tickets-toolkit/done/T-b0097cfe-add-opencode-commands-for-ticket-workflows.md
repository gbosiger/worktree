---
{
  "id": "T-b0097cfe",
  "kind": "task",
  "title": "Add OpenCode commands for ticket workflows",
  "status": "done",
  "parent": "E-1a88a55f",
  "depends_on": [],
  "implementer": "agent",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Add OpenCode commands for ticket workflows

## Purpose and scope

Provide short OpenCode prompts for the toolkit's supported ticket operations,
especially creating epics/stories/tasks, using existing skills and lifecycle
gates rather than duplicating their rules or requiring long user instructions.

## Acceptance criteria

- [x] Project-local shortcuts cover creation, listing/showing/checking, lifecycle, roles, dependencies, and a general work request.
- [x] Templates use existing skills and the supported CLI; ambiguous essentials prompt clarification rather than invented IDs/approval.
- [x] Canonical command files are linked into discovery here and into installed projects without duplicated prompts or global config changes.
- [x] Installer preserves unrelated commands/configuration and rejects regular-file or dangling-link command conflicts before toolkit writes.
- [x] README and focused OpenCode guidance show short examples, constraints, and actual command names; regression tests and board check pass.

## Approach and decisions

Follow https://opencode.ai/v2/docs/commands: Markdown command templates in
.opencode/commands/, description frontmatter, and $ARGUMENTS for natural-language
requests. Keep canonical templates in commands/ and installed .workkit/commands/;
use relative discovery links. Do not force a model/agent, spawn a background
session, interpolate requests into shell blocks, or implement future archive
commands. Ticket creation stays in backlog and does not imply implementation.

## Verification

- `python3 -m unittest discover -s tests -v`: all 27 tests pass.
- `./work --root . check`: all 10 tickets validate.
- All 14 command discovery paths resolve to canonical files. Tests cover metadata,
  argument placeholders, absence of shell interpolation, skill delegation,
  installed links/edit propagation/relocation, reinstallation from a copied
  runtime, custom configuration preservation, and preflight command conflicts.
- Prompt templates and installer behavior are tested; agent-generated ticket
  quality still requires human review in actual command use.

## Handoff

Human-reviewed and retained in this epic's done/ folder. See docs/OPENCODE.md
for commands. Ticket acceptance does not imply a Git commit, merge, global
configuration mutation, or publication.

## Acceptance record

2026-11-06 — human: The maintainer confirmed in conversation that the tickets
had been reviewed and completed, then requested reconciliation of this ticket.
Its existing acceptance criteria are checked and verification is recorded above.
This entry records that confirmation; no new test run or Git operation is claimed.
