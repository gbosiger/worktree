---
{
  "id": "E-1c6791d9",
  "kind": "epic",
  "title": "Bring Worktree Tickets into Neovim",
  "status": "backlog",
  "parent": null,
  "depends_on": [],
  "implementer": null,
  "reviewer": null,
  "branch": null,
  "base_branch": null
}
---
# Bring Worktree Tickets into Neovim

## Outcome and value

Neovim users can discover, reference, edit, and advance repository tickets without
leaving their editor. A searchable completion menu and a Neo-tree ticket source
make the Markdown board feel like a native workspace rather than a collection of
paths to remember. The CLI remains the authority for lifecycle rules.

## Scope

Included:

- A Neovim plugin with worktree-local board discovery and fresh ID-based lookup.
- Context-aware ticket reference completion, searchable by ID and title, with
  status/parent labels and a ticket preview; accepting inserts the immutable ID.
- An optional Neo-tree source alongside filesystem and Git sources: status lanes,
  optional groups, epics, and their status-grouped stories/tasks.
- Open/preview, copy ID, create, and explicit lifecycle actions using the toolkit.
- Buffer-aware actions default to the open ticket's immutable ID; an explicit
  ID or selected tree/picker entry targets that ticket instead.
- An optional Telescope picker for the plugin's list action, with searchable
  ticket rows, previews, status filters, and selection opening the Markdown file.
- Setup guidance, configurable mappings, accessibility fallbacks, and tests.

Excluded:

- A replacement ticket format, database, service, or mandatory editor dependency
  for toolkit users; changing existing lifecycle or acceptance rules.
- Git/PR automation, an AI chat integration, and automatic acceptance or commits.
- Implementing archive/history lookup from E-0182afb4; support the current
  file-backed board and document the future integration boundary.

## Acceptance criteria

- [ ] Two open projects or Git worktrees resolve their own boards, without leaking results through a global current-directory cache; opening a ticket after a status move resolves its current path by ID.
- [ ] In documented ticket-reference contexts and plugin command ID arguments, typing an ID fragment or title words offers matching local tickets with ID, title, kind, and status. Preview shows parent and acceptance context; accepting inserts only the ID. Manual invocation is available outside detected contexts.
- [ ] Completion refreshes after ticket creation, edits, moves, and removal; malformed records are diagnosed instead of crashing the editor or silently hiding unrelated valid tickets.
- [ ] A selectable Neo-tree source displays backlog/WIP/review/done, optional groups, epics, and child status lanes. Users can filter/search, expand, preview, open Markdown, and copy an ID; empty lanes have an intentional presentation.
- [ ] The tree preserves useful expansion/selection by immutable ID on refresh, follows moved tickets, and clearly distinguishes status and ticket kind without requiring icons or color.
- [ ] Users can create a ticket under a valid selected parent and explicitly start, request review, complete, or reopen it. CLI gates/errors remain visible; completion requires reviewer identity and evidence, and no action silently checks acceptance boxes.
- [ ] With a review ticket open, invoking the plugin's done action without an ID targets that buffer's ticket and still requires reviewer/evidence and all CLI gates. Explicit IDs override buffer context; tree/picker actions target the selected entry. No-context actions request selection rather than reusing a stale ticket.
- [ ] With Telescope configured, the plugin's list action opens a fuzzy-searchable picker of local tickets, with ID/title/kind/status labels, status filtering (including review), and Markdown preview. Selecting a result opens its current Markdown path by ID; cancelling does not open or mutate a ticket.
- [ ] Mutations handle unsaved ticket buffers explicitly, do not overwrite edits or target a different worktree, and refresh views only after reporting the command outcome. Cancellation changes nothing.
- [ ] Missing toolkit, absent board, unavailable optional integrations, invalid metadata, and failed commands produce actionable messages. Discovery and subprocess work do not block normal editing.
- [ ] Automated tests and a documented manual demo cover completion, tree navigation, Telescope list/selection, buffer-inferred actions, external file moves, lifecycle success/failure, and separate worktrees. Installation and supported Neovim/completion/Neo-tree/Telescope versions are documented.

## Stories and dependencies

Supporting tasks:

1. T-5e7187d5 — Design the workspace and integration contract.
2. T-d8ea9e0a — Worktree-aware board discovery and refresh.
3. T-4a0e0925 — Ticket ID/title completion and previews.
4. T-683615e7 — Neo-tree board source.
5. T-a8238487 — Safe editor actions through the CLI.
6. T-420616c1 — Telescope list, search, preview, and open.
7. T-2a480000 — Integration verification and documentation.

Design precedes discovery; completion, tree, actions, and Telescope depend on
discovery and can then progress independently. End-to-end verification follows
all four.
No external epic is a prerequisite; E-0182afb4 is related future archive work.

## Decisions and open questions

- Presentation direction: a “ticket cockpit” with compact status labels, readable
  ID/title rows, and an on-demand detail preview—not a second Markdown editor.
  Example: `Backlog → E-… Neovim workspace → WIP → T-… Completion`.
- Decide minimum Neovim version, plugin location/distribution, and CLI resolution
  for toolkit checkouts versus installed `.workkit/` projects in the design task.
- Choose initial completion adapter(s), considering blink.cmp and nvim-cmp;
  document supported contexts and avoid requiring both frameworks.
- Confirm tree layout and filtering behavior with a small sketch/demo before
  building the renderer. Keep Neo-tree optional for completion/action users.
- Telescope is optional and independent of Neo-tree. The editor list command
  opens the picker when available; retain a documented core selection fallback
  when it is absent. This does not change the terminal CLI's list output.
- Resolve action targets from explicit arguments/selected entries before current
  ticket-buffer context, never from a remembered last ticket. Read identity from
  validated board metadata, not a filename guess or arbitrary ID in the prose.
- Choose a tested data contract: current CLI output is human-oriented, so do not
  casually parse it as a stable machine API or execute Markdown as code.
- Roles are unset; establish implementer/reviewer before execution, not by
  assuming approval. Keep lasting design and user guidance in maintained docs.

## Verification and handoff

Prepared in backlog; no implementation or acceptance is claimed. Next action:
resolve design decisions in T-5e7187d5, then follow explicit dependencies. Use
fixture boards (including optional groups), headless editor tests, fake CLI
failures, and a real Neo-tree/completion smoke test. Record exact supported
versions and remaining limitations rather than claiming untested compatibility.
