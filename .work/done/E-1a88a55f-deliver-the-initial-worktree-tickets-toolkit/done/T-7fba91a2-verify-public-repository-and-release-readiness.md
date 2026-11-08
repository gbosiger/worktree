---
{
  "id": "T-7fba91a2",
  "kind": "task",
  "title": "Verify public repository and release readiness",
  "status": "done",
  "parent": "E-1a88a55f",
  "depends_on": [
    "T-5079b576",
    "T-b5d61768"
  ],
  "implementer": "agent",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Verify public repository and release readiness

## Purpose and scope

Check that the toolkit on GitHub is the version you approved and that a new
user can follow its setup instructions. The agent gathers the technical
evidence below; you review its summary and decide whether anything blocks release.

Expected repository: https://github.com/gbosiger/worktree. This ticket checks
the existing repository; it does not publish anything.

## Acceptance criteria

- [x] Confirm the GitHub repository and branch are the ones you intend to share, and the repository is public.
- [x] Confirm you approved both earlier reviews: T-5079b576 (ticket rules and human–agent handoffs) and T-b5d61768 (commands and installation).
- [x] Review the agent's evidence that GitHub contains the approved version and its tests pass. Resolve any reported differences or failed checks before release.
- [x] Read the setup instructions in README.md and docs/INSTALLATION.md. They describe this repository and how to use it, without requiring a particular editor or outdated ZIP/bootstrap steps.

## Agent checks — prepare before human review

Provide a short results summary with links, not just commands or raw logs:

- Locate the two earlier reviews with `./work show T-5079b576` and
  `./work show T-b5d61768`. Report whether each was approved and any open findings.
- Record the reviewed Git commit (version identifier), the public branch URL,
  and a GitHub link to that commit. Compare the public branch with the approved
  version; a configured local remote is not evidence that the version is online.
- Run `python3 -m unittest discover -s tests -v` and `./work --root . check`
  against that version. State which version was tested. Link GitHub's automated
  test results if available; otherwise say they were not verified.
- If publication involved rewriting Git history, verify archived tickets remain
  readable using the preservation rules in docs/GIT.md. This is an agent check,
  not something the human must diagnose.

If evidence is missing, say what is missing and the next action needed. Do not
ask the human to approve an unexplained technical result.

## Results

### CI repair — 2026-11-08

The supplied GitHub Actions log tested commit
`22ef5baf86d2838b59276f148cb0176d1f16ee0c` on
`feature/E-1a88a55f-initial-toolkit`. All nine preflight tests failed in
setup because `tests/test_preflight.py` required the local-only directory
`/tmp/opencode`. The fixture now uses Python's default temporary directory,
consistent with the other test fixtures; no runner-specific setup is required.

Reconciled duplicate backlog/WIP copies of this ticket into this WIP record,
preserving the maintainer's checked criteria and agent/human ownership.
Preflight passed on the epic's recorded branch and base (`master`), with both
this ticket and its epic WIP. No unrelated work was discarded.

Verification against 22ef5ba plus this uncommitted repair:

- `python3 -m unittest discover -s tests -v`: all 174 tests pass (273.276 s),
  including all nine preflight tests. An earlier run hit the 120-second tool
  timeout; the complete rerun used a longer timeout.
- `./work --root . check`: passes, 46 live tickets.
- `git diff --check`: clean.

These are local results, not successful remote CI evidence. No commit, push,
integration, release, or new human acceptance was performed. Keep the public
revision/tests criterion unchecked until the repair is reviewed, explicitly
committed/published, and GitHub's complete Python matrix passes. This ticket
remains WIP pending that evidence; the parent epic remains WIP.

The audit and handoff below are historical and do not supersede the current
maintainer checkmarks or this repair evidence.

The repository/visibility/branch item was already checked by the maintainer.

Agent audit baseline (2026-11-07), before T-341cb396 changes:

- GitHub API confirmed https://github.com/gbosiger/worktree is public; default
  branch is master. The public
  [feature branch](https://github.com/gbosiger/worktree/tree/feature/E-1a88a55f-initial-toolkit)
  matched clean local [d4d5cde](https://github.com/gbosiger/worktree/commit/d4d5cdebf6bf3f02f9c9796adc5cd0b8d6783687)
  by git ls-remote; master remained at 9857e9b. Feature publication is not final
  integration into the default branch.
- Local tests at d4d5cde: 155 pass (91.187 s); board validation: 27 tickets OK.
- [GitHub CI](https://github.com/gbosiger/worktree/actions/runs/42385421937)
  failed because its board-check step called removed root work.py. Python 3.13
  unit tests passed; Python 3.10/3.12 jobs were cancelled, not verified successful.
- T-5079b576 and T-b5d61768 remain backlog with no human approval recorded.
  T-341cb396 fixes CI and preview paths and reconciles the review checklists;
  its unpublished working-tree checks are not proof of a passing remote run.

After T-341cb396 review and authorized publication, record the new approved
commit, compare it with the intended public branch, and verify successful CI
across the configured Python matrix. The human review and final readiness items
remain unchecked. No new history rewrite or publication occurred in this audit.

## Handoff

The human keeps final approval; the agent may gather evidence and explain
findings. The two earlier reviews must be approved before this review is finished.
This rewrite records no new approval or successful checks.

Do not push, merge, recreate the repository, change its visibility, rewrite Git
history, or publish a release without explicit authorization for that action.

## Acceptance record

2026-11-08T18:07:57+00:00 — human: n/a
