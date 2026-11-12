---
{
  "id": "E-28d90d19",
  "kind": "epic",
  "title": "Make tickets easier to read and resume",
  "status": "done",
  "parent": null,
  "depends_on": [],
  "implementer": "agent",
  "reviewer": "agent",
  "branch": "codex/E-28d90d19-readable-tickets",
  "base_branch": "master"
}
---
# Make tickets easier to read and resume

A maintainer should be able to skim a ticket, decide what success looks like, and resume the work in a fresh session.

## Scope and delivery

Apply the preparation guidance to the four creation templates, slash commands, and authoring skill, then try it on the three existing backlog epics and their children. Keep detailed product rules in maintained requirements. The final demonstration is a fresh install generating each ticket kind and a reviewer reading a real epic, story, and task without needing the previous session.

## Acceptance criteria

- [x] Each ticket template and authoring entry point asks for a clear outcome and observable checks.
- [x] Every existing backlog item describes its problem, scope, and verifiable result and points to any detailed product requirements.
- [x] An interrupted implementer or reviewer can resume from the ticket and repository alone.

## Handoff

In the project checkout on `codex/E-28d90d19-readable-tickets` (base `master`), compare the four templates and `docs/AUTHORING.md` with the rewritten backlog. All 26 backlog links resolve. A fresh installation generated all four ticket kinds and passed its board check. All three canonical skills passed validation. The full suite (`python3 -m unittest discover -s tests -v`) passed 198 tests. `./work --root . check` validated 27 tickets.

The first draft left too little context for the assignee. The revised guide draws on GOV.UK’s user-story guidance, Atlassian’s epic guidance, and Bill Wake’s INVEST and SMART distinctions. Source links and worked examples are in `docs/AUTHORING.md`.

Review follow-up: T-f7d4aef3 and T-8818c75d now require recorded decisions. E-f44b10c1 has one check for each lifecycle shortcut, and E-1c6791d9 points to the current first task. The authoring guide covers these cases. T-d87dad08 (Document concurrent epic work with Git worktrees) was added under E-f44b10c1; its scope is recorded in that epic and its `Requirements:` links target `docs/GIT.md`. The terminal epic scope now also covers branch setup on start (S-c382b0f8) and the concurrent-worktree guide (T-d87dad08); both are reflected in its acceptance criteria and `docs/requirements/terminal.md`.

Repeat preparation trial: three fresh agents prepared the Neovim epic from the same brief. The pre-edit and refined versions produced 61 and 44 checkboxes respectively. Both required a recorded board-interface decision. The refined version also named blocked consumers on deferral, but its lifecycle story still grew from eight checks to nine. Review checklist quality by the decisions a person can accept separately. The full suite passed again (198 tests), and all three disposable boards validated.

Human reviewer: open E-f44b10c1 to judge the delivery scope, S-c382b0f8 to try the grouped-branch example, and T-8818c75d to identify the archive decision and evidence needed. Check whether each assignment makes sense on its own. Review stays in `work-execute` because ticket lookup, roles, preflight, and evidence are shared with implementation.

The GitHub archive decision belongs to T-8818c75d. The local file-history reader and the older proposal for squash messages need reconciliation before that feature starts.

## Acceptance record

2026-11-12T18:52:34+00:00 — agent: Independent subagent review found no rule loss and APPROVE after fixes. Full suite passed 198 tests, board check validated 27 tickets, all local links resolve, task headings aligned with template.
