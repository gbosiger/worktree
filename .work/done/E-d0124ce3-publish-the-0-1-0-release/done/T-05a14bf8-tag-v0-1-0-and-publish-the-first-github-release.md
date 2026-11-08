---
{
  "id": "T-05a14bf8",
  "kind": "task",
  "title": "Tag v0.1.0 and publish the first GitHub release",
  "status": "done",
  "parent": "E-d0124ce3",
  "depends_on": [
    "T-516bff53",
    "T-b0466ca9"
  ],
  "implementer": "agent",
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

- [x] An annotated tag `v0.1.0` exists on the exact approved commit on the default branch, signed if signing is configured, and is pushed to GitHub.
- [x] The release workflow (or the documented `gh release create` fallback) creates the `0.1.0` release from that tag, marked latest and not a pre-release.
- [x] Release notes match the changelog's `0.1.0` section, and the source zip/tarball assets are present and fetchable.
- [x] GitHub lists `0.1.0` as the repository's first release, with the correct tag, commit, and date.

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

The maintainer explicitly authorized agent publication on 2026-11-08 (selected
"Publish and verify"), including integration onto master, necessary master/tag
pushes, and an unsigned annotated tag because no signing key is configured.
The version is 0.1.0 and the prepared changelog date matches today's UTC date.
Human review/acceptance is retained; the agent must not accept on their behalf.

Pre-publication checks: authenticated as gbosiger with repository/workflow access;
GitHub default branch is master, public repository gbosiger/worktree; no existing
releases or v0.1.0 tag. Remote master matched local master e9c6e3f8a4f1b59072d858c80bb59c377b2f138f.
The only initial dirty changes were the maintainer's implementer assignments for
these two tickets; they are preserved. Preparation previously passed 197 tests,
board validation, actionlint, and both artifact-format installation smoke tests.

## Publication evidence (2026-11-08)

- Approved source: `513fa970c36b50408ccb8b0d9358d952491ba031`, fast-forwarded
  onto master and pushed before the tag. Its clean checkout passed 197 tests
  (148.209s, Python 3.14.8) and board validation (30 tickets).
- Unsigned annotated tag object: `21674555e3eb0bb45ff000cd18017b01ccdbcc92`.
  Remote GitHub tag-ref API confirms object type `tag`; no signing key was
  configured, and the maintainer explicitly approved the unsigned annotation.
  No tag was rewritten or moved.
- Tag: https://github.com/gbosiger/worktree/releases/tag/v0.1.0
- Hosted validation: https://github.com/gbosiger/worktree/actions/runs/42523884001
  passed Python 3.10/3.12/3.13 tests and board checks. The overall workflow failed
  only afterward in archive preparation because checkout peeled the local tag
  annotation. It did not publish anything. T-b0466ca9 was reopened, fixed,
  independently reviewed, tested (198 tests), and committed as b013b25110b9.
- Used the documented manual fallback from a fresh public full-history clone at
  the unchanged tag, after hosted validation passed. Exact-tag preparation and
  both artifact smoke tests passed; the original tagged publishing script created
  a draft, uploaded the assets, and published the release. No replacement tag.
- GitHub release ID: `438529064`, name `0.1.0`, published
  `2026-11-08T21:19:42Z`, not draft/prerelease. The releases list contains exactly
  this release with `isLatest: true`; the latest-release API agrees.
- Release body matches the tagged changelog section exactly. Both source assets
  downloaded successfully and match local exact-tag preparation byte-for-byte
  and GitHub's SHA-256 digests:
  - `worktree-tickets-0.1.0.tar.gz`:
    `fea76a4e8f7d9aa58add1e559b5fb186451318fbda28d7a532a715148f1683bf`
  - `worktree-tickets-0.1.0.zip`:
    `130048a8fdf384da43cab251cdc359304008515426510873155087a7c52bbb0f`
- Local evidence: `/tmp/opencode/worktree-v0.1.0-verification-zg4556wk/`
  (`source/`, `prepared/`, `downloaded/`, and `release.json`).

Human review requested: inspect the release page, notes/assets, exact tag commit,
and successful matrix jobs. The overall automated publication run is red; the
manual fallback is the actual successful publication mechanism, not a claimed
green release workflow. Hosted jobs also emitted nonblocking Node 20 action
deprecation and ubuntu-latest migration notices. No acceptance is recorded on
behalf of the human. Artifact verification may proceed before this acceptance
under the maintainer's explicit dependency-gate exception.

## Acceptance record

2026-11-08T21:28:48+00:00 — human: Maintainer explicitly accepted all release work in this conversation: "I accept evertyhing.. finalize". Acceptance includes the disclosed manual publication fallback after successful tag matrix checks, approved unsigned annotated tag, published release and verified assets; no claim that the original automated publication run succeeded.
