---
{
  "id": "T-2a480000",
  "kind": "task",
  "title": "Verify and document the Neovim ticket workflow",
  "status": "backlog",
  "parent": "E-1c6791d9",
  "depends_on": ["T-4a0e0925", "T-683615e7", "T-a8238487", "T-420616c1"],
  "implementer": null,
  "reviewer": null,
  "branch": null,
  "base_branch": null
}
---
# Verify and document the Neovim ticket workflow

## Purpose and scope

Verify the integrated editor experience and provide reproducible installation,
configuration, troubleshooting, and a short end-to-end demo guide.

## Acceptance criteria

- [ ] Automated coverage spans discovery, completion insertion, tree refresh, and safe CLI actions using temporary boards and supported headless Neovim tooling.
- [ ] A manual smoke-test record names actual Neovim, completion framework, and Neo-tree versions and covers finding a title, inserting its ID, opening/editing, advancing, and observing refresh.
- [ ] Record the tested Telescope version and demonstrate list filtered to review → fuzzy search → preview → open Markdown → done without an ID, with reviewer/evidence prompts and a rejected-gate example. Verify explicit target overrides, cancellation, moved-result lookup, and operation without Telescope.
- [ ] Include separate worktrees, optional groups, external file moves, unsaved buffers, absent integrations/toolkit, malformed metadata, and failed lifecycle gates in the verification matrix.
- [ ] Publish setup examples for toolkit and installed projects, optional integrations, mappings/commands, text-only display, refresh/troubleshooting, and explicit archive limitations.
- [ ] Run the Python regression suite and board check; record evidence and remaining limitations without inventing reviewer acceptance.

## Approach and decisions

Verify the epic criteria against the implemented contract. Keep documentation in
maintained project docs rather than embedding the only setup guide in this ticket.

## Verification

Run the plugin's documented tests, `python3 -m unittest discover -s tests -v`,
and `./work --root . check`, then record the real integration smoke-test results.

## Handoff

Link docs and test evidence; identify unresolved defects and request epic review
only when observable criteria are satisfied. Do not mark acceptance on behalf of
an unset reviewer.
