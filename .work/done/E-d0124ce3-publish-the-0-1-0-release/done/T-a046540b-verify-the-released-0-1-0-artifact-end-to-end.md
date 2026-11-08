---
{
  "id": "T-a046540b",
  "kind": "task",
  "title": "Verify the released 0.1.0 artifact end-to-end",
  "status": "done",
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

- [x] A clean checkout of `v0.1.0` passes `python3 -m unittest discover -s tests -v` and `./work --root . check`.
- [x] `./work setup` then `work --version` prints `0.1.0`; installing into a fresh project yields `./.workkit/work --version` of `0.1.0` and a `.workkit/VERSION` of `0.1.0`.
- [x] The GitHub release's source assets (zip/tarball) extract to the same `0.1.0` content as the tag.
- [x] The release page, tag, and changelog date/version are all consistent.

## Approach and decisions

The agent gathers the clean-checkout and install evidence and reports any
discrepancy; the human confirms the release is what they approved.

## Verification

Record the commands, versions, test counts, and links for each check above.

## Handoff

This is the final acceptance gate for the release epic. No further publication.

## Authorized execution exception (2026-11-08)

Preflight reported only unfinished dependency T-05a14bf8, which is now in human
review with real publication evidence. The maintainer explicitly authorized
gathering artifact-verification evidence before accepting that prerequisite,
while retaining human acceptance of both tickets. The dependency metadata is
preserved. Because the CLI intentionally has no dependency-override flag, this
ticket was manually moved from backlog to WIP with matching status under that
specific exception, not by falsely accepting the publication ticket. Branch,
ownership, board validation, and WIP ancestor gates passed preflight. The epic
remains WIP. This exception is not authority to accept either ticket.

The same exception covers the manual WIP-to-review move after verification,
because the CLI dependency gate also applies to `review`. Both tickets now await
the human; no dependency was removed and no acceptance was invented.

## Artifact verification evidence (2026-11-08)

- Fresh full-history clone from the public repository, not a local copy:
  `git clone https://github.com/gbosiger/worktree.git source`, then
  `git checkout --detach v0.1.0`. HEAD is exactly
  `513fa970c36b50408ccb8b0d9358d952491ba031`; tracked status was clean before
  and after verification. The local and remote annotated tag object is
  `21674555e3eb0bb45ff000cd18017b01ccdbcc92` (unsigned as explicitly approved).
- In that clone, `python3 -m unittest discover -s tests -v` passed all **197**
  tests in **151.087s**, Python 3.14.8. `./work --root . check` passed with
  30 valid tickets. The later workflow correction has 198 tests on master;
  it is not part of, and did not rewrite, this 197-test tagged release.
- `./work setup` with an isolated HOME, followed by actual PATH-resolved
  `work --version` from `/`, printed `0.1.0`. `work install` into a new project
  succeeded; its `.workkit/VERSION` and local launcher both reported `0.1.0`.
  The real user's HOME/PATH configuration was not changed.
- Downloaded both published assets using `gh release download v0.1.0 --repo
  gbosiger/worktree --pattern 'worktree-tickets-*'`. Both matched GitHub's
  SHA-256 digests and local preparation byte-for-byte (hashes in T-05a14bf8).
- Independently compared the complete archive manifests against `git ls-tree`
  and `git cat-file` of the tag: **105 tracked files** in each format, exact
  file contents, executable bits for regular files, and symlink targets; no
  missing/extra files. Symlink permission bits are intentionally not compared:
  Git stores link targets, not link permission bits. An initial comparison
  incorrectly treated symlink execute bits as file modes; correcting that
  verification assertion found no artifact difference.
- Ran the tagged `smoke-release.sh` against the **downloaded** tar.gz and ZIP.
  Unix tar/unzip extraction preserved executable launcher and relative links.
  Each extracted toolkit completed isolated setup, installation, version checks,
  epic/task creation, and a fresh-board check (2 tickets). Bundled historical
  development-board checks require the full-history clone, as documented.
- Release https://github.com/gbosiger/worktree/releases/tag/v0.1.0 is named
  `0.1.0`, latest, non-draft/non-prerelease, and the only release, published
  `2026-11-08T21:19:42Z`. The tag date and changelog date are also 2026-11-08.
  Release notes match the exact tagged changelog section.
- Tag matrix evidence: https://github.com/gbosiger/worktree/actions/runs/42523884001
  has successful Python 3.10/3.12/3.13 test and board jobs, but overall failed
  annotated-tag preparation. Publication used the documented manual fallback;
  that failure is not represented as a successful automated publication.
- Corrected future workflow committed as b013b25110b9 and integrated/pushed onto
  master without moving v0.1.0. Its ordinary CI passed:
  https://github.com/gbosiger/worktree/actions/runs/42524805030.
- Local evidence root: `/tmp/opencode/worktree-v0.1.0-verification-zg4556wk/`,
  including the public `source/` clone, `tag-tests.log`, `release.json`,
  `prepared/` and `downloaded/` assets, `isolated-home/`, and `fresh-project/`.

Ready for human review of the release page and evidence above. All implementation
checks are evidenced, but this is not a human acceptance record. No further
publication or tag mutation is needed for review.

## Acceptance record

2026-11-08T21:29:21+00:00 — human: Maintainer explicitly accepted all release work in this conversation: "I accept evertyhing.. finalize". Accepted public full-history tagged checkout (197 tests), clean board check, isolated setup/install, and both published assets matching all 105 tracked files, executable bits and link targets; release notes/date/version consistency recorded in this ticket.
