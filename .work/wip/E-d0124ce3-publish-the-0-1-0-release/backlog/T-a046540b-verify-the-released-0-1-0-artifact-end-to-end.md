---
{
  "id": "T-a046540b",
  "kind": "task",
  "title": "Verify the released 0.1.0 artifact end-to-end",
  "status": "backlog",
  "parent": "E-d0124ce3",
  "depends_on": [
    "T-05a14bf8"
  ],
  "implementer": "agent",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Verify the released 0.1.0 artifact end-to-end

## Purpose and scope

Prove that a brand-new user can get exactly what the release advertises, without
relying on the development checkout.

## Acceptance criteria

- [ ] A clean checkout of `v0.1.0` passes `python3 -m unittest discover -s tests -v` and `./work --root . check`.
- [ ] `./work setup` then `work --version` prints `0.1.0`; installing into a fresh project yields `./.workkit/work --version` of `0.1.0` and a `.workkit/VERSION` of `0.1.0`.
- [ ] The GitHub release's source assets (zip/tarball) extract to the same `0.1.0` content as the tag.
- [ ] The release page, tag, and changelog date/version are all consistent.

## Approach and decisions

The agent gathers the clean-checkout and install evidence and reports any
discrepancy; the human confirms the release is what they approved.

## Verification

Record the commands, versions, test counts, and links for each check above.

## Handoff

This is the final acceptance gate for the release epic. No further publication.
