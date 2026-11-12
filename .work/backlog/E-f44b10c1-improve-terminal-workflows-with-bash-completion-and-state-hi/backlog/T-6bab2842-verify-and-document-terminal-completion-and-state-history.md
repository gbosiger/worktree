---
{
  "id": "T-6bab2842",
  "kind": "task",
  "title": "Test and document the terminal workflows",
  "status": "backlog",
  "parent": "E-f44b10c1",
  "depends_on": ["S-5299cba3", "S-56c90e4f", "T-10e609cd", "S-8ce9abfb", "S-c382b0f8"],
  "implementer": null,
  "reviewer": null,
  "branch": null,
  "base_branch": null
}
---
# Test and document the terminal workflows

Give maintainers a repeatable terminal walkthrough covering completion, history, and the two lifecycle shortcuts.

## Scope

Use disposable boards in a toolkit checkout and an installed project. Collect a repeatable Bash walkthrough, sample history before and after reopen, and a grouped branch setup example. Show where the normal lifecycle path differs from each opt-in and which cases still need manual verification.

## Acceptance criteria

- [ ] The walkthrough shows suggestions changing after a move and history surviving archive and reopen.
- [ ] Examples cover ordinary starts, group and epic branch setup, and confirmed or declined WIP acceptance.
- [ ] Record checks, limitations, and the module-layout decision for review.

Requirements: [Verification](../../../../docs/requirements/terminal.md#verification).
