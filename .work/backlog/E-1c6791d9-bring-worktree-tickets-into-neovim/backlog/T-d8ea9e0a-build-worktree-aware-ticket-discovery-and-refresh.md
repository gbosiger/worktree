---
{
  "id": "T-d8ea9e0a",
  "kind": "task",
  "title": "Build worktree-aware ticket discovery and refresh",
  "status": "backlog",
  "parent": "E-1c6791d9",
  "depends_on": ["T-5e7187d5"],
  "implementer": null,
  "reviewer": null,
  "branch": null,
  "base_branch": null
}
---
# Build worktree-aware ticket discovery and refresh

## Purpose and scope

Provide the shared board model and asynchronous refresh used by all plugin views.

## Acceptance criteria

- [ ] Discover the correct project board from the active buffer with documented explicit-root overrides; isolate multiple projects and Git worktrees.
- [ ] Read current JSON-frontmatter Markdown records, including optional groups, without evaluating content; expose ID, title, kind, status, parent, path, and preview content.
- [ ] Diagnose malformed/duplicate records and missing boards without crashing or hiding unrelated valid records.
- [ ] Invalidate on relevant saves, external creates/edits/moves/removals, and successful plugin mutations; provide manual refresh and resolve moved paths by ID.
- [ ] Fixture/headless tests demonstrate isolated caches, stale-result protection, external moves, and nonblocking scheduled updates using the design's responsiveness criteria.

## Approach and decisions

Implement the contract selected by T-5e7187d5. Do not add a persistent database or
make undocumented CLI output an implicit machine protocol.

## Verification

Exercise two worktrees, nested groups, malformed files, rapid refreshes, and a
ticket moved while selected. Record test commands and results.

## Handoff

Document model/refresh interfaces for completion, tree, and action consumers.
