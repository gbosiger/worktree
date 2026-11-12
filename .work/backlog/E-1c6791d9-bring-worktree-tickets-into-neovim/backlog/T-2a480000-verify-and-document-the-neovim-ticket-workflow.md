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

Give a Neovim user a tested setup guide and a walkthrough they can repeat.

## Scope

Start from the implemented plugin and its supported-version decisions. Produce a setup guide for both installation layouts and run the workflow with a real editor as well as fixtures. Record the tested versions and which optional integrations were present so another maintainer can reproduce failures.

## Acceptance criteria

- [ ] The guide identifies tested versions and covers both checkout and installed setups.
- [ ] A recorded walkthrough shows completion, tree navigation, picker selection, and a successful and rejected action.
- [ ] The reviewer can find the headless results and any manual checks still outstanding.

Requirements: [Verification](../../../../docs/requirements/neovim.md#verification).
