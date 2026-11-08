---
{
  "id": "S-8ce9abfb",
  "kind": "story",
  "title": "Allow explicitly confirmed acceptance directly from WIP",
  "status": "backlog",
  "parent": "E-f44b10c1",
  "depends_on": [],
  "implementer": null,
  "reviewer": null,
  "branch": null,
  "base_branch": null
}
---
# Allow explicitly confirmed acceptance directly from WIP

## Required behavior and value

Allow an explicitly requested, confirmed `wip -> implemented` acceptance path.
For example, a task whose purpose is to perform a review may already contain
the completed review and a fully checked checklist while still in `wip/`.
The user should be able to accept it without a separate move through `review/`,
but never by default or merely because all boxes are checked. Here “review task”
describes the ticket's purpose, not its current lifecycle status.

## Acceptance criteria

- [ ] An explicit opt-in lets an otherwise eligible WIP ticket be accepted into implemented, not done, without first moving it to review.
- [ ] Without opt-in, accepting WIP remains rejected with guidance toward the normal review flow or the explicit shortcut; checking boxes alone never triggers a transition.
- [ ] Before mutation, show a warning naming the ticket and the skipped review-state handoff, and require affirmative confirmation. Decline, empty input, EOF, or cancellation leaves the ticket unchanged.
- [ ] Retain checked-checklist, recorded-reviewer, matching `--by`, nonempty evidence, dependency, and completed-child gates. Confirmation waives only the requirement to be in review status.
- [ ] Record ordinary timestamped acceptance evidence. If state-history logging is available, record the actual WIP-to-implemented transition without inventing a visit to review.
- [ ] Noninteractive use cannot silently confirm or hang waiting for input. Decide and document whether it is refused or requires a separately explicit acknowledgement; no general default-yes behavior.
- [ ] Dry runs describe the exception and remaining confirmation requirement without changing status, acceptance records, or history.
- [ ] Bash completion keeps WIP IDs out of ordinary `done` suggestions; include them only in the chosen explicit opt-in context, with normal command-time validation unchanged.
- [ ] Regression tests cover confirmed success, default refusal, decline/cancel/EOF, noninteractive behavior, dry runs, every retained acceptance gate, and unchanged normal review acceptance.
- [ ] Lifecycle/help documentation explains the exception and warns that agent workflows still require explicit authorization to review/accept; opt-in is not permission to invent reviewer approval.

## Approach and decisions

Choose the opt-in spelling and confirmation interface before implementation;
no particular flag is specified yet. Inspect `transition()` and argument parsing
in `.work/tools/work.py`, `docs/LIFECYCLE.md`, and acceptance/archive validation.
Keep this a narrow status-gate exception rather than a force command bypassing
validation. Confirm which ticket kinds may use it; the motivating case is a
review-purpose task, but there is no existing dedicated review ticket kind.

Coordinate the candidate matrix with S-5299cba3 and history semantics with
T-f7d4aef3/S-56c90e4f. No hard dependency on history recording is required; the
combined epic must cover the exception once logging is present. Resolve lock
handling and revalidation around user input so confirmation does not authorize
acceptance of a ticket that changed meanwhile.

## Verification

Use disposable boards and scripted terminal/nonterminal input. Verify rejected
or cancelled attempts leave all files unchanged, and accepted records still pass
board/archive validation. Run the unit suite and board check; collect a short
manual warning/confirmation transcript without claiming reviewer approval.

## Handoff

Backlog specification only. Resolve interface, ticket-kind scope, and
noninteractive policy under the epic's branch/base and role preflight before
implementation. Normal agent review/acceptance authorization rules remain intact.
