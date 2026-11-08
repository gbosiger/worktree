---
{
  "id": "E-d0124ce3",
  "kind": "epic",
  "title": "Publish the 0.1.0 release",
  "status": "done",
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
- [x] Tag-triggered Python 3.10/3.12/3.13 tests and `work check` gate publication with changelog notes and source zip/tarball assets; push/pull_request CI remains configured. Accepted first-release deviation: publication used the documented fallback after the tag matrix passed; the corrected future automation is reviewed/tested, not claimed as an exercised successful tag-publication run.
- [x] Repository presentation has status/version badges, the retained correct LICENSE notice, clean tracked sources, and exact description/homepage/topic commands prepared as allowed by T-64380128. Accepted preparation-only deviation: account About/topic settings remain unchanged, rather than claiming those remote settings were applied.
- [x] An annotated `v0.1.0` tag exists on the approved default-branch commit, and GitHub shows `0.1.0` as the repository's first and latest release (not a pre-release) with accurate notes and assets.
- [x] A clean checkout of `v0.1.0` passes the test suite and `work check`, installs into a fresh project, and reports `0.1.0`; the release's source assets match the tag.

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

At the end of local preparation, remaining gates were publication/final verification, not a routine agent
review pause: separately authorize integrating these preparation commits onto
master and publishing its approved exact commit, confirm version/date/signing,
then execute T-05a14bf8 and verify the actual release in T-a046540b. Both stay
backlog/human-owned; the epic stays WIP until all release evidence exists.
About/topic edits are prepared but not applied. `docs/PUBLISHING.md` gives the
exact sequence, including why a partially complete release epic must not be
falsely accepted to satisfy `work merge`.

Follow-up authorization (2026-11-08): the maintainer reassigned both remaining
tickets to implementer `agent`, retaining human review, and explicitly selected
"Publish and verify". This authorizes integrating preparation onto master,
necessary master/tag pushes and GitHub release publication, an unsigned annotated
v0.1.0 tag because no signing key is configured, and artifact verification before
the publication ticket is accepted (explicit dependency-gate exception). The
epic remains WIP and both tickets must await human review. Account About/topic
settings are still only prepared commands, not authorized/applied mutations.

Publication/verification outcome: v0.1.0 is published at
https://github.com/gbosiger/worktree/releases/tag/v0.1.0 from master commit
513fa970c36b50408ccb8b0d9358d952491ba031. T-05a14bf8 and T-a046540b are in
human review with complete evidence; no human acceptance has been asserted.
The public-clone tagged suite passed 197 tests; both downloaded source formats
match all 105 tracked files, executable bits, and symlink targets and install
successfully. The epic remains WIP pending human review and the remaining
repository-presentation/automated-workflow criteria.

Important limitation: the first tag's three hosted matrix jobs passed but its
automated archive preparation failed due to checkout peeling the annotation.
The documented manual fallback published the unchanged approved tag. The
future-workflow correction reopened T-b0466ca9 and was independently reviewed,
accepted, committed (b013b25110b9), integrated and pushed onto master. Its 198-test
ordinary CI passed (run 42524805030); no new tag was created to claim a tested
automatic publication. The automated-publication epic checkbox remains unchecked
for honest human assessment. About/topic settings likewise remain prepared, not
applied. Human review should acknowledge these facts before final epic acceptance.

## Final maintainer approval

The maintainer explicitly stated in this conversation: "I accept evertyhing..
finalize". This supplies human acceptance for both reviewed tickets and the
release epic, including the disclosed manual fallback/unchanged tag and the
prepared-only account metadata. The two formerly unchecked epic criteria above
are transparently restated to record those accepted delivery deviations; this
does not claim a successful automated publication or applied account settings.
All five children are accepted and committed. Finalization commits the epic,
integrates it into master, and archives only its complete ticket tree through
the separate integration/cleanup commits. The release tag and its artifacts
remain immutable; no new release or account-setting mutation is required.

## Acceptance record

2026-11-08T21:30:17+00:00 — human: Maintainer explicitly accepted everything and requested finalization in this conversation. All five children accepted/committed; release v0.1.0 published and verified. Acceptance records disclosed manual fallback, immutable unsigned annotated tag, tested future automation correction, and prepared-only About metadata rather than fabricated remote settings or green tag publication.
