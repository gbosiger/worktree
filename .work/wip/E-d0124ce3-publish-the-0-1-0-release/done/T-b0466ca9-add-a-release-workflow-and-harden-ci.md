---
{
  "id": "T-b0466ca9",
  "kind": "task",
  "title": "Add a release workflow and harden CI",
  "status": "done",
  "parent": "E-d0124ce3",
  "depends_on": [
    "E-1a88a55f"
  ],
  "implementer": "agent",
  "reviewer": "agent",
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

- [x] `.github/workflows/release.yml` triggers on tags matching `v*`, runs the Python 3.10/3.12/3.13 unit tests and `./work --root . check`, and creates or updates the GitHub release only after they pass, marked latest and not a pre-release.
- [x] Release notes come from the changelog's `0.1.0` section (or a bounded fallback), and the source zip/tarball are attached. Re-running for the same tag does not create a duplicate release.
- [x] `tests.yml` still runs on push and pull_request, with a `concurrency` group that cancels superseded runs.
- [x] All third-party actions (`actions/checkout`, `actions/setup-python`, and the release action) are pinned to full commit SHAs, not mutable tags.
- [x] No new mandatory external service or secret beyond the standard `GITHUB_TOKEN`, with `contents: write` scoped to the release job only.

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

The maintainer authorized agent review/completion of local preparation. Independent
review `ses_e43389517ffewug9m7LdExVrc2` approved the actual implementation without
blocking findings and reran all five publishing tests successfully.

Implementation uses the runner's GitHub CLI rather than an additional release
action. Checkout v4.3.1 and setup-python v5.6.0 SHAs were resolved against the
upstream GitHub tag-ref API. No mutable action references remain. Notes/version
validation and archives come from the exact annotated tag's committed files.
Both formats are smoke-tested before publication; a failed initial upload leaves
a draft that reruns reuse. A stubbed gh test verifies this retry path offline.

Verification (2026-11-08): five focused tests passed, including real toolkit setup,
installation, fresh-board creation/check, and relative symlinks from both tar.gz
and Unix unzip extraction. Actionlint 1.7.12 (download checksum verified against
its upstream release metadata) passed both workflows. Board check: 30 valid
tickets. Full suite: `python3 -m unittest discover -s tests -v` passed all 197
tests (148.540s, Python 3.14.8). `bash -n` passed both shell scripts.
No actual hosted CI, tag push, release, or remote
settings change was performed; those remain publication-ticket evidence.

`docs/PUBLISHING.md` contains approval gates, exact tag and fallback commands,
partial-epic integration guidance, and source-archive/history limitations.

## Acceptance record

2026-11-08T20:12:07+00:00 — agent: Independent review ses_e43389517ffewug9m7LdExVrc2 approved; 197 tests passed, actionlint passed both workflows, bash syntax checks passed, board valid. Archive installation and gh retry verified offline; hosted publication reserved for T-05a14bf8.
