---
{
  "id": "E-1a88a55f",
  "kind": "epic",
  "title": "Deliver the initial Worktree Tickets toolkit",
  "status": "wip",
  "parent": null,
  "depends_on": [],
  "implementer": "agent",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Deliver the initial Worktree Tickets toolkit

## Outcome and value

A small open-source project can keep feature intent, stories, and human–agent
handoffs in Git, using an editor or dependency-free helper scripts.

## Scope

Include Markdown convention, lifecycle CLI, templates, project skills, tests,
copy-based adoption, and publication instructions. Exclude live cross-branch
coordination, automatic updates, automatic branch operations, and board UI.

## Acceptance criteria

- [x] Create, start, review, complete, and reopen groups/epics/stories/tasks.
- [x] Validate IDs, hierarchy, dependencies, and completion evidence.
- [x] Adopt the toolkit in another project while preserving existing instructions.
- [ ] Human reviews the draft convention, command interface, and example workflow.
- [ ] Maintainer publishes the reviewed project on their public GitHub account.

## Verification and handoff

Nine automated workflow/regression tests pass on Python 3.12.14. CI is configured
for Python 3.10, 3.12, and 3.13 but has not run remotely. Local `.work` validates.
Implementation is available for human review. Public GitHub publication and local
placement in the maintainer's ~/Projects folder remain outstanding.
