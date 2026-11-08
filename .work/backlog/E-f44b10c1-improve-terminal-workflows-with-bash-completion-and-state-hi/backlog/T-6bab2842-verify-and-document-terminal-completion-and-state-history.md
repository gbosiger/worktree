---
{
  "id": "T-6bab2842",
  "kind": "task",
  "title": "Verify and document terminal completion and state history",
  "status": "backlog",
  "parent": "E-f44b10c1",
  "depends_on": ["S-5299cba3", "S-56c90e4f", "T-10e609cd", "S-8ce9abfb"],
  "implementer": null,
  "reviewer": null,
  "branch": null,
  "base_branch": null
}
---
# Verify and document terminal completion and state history

## Purpose and scope

Prepare end-to-end evidence and user guidance for Bash completion and the state
history log, without asking reviewers to interpret raw logs or build an animation.

## Acceptance criteria

- [ ] A repeatable Bash smoke test demonstrates enabling/disabling completion, command-specific IDs from nested directories, explicit-root selection, and refreshed suggestions after a transition.
- [ ] A story/epic walkthrough shows timestamped state changes, return from review, acceptance/commit, and archived reopening, preserving prior history and acceptance evidence.
- [ ] Tests demonstrate that completion, rejected commands, and dry runs leave history and board contents unchanged.
- [ ] Documentation explains supported Bash versions, checkout/install setup, command filtering limitations, the history format, and what older/manual changes cannot reveal.
- [ ] Record results for `python3 -m unittest discover -s tests -v` and `./work --root . check`, plus focused Bash/history tests and any known limitations.
- [ ] A short linked evidence summary gives the reviewer reproducible examples and identifies remaining decisions; no human approval or unperformed tests are claimed.
- [ ] S-8ce9abfb's WIP acceptance walkthrough demonstrates default refusal, explicit warning/confirmation, unchanged retained gates, opt-in completion filtering, and a truthful direct-transition history entry.

## Approach and decisions

Prerequisites: S-5299cba3 — Complete work commands with relevant board ticket IDs;
S-56c90e4f — Record ticket state changes for later timeline playback. Use disposable
fixture repositories, not destructive lifecycle experiments on the dogfood board.

Also consume T-10e609cd — Assess and selectively split Python code for
agent-efficient maintenance. Include its split/no-split rationale and, if code
moved, installation/import regression evidence in the final summary.

## Verification

Collect automated results, tested Bash versions, setup commands, sample event
sections, and observed limitations. Separate technical evidence from the
reviewer's decision about whether the interactions are understandable and useful.

## Handoff

Backlog verification task. After preparing the evidence, hand off for explicit
review under the agreed roles; do not infer acceptance from test success.
