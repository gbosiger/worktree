---
{
  "id": "T-6824d1dc",
  "kind": "task",
  "title": "Judge the non-blocking findings from the preflight CLI review",
  "status": "done",
  "parent": "E-1a88a55f",
  "depends_on": [],
  "implementer": "agent",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Judge the non-blocking findings from the preflight CLI review

## Purpose and scope

Independently judge the three non-blocking observations recorded in the agent
review of T-cd66778b (preflight CLI). For each, record a written decision:
close with rationale (no change), or open a scoped follow-up ticket with the
maintainer. Do not treat them as accepted defects, and do not reopen or
re-review T-cd66778b, which is already accepted.

## Acceptance criteria

- [x] Judge the lock-free design and its concurrency limits. Record "close"
      with the reasoning, or a concrete change proposal. Decision: close with
      the existing point-in-time contract, not the original checklist's
      "never a false pass" premise; evidence and limitations are below.
- [x] Judge ancestor dependency gating: decide whether `preflight` (execute
      mode) should block a child when an *ancestor* has an unfinished
      dependency, or only the selected ticket. Record "keep" (fails-safe) or a
      scoped relaxation ticket. Decision: keep the fail-safe ancestor gate;
      evidence and rationale are below.
- [x] Judge commit-time bookkeeping: confirm the next `work commit` for
      T-cd66778b must exclude the unrelated convention-review bookkeeping
      (T-5079b576 moved to WIP; new T-7ff2dcbf and T-fbcc26e0). Record any
      staging guidance that the commit skill should carry. Decision: exclude
      unrelated bookkeeping and honor the existing board guard; do not stage
      everything merely to make the command pass. No commit is authorized here.

## Approach and decisions

Source: the `## Review findings` section of T-cd66778b. Read that section,
`docs/GIT.md`, and the `preflight`/`execution_target` code before judging. Each
item above maps one-for-one to the three observations quoted there. A "close"
decision needs one sentence of rationale; a "change" decision names the fix and
opens a separate ticket rather than editing this one.

## Decisions and evidence (2026-11-08)

### Lock-free observation: keep; reject the stronger concurrency premise

`preflight` intentionally bypasses `locked(root)`, samples the branch, reads
worktree/status information, checks lock/journal presence, and then validates
the board. Those observations are not an atomic snapshot. A concurrent writer
can finish between checks or change Git state after its branch was sampled;
therefore exit 0 does not guarantee the checkout is still suitable when the
command returns. The original acceptance-item premise claiming otherwise was
incorrect and has been corrected above, not accepted as evidence.

Reproduction: in a disposable repository, use the existing PreflightTests setup
to create main/feature and a task targeting feature. Wrap `_git` so that after
its status query completes, a separate `git switch main` runs. `preflight`
returns successfully using its sampled feature branch even though the actual
branch is main before it returns. The wrapper injects the external change;
preflight itself still performs no writes. This disproves the unconditional
"never falsely passes" claim without modifying the real checkout.

No runtime change is proposed: docs/GIT.md already calls it a point-in-time
check, explicitly disclaims protection against concurrent Git/editor writes,
and requires rerunning after context changes. A toolkit lock would only
coordinate cooperating toolkit commands, not arbitrary Git/editor actions.
Close this observation under that bounded contract; do not promise atomic or
race-free execution, and do not work concurrently in the selected checkout.

### Ancestor dependencies: keep the fail-safe execution policy

`check` validates structure and completion consistency; it deliberately allows
unfinished dependencies on WIP tickets. Execution preflight has a different
purpose: its chain includes the selected ticket and all ancestors, and it
checks unfinished dependencies on each. This prevents implementing work inside
an ancestor whose declared prerequisites are still incomplete, consistent with
work-execute's rule to stop on an ancestor gate rather than silently bypass it.

Reproduction: create a WIP epic depending on a separate backlog epic, then
select a child task with no dependencies. The board validates, but preflight
reports the WIP epic's unfinished dependency and exits with a blocker. This is
intentional execution policy, not a defect in low-level lifecycle behavior.
No relaxation ticket is needed; any exceptional workflow needs explicit
authorization rather than silently weakening the default.

### Commit scope: retain selective staging and report the board blocker

The current commit skill already requires selective staging, staged-diff
inspection, explicit ticket selection, and refusing to stage the whole board
to bypass its unstaged-board guard. No duplicated guidance or new skill rule
is needed. Ticket selection limits the ticket queue, not the already-staged
implementation files: `work commit` commits all staged content.

Important qualification: leaving unrelated board changes unstaged preserves
them, but currently also blocks `work commit`, because `commit_prepare` refuses
any untracked/unstaged board files. Merely selecting T-cd66778b cannot bypass
that guard. `./work commit T-cd66778b --dry-run` was attempted on the actual
checkout and failed with "Unstaged board files detected" naming unrelated
release-backlog files. No staging, commit, recovery, or reset was performed.

Before a future commit, obtain a concrete authorized plan to save the unrelated
bookkeeping separately or isolate the intended changes in a clean context.
Do not invent ownership, discard user work, or stage mixed changes to force
success. This is a setup/authorization decision, not a preflight defect; the
accepted T-cd66778b stays implemented until an authorized commit is possible.

## Verification

Record each decision inline (check the box and append the decision text) with
evidence. Run `./work --root . check` and `git diff --check` after any edits.

Two disposable-repository experiments above passed their assertions: concurrent
branch-switch false-pass reproduction and ancestor-dependency blocking.
The real commit dry run failed as expected on the unstaged-board guard.
Only judgment/evidence Markdown and this task's lifecycle were changed; no
runtime code or tests were changed and the full regression suite was not rerun
for this documentation-only judgment. `./work --root . check` passed (45 live
tickets); `git diff --check` passed.

## Handoff

Prepared 2026-11-08; judgment implemented by agent, with human reviewer for
the recorded decisions. All observations have a written disposition; no new
implementation defect or follow-up ticket is proposed. T-cd66778b already has
the independent agent's acceptance record and remains implemented, not reopened
or re-reviewed here. The remaining feature tasks T-7ff2dcbf and T-fbcc26e0 stay
backlog; this judgment does not accept them or the parent epic.

Context: /home/gbo/Projects/worktree-tickets on
feature/E-1a88a55f-initial-toolkit, base master; parent E-1a88a55f stays WIP.
Existing review notes and unrelated backlog work are preserved. Next action:
review these judgments separately; no acceptance, staging, commit, or push has
been performed by this task.

## Acceptance record

2026-11-08T12:29:14+00:00 — human: Maintainer requested 'close what can be close and take a new ticket' after receiving the three recorded judgments: keep snapshot-only preflight, keep ancestor gates, and retain selective staging without bypassing the board guard. No code changes or new defects were proposed; board and whitespace checks passed.
