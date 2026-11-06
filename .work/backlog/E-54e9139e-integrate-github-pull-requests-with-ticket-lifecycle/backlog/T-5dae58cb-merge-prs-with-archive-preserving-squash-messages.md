---
{
  "id": "T-5dae58cb",
  "kind": "task",
  "title": "Merge PRs with archive-preserving squash messages",
  "status": "backlog",
  "parent": "E-54e9139e",
  "depends_on": ["T-266c67e6", "T-e769d578"],
  "implementer": "agent",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Merge PRs with archive-preserving squash messages

## Purpose and scope

Implement explicitly authorized task-to-epic and epic-to-default merges without
losing archive records through either squash boundary.

## Acceptance criteria

- [ ] Generate and preview exact archive-preserving messages: task records survive the feature merge; the final epic message contains the full epic record and all task records, including earlier task merges.
- [ ] Do not rely on GitHub's generated squash message. Missing/altered records or unsupported method/queue/policy combinations block with actionable diagnostics rather than silent fallback.
- [ ] Recheck current-head gates after cleanup and immediately before merge; new cleanup commits require fresh checks and required reapproval, with no branch-protection bypass.
- [ ] Task merges allow unrelated unfinished epic children; epic merges require scoped backlog/completion/dependency/acceptance and GitHub gates. No unrequested push or merge occurs.
- [ ] Reconcile already-merged/closed PRs and ambiguous network outcomes before retrying; conflicts, permissions, protected branches, and forks fail recoverably with completed/pending actions reported.
- [ ] A normal clone of the resulting default branch resolves task/epic IDs, validates dependencies, and reopens archived content without GitHub access. Tests simulate both squash levels and failure/head-change races.

## Approach and decisions

Consume T-266c67e6 gates and T-e769d578 cleanup. Follow the approved supported
merge policy; never enable an alternative policy or weaken repository protection.

## Verification

Use fake remote merge responses plus real local squash histories to verify full
record retention, retry safety, and offline lookup/reopening.

## Handoff

Provide exact message samples and merge-safety evidence to the human reviewer.
