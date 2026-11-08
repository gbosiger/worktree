---
{
  "id": "T-f7d4aef3",
  "kind": "task",
  "title": "Define a timestamped ticket state history format",
  "status": "backlog",
  "parent": "E-f44b10c1",
  "depends_on": [],
  "implementer": null,
  "reviewer": null,
  "branch": null,
  "base_branch": null
}
---
# Define a timestamped ticket state history format

## Purpose and scope

Define a readable state-change section for stories and epics that can later be
parsed for timeline playback. Deliver a maintained format/lifecycle proposal,
not transition-writing code or a visualization.

## Acceptance criteria

- [ ] Specify the section heading, versioning/parsing rules, and concrete examples for normal progression, return from review, and reopen/reaccept cycles.
- [ ] Each event identifies previous/next state and a timezone-aware timestamp associated with the immutable ticket ID; define stable ordering when timestamps tie or clocks move backward.
- [ ] Decide creation/initial-state events and whether tasks/groups use the same log. Explicitly distinguish a missing historical record from a known initial state.
- [ ] Define events for acceptance into implemented, commit into done, automatic ancestor reopening, archived restoration, and container moves that leave descendant states unchanged.
- [ ] Define preservation through archive/merge/reopen and how this coexists with existing timestamped acceptance records without weakening their validation.
- [ ] Explain manual Markdown status edits, malformed history, older tickets, older toolkit copies, and any incompatible draft-format changes. Never fabricate timestamps for unobserved past transitions.
- [ ] Document failure semantics for multi-ticket operations and commit rollback: persisted events must describe actual persisted state changes, not failed attempts.
- [ ] Record decisions and remaining tradeoffs in maintained docs and provide an implementation/test checklist for S-56c90e4f.

## Approach and decisions

Read `docs/FORMAT.md`, `docs/LIFECYCLE.md`, transition/reopen/persist, and
commit/merge code in `.work/tools/work.py`. Keep history in a separate Markdown
section, not a duplicate acceptance gate. UTC is the proposed timestamp basis;
precision, event syntax, and ordering remain design decisions. No external
service, database, Git-history rewrite, or mandatory dependency is in scope.

## Verification

Walk the example event streams through every lifecycle operation and an archived
reopen. Explain which future playback questions can be answered and which remain
unknown for preexisting/manual changes. Supply examples for review, not invented
execution evidence.

## Handoff

Backlog design task; format decisions are not yet approved. Execute under the
normal branch/worktree and review gates. S-56c90e4f depends on this deliverable.
