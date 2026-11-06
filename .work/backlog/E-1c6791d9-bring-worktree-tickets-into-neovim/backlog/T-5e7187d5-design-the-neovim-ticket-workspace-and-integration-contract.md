---
{
  "id": "T-5e7187d5",
  "kind": "task",
  "title": "Design the Neovim ticket workspace and integration contract",
  "status": "backlog",
  "parent": "E-1c6791d9",
  "depends_on": [],
  "implementer": null,
  "reviewer": null,
  "branch": null,
  "base_branch": null
}
---
# Design the Neovim ticket workspace and integration contract

## Purpose and scope

Define an implementable editor-native experience and integration boundary before
choosing APIs or dependencies. Deliver a maintained design note and UX sketch.

## Acceptance criteria

- [ ] Sketch completion results/preview and Neo-tree status/group/epic/child navigation, including empty states, filtering, keyboard actions, and text-only status labels.
- [ ] Document minimum Neovim version, plugin packaging/location, initial completion adapter(s), optional Neo-tree dependency, and configuration/mapping defaults.
- [ ] Define project/worktree discovery, local versus PATH CLI resolution, async refresh, and a tested data contract; do not assume human-readable CLI output is a stable API.
- [ ] Specify completion contexts and ranking, unsaved-buffer handling, lifecycle prompts, error presentation, and a measurable responsiveness test approach.
- [ ] Specify buffer-derived action identity and explicit/selected-target precedence; sketch Telescope list/search/preview/open, status filters, no-context selection, and the core fallback when Telescope is unavailable. Document supported Telescope versions and keep it independent of Neo-tree.
- [ ] Record archive integration as future scope and resolve blocking choices or flag them for review before dependent implementation starts.

## Approach and decisions

Read docs/FORMAT.md, docs/LIFECYCLE.md, installation guidance, and current CLI
behavior. Evaluate the supported APIs of Neo-tree and candidate completion
frameworks. Keep the toolkit usable without Neovim or third-party services.

## Verification

Walk the sketch through finding a ticket, inserting its ID, opening it from the
tree, and advancing it with a rejected and a successful CLI action.

## Handoff

Link the design note, compatibility decisions, and remaining questions here.
Roles remain unset; obtain an explicit implementation/review handoff.
