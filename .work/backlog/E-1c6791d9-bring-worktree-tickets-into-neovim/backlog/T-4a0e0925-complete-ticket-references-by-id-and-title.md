---
{
  "id": "T-4a0e0925",
  "kind": "task",
  "title": "Complete ticket references by ID and title",
  "status": "backlog",
  "parent": "E-1c6791d9",
  "depends_on": ["T-d8ea9e0a"],
  "implementer": null,
  "reviewer": null,
  "branch": null,
  "base_branch": null
}
---
# Complete ticket references by ID and title

## Purpose and scope

Make references discoverable at the cursor instead of requiring remembered IDs.

## Acceptance criteria

- [ ] Implement the chosen completion adapter(s) for documented reference contexts and plugin command ID arguments, plus explicit invocation elsewhere.
- [ ] Match ID fragments and title words with deterministic ranking; show ID, title, kind, and status, with parent and acceptance context in preview.
- [ ] Accepting replaces only the reference fragment with the immutable ID, preserving surrounding text and cursor behavior.
- [ ] Parent/dependency prompts filter invalid kinds/self references where known; ordinary prose reference completion remains unrestricted by lifecycle eligibility.
- [ ] Tests cover empty/no-match results, duplicate titles, all ticket kinds, buffer-local worktree selection, refresh after moves, and missing optional adapter behavior.

## Approach and decisions

Use the shared model and selected framework APIs. Avoid noisy unsolicited
completion in arbitrary prose; document precisely where automatic triggers apply.

## Verification

Add adapter tests and a real supported-framework smoke test for typing a title,
previewing a candidate, and inserting an ID without damaging adjacent Markdown.

## Handoff

Record supported versions, trigger contexts, setup, and test evidence.
