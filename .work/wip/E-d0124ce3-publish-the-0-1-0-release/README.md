---
{
  "id": "E-d0124ce3",
  "kind": "epic",
  "title": "Publish the 0.1.0 release",
  "status": "wip",
  "parent": null,
  "depends_on": [
    "E-1a88a55f"
  ],
  "implementer": "agent",
  "reviewer": "human",
  "branch": "feature/E-d0124ce3-release-0.1.0",
  "base_branch": "master"
}
---
# Publish the 0.1.0 release

## Outcome and value

New users can install a clearly versioned `0.1.0` of Worktree Tickets from a
GitHub release whose notes say what shipped, and trust that the exact tagged
commit passed the same tests locally and in CI. Maintainers get a repeatable
tag-and-release path for future versions instead of a hand-built snapshot, with
the first release visible on the repository as the latest (and first) release.

## Scope

Included:

- Reconcile the version identifier to `0.1.0` across `VERSION`, the README, and
  the changelog (see Decisions and open questions). Convert the draft changelog
  entries into a single dated `0.1.0` release section in Keep-a-Changelog style,
  with a fresh `Unreleased` section above it.
- A GitHub Actions release workflow that runs the Python test matrix and board
  check on pushed `v*` tags and only then creates the GitHub release with
  changelog notes and source assets; harden the existing CI by pinning actions to
  commit SHAs and cancelling superseded runs.
- Repository metadata for a first public release: status/version badges, About
  text and topics, and a pass over LICENSE, CONTRIBUTING, and `.gitignore`.
- Create and push an annotated `v0.1.0` tag on the approved default-branch commit
  and publish the first GitHub release (marked latest, not a pre-release).
- Verify the released artifact installs and works from a clean checkout.

Excluded:

- Future feature work (Neovim, GitHub PR integration, terminal completion) — those
  remain separate backlog epics and are not prerequisites for this release.
- Automatic acceptance or human review, and any unrequested history rewrite,
  default-branch rename, or repository re-platforming.
- Adding dependency bots, issue/PR automations, or other machinery the maintainer
  has not asked for (decided in T-64380128).

## Acceptance criteria

- [x] `./work --version` and a fresh `work install` both report `0.1.0`; the README no longer claims a draft version, and the changelog has a dated `0.1.0` release section plus an empty `Unreleased` section.
- [ ] Pushing a `v*` tag runs CI (Python 3.10/3.12/3.13 tests and `work check`) and creates the GitHub release only after those pass, with release notes from the changelog and source zip/tarball assets; the existing tests workflow still runs on push and pull_request.
- [ ] The GitHub repository shows the intended description, topics, homepage, status/version badges, correct LICENSE year/holder, and no committed cache or build artifacts.
- [ ] An annotated `v0.1.0` tag exists on the approved default-branch commit, and GitHub shows `0.1.0` as the repository's first and latest release (not a pre-release) with accurate notes and assets.
- [ ] A clean checkout of `v0.1.0` passes the test suite and `work check`, installs into a fresh project, and reports `0.1.0`; the release's source assets match the tag.

## Stories and dependencies

Depends on E-1a88a55f (Deliver the initial Worktree Tickets toolkit). Do not tag
or publish until that epic is accepted, committed, and merged to the default
branch.

Backlog tasks:

1. T-516bff53 — Reconcile version, changelog, and release notes for 0.1.0 (after E-1a88a55f).
2. T-b0466ca9 — Add a release workflow and harden CI (after E-1a88a55f).
3. T-64380128 — Prepare repository metadata for the first public release (after E-1a88a55f).
4. T-05a14bf8 — Tag v0.1.0 and publish the first GitHub release (after T-516bff53 and T-b0466ca9).
5. T-a046540b — Verify the released 0.1.0 artifact end-to-end (after T-05a14bf8).

Tasks 1–3 can proceed in parallel once E-1a88a55f closes. Task 4 needs the correct
version (task 1) and a working release workflow (task 2); task 3 is parallel and
not a hard gate, though it should be in place before the release is announced.
Task 5 verifies the result of task 4. Explicit metadata dependencies record this
ordering; the list above is guidance.

## Decisions and open questions

- The first public release is `v0.1.0`. The repository currently self-identifies
  as draft `0.2.0` (`VERSION` in `.work/tools/work.py`, the README footer, and the
  changelog headings). Reconcile by setting `VERSION = '0.1.0'` and folding the two
  draft changelog sections into one `0.1.0` entry. Confirm with the maintainer that
  this normalization to `0.1.0` (not `0.2.0`) is intended before tagging.
- Release mechanism: prefer a GitHub Actions release workflow triggered by a `v*`
  tag so tests gate every release. A manual `gh release create v0.1.0` is the
  fallback if the workflow is judged overkill. Pin third-party actions to full
  commit SHAs for supply-chain hygiene.
- Tag style: annotated and signed (`git tag -s v0.1.0`) is preferred; confirm
  signing (SSH or GPG) is available at execution time and fall back to an
  annotated unsigned tag if not, recording which was used.
- Default branch is `master` (per E-1a88a55f metadata and the public repository).
  Do not rename it as part of this release.
- Whether to add issue/PR templates and a SECURITY.md is optional for a small
  single-maintainer project; resolve in T-64380128 rather than requiring them here.

## Verification and handoff

Execution authorized by the maintainer on 2026-11-08: prepare the 0.1.0 release,
perform agent-capable reviews and completion, and commit between tickets without
publication. The maintainer explicitly authorized creating the recorded release
branch from master. The three local preparation tasks use agent review under
that instruction; publication and final released-artifact acceptance remain
human-owned. The clean starting checkout had no unrelated edits.

The requested 0.1.0 epic establishes the intended version normalization for
local preparation. Confirm the final version/date and approved default-branch
commit before tagging. No tag, push, merge, release, or account-setting mutation
is implied by local preparation.

Local preparation outcome: T-516bff53, T-b0466ca9, and T-64380128 have independent
approval and passing verification. Each task records its evidence and is committed
separately. The final local suite passed 197 tests; both source formats were
installed and their fresh boards checked. Hosted Python-matrix execution is not
claimed. GitHub's releases API still returned no releases on 2026-11-08.

Remaining gates are real publication/final verification, not a routine agent
review pause: separately authorize integrating these preparation commits onto
master and publishing its approved exact commit, confirm version/date/signing,
then execute T-05a14bf8 and verify the actual release in T-a046540b. Both stay
backlog/human-owned; the epic stays WIP until all release evidence exists.
About/topic edits are prepared but not applied. `docs/PUBLISHING.md` gives the
exact sequence, including why a partially complete release epic must not be
falsely accepted to satisfy `work merge`.
