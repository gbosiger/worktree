---
{
  "id": "T-266c67e6",
  "kind": "task",
  "title": "Recheck epic readiness and merge gates",
  "status": "backlog",
  "parent": "E-54e9139e",
  "depends_on": ["T-dc9a8fcd"],
  "implementer": "agent",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Recheck epic readiness and merge gates

## Purpose and scope

Provide explicit idempotent draft-to-ready promotion and reusable gates for the
current PR head. Readiness is neither ticket acceptance nor merge authorization.

## Acceptance criteria

- [ ] Epic readiness checks that epic's backlog plus all unfinished children, dependencies, and explicit acceptance; unrelated repository backlog does not block it.
- [ ] Accepted done task batches remain eligible while other epic work is unfinished; existing ticket acceptance gates are not weakened.
- [ ] Required GitHub checks/reviews and the current PR head are evaluated with actionable blocked reasons; promoting a draft never merges it.
- [ ] Repeated readiness is safe, and added/reopened work, changed heads, or cleanup commits invalidate stale evidence; merge callers can recompute the same gates immediately before merging.
- [ ] Preview is read-only. Tests cover empty backlog with WIP/review children, unmet dependencies/acceptance, already-ready PRs, changed heads, and unrelated backlog.

## Approach and decisions

Keep gate evaluation reusable by T-5dae58cb. Do not treat an AGENT-labelled
comment or the PR author's advisory self-review as independent approval.

## Verification

Test local lifecycle fixtures and mocked GitHub state transitions, including
checks/reviews invalidated by a new head. Run the unit suite.

## Handoff

Provide gate diagnostics and current-head test evidence to the human reviewer.
