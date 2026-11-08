---
{
  "id": "T-d190ce5e",
  "kind": "task",
  "title": "Verify documentation is current after archive rework",
  "status": "done",
  "parent": "E-1a88a55f",
  "depends_on": [],
  "implementer": "agent",
  "reviewer": "agent",
  "branch": null,
  "base_branch": null
}
---
# Verify documentation is current after archive rework

## Purpose and scope

After T-2e1b1dd2 replaced marker-required archives with Git-native file history,
check that every lasting document, command template, and skill describes the
current behavior rather than stale or contradictory guidance. Fix confirmed
inaccuracies. Do not change archive behavior or policy here.

## Acceptance criteria

- [x] The stale unimplemented-CLI claim is absent: `commands/work.md` remains removed by T-1f838137, and maintained CLI guidance documents the existing `work commit` command.
- [x] README.md, docs/FORMAT.md, docs/GIT.md, docs/LIFECYCLE.md, CHANGELOG.md, and the archive sections of skills reference the current markerless file-history model with no leftover "marker required" or "v2" wording that contradicts it.
- [x] Each focused reference (CONVENTION.md index) still points to maintained documents; no broken links or duplicated, divergent instructions.
- [x] Verification records concrete before/after fixes with the files changed and the stale wording removed.

## Approach and decisions

The confirmed finding from T-2e1b1dd2 review: `commands/work.md` line 16 says
"The proposed commit/archive CLI is not implemented; do not pretend it exists."
That is inaccurate now. Update it to match the implemented command, keeping the
"do not pretend unsupported behavior exists" intent. Sweep the other durable
docs for the same class of drift, but do not rework archive semantics.

Scope reconciliation (2026-11-07): completed T-1f838137 removed the general
dispatcher and lifecycle/query prompts. Its removal supersedes editing
commands/work.md; do not restore it. The first criterion now checks absence of
the stale claim and accuracy of maintained CLI guidance instead. Agent implements;
a separately requested agent review follows, as specified below.

## Verification

Implementation verification (2026-11-07):

- `python3 -m unittest discover -s tests -v`: 155 tests pass (91.108 s).
- `./work --root . check`: OK, 27 tickets.
- `git diff --check`: clean.
- Standard-library Markdown-link scan of README, convention index, changelog,
  contributing guide, docs, canonical skills, commands, and templates: all 21
  local links across 23 maintained files resolve; local heading anchors resolve.
  The same scan confirms no removed slash shortcuts or stale unimplemented-CLI
  claim, and commands/work.md remains absent. External links were not fetched.
- Read the focused references and canonical skills/templates for consistency.
  docs/GIT.md already describes markerless lookup, retained commits, and separate
  integration/cleanup accurately; no edit required. Legacy v1/v2 descriptions
  remain explicitly labeled compatibility/history, not current writer rules.

Concrete fixes (lasting files):

- README.md: replaced review -> done "after acceptance" with review -> implemented
  after acceptance, then done after explicit ticket commit.
- docs/FORMAT.md: replaced "archive commit/removal command is work commit" with
  retained commits and post-integration work merge cleanup. Qualified the v1
  message/envelope requirements as legacy and documented materialization as the
  alternative to preserving that envelope through squash/rebase.
- docs/LIFECYCLE.md: added implemented to the already-established ancestor stop
  gate, matching work-execute; replaced "moving implemented work into review"
  with handing WIP work into review to avoid confusing the status with prose.
- CHANGELOG.md: removed current snapshot-first writer claims and the obsolete
  list of browsing/lifecycle slash wrappers. Described retained ticket commits,
  four creation prompts, and terminal CLI actions; labeled recovery v2 legacy.
  Earlier backend/snapshot/signing history remains identified as historical.
- skills/work-commit/SKILL.md: qualified "a commit does not ... mean ... done"
  as plain Git behavior and distinguished work commit's accepted-to-done move.
  Edited only the canonical source, not its discovery link.
- docs/PUBLISHING.md: added installed .opencode/commands links to the reviewed
  project assets to commit, matching the existing installation guidance.

No CLI, tests, ticket format, archive behavior, or lifecycle policy was changed.
Historical acceptance/progress records were not rewritten.

## Handoff

Agent implements and a separately requested agent review follows. Documentation
edits only; no behavior, commit, publication, or acceptance of the parent epic.

Implementation ready for review (2026-11-07). Context:
/home/gbo/Projects/worktree-tickets on feature/E-1a88a55f-initial-toolkit,
matching E-1a88a55f's recorded branch/base (master). Checkout began clean at
21b4b5d. This ticket moves to review; the parent epic stays WIP and all sibling
statuses remain unchanged. No Git mutation or acceptance was performed.

Next action: separately request agent review of the actual documentation diff
and the evidence above. Do not accept the parent or begin later feature epics.

## Acceptance record

2026-11-07T13:48:31+00:00 — agent: Reviewed doc diff in CHANGELOG.md, README.md, docs/FORMAT.md, docs/LIFECYCLE.md, docs/PUBLISHING.md, skills/work-commit/SKILL.md. commands/work.md absent; stale 'not implemented' claim gone from all maintained docs. No contradictory marker-required/v2 wording (legacy-only). 21 local links resolve; 155 tests OK; ./work --root . check OK (27 tickets).
