---
{
  "id": "T-05a14bf8",
  "kind": "task",
  "title": "Tag v0.1.0 and publish the first GitHub release",
  "status": "backlog",
  "parent": "E-d0124ce3",
  "depends_on": [
    "T-516bff53",
    "T-b0466ca9"
  ],
  "implementer": "human",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Tag v0.1.0 and publish the first GitHub release

## Purpose and scope

Put the reviewed, tested `0.1.0` on the public default branch under a signed tag
and publish it as the first GitHub release. This is the explicit publication
step; it is not performed during preparation.

## Acceptance criteria

- [ ] An annotated tag `v0.1.0` exists on the exact approved commit on the default branch, signed if signing is configured, and is pushed to GitHub.
- [ ] The release workflow (or the documented `gh release create` fallback) creates the `0.1.0` release from that tag, marked latest and not a pre-release.
- [ ] Release notes match the changelog's `0.1.0` section, and the source zip/tarball assets are present and fetchable.
- [ ] GitHub lists `0.1.0` as the repository's first release, with the correct tag, commit, and date.

## Approach and decisions

Confirm the approved commit hash on the merged default branch before tagging.
Prefer `git tag -s v0.1.0 -m ...`; fall back to an annotated unsigned tag if
signing is unavailable, and record which was used. The release workflow creates
the release automatically on tag push; otherwise the human runs the fallback
command.

## Verification

Link the tag, the release URL, and the CI run for that tag. Record the commit
hash and any signing/verification output.

## Handoff

The human publishes; the agent may prepare the exact commands and notes, but only
an explicit maintainer instruction authorizes the push and the release.
