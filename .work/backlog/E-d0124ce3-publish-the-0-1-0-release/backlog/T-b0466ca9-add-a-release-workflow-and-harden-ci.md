---
{
  "id": "T-b0466ca9",
  "kind": "task",
  "title": "Add a release workflow and harden CI",
  "status": "backlog",
  "parent": "E-d0124ce3",
  "depends_on": [
    "E-1a88a55f"
  ],
  "implementer": "agent",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Add a release workflow and harden CI

## Purpose and scope

Make releases reproducible: a pushed `v*` tag must pass the same test matrix as
every commit and only then create the GitHub release with changelog notes and
source assets. Also tighten the existing workflow so third-party actions are
pinned and superseded runs are cancelled.

## Acceptance criteria

- [ ] `.github/workflows/release.yml` triggers on tags matching `v*`, runs the Python 3.10/3.12/3.13 unit tests and `./work --root . check`, and creates or updates the GitHub release only after they pass, marked latest and not a pre-release.
- [ ] Release notes come from the changelog's `0.1.0` section (or a bounded fallback), and the source zip/tarball are attached. Re-running for the same tag does not create a duplicate release.
- [ ] `tests.yml` still runs on push and pull_request, with a `concurrency` group that cancels superseded runs.
- [ ] All third-party actions (`actions/checkout`, `actions/setup-python`, and the release action) are pinned to full commit SHAs, not mutable tags.
- [ ] No new mandatory external service or secret beyond the standard `GITHUB_TOKEN`, with `contents: write` scoped to the release job only.

## Approach and decisions

Recommend `softprops/action-gh-release` (or the equivalent via `gh release create`)
pinned to a SHA. Keep `contents: read` on the test job; grant `contents: write`
only to the release job. Document the manual `gh release create` fallback in the
workflow comment or docs/PUBLISHING.md.

## Verification

Run a YAML lint (`actionlint` where available), review the workflow trigger and
permissions, and confirm the release job depends on the test job's success. Note
that a real tag push is exercised in T-05a14bf8, not here.

## Handoff

Hand the workflow diff and the manual fallback instructions to the human reviewer.
