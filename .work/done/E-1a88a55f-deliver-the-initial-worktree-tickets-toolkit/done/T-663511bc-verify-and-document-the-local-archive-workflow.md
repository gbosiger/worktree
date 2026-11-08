---
{
  "id": "T-663511bc",
  "kind": "task",
  "title": "Verify and document the local archive workflow",
  "status": "done",
  "parent": "E-1a88a55f",
  "depends_on": [
    "T-2c08fd6d"
  ],
  "implementer": "agent",
  "reviewer": "agent",
  "branch": null,
  "base_branch": null
}
---
# Verify and document the local archive workflow

## Purpose and scope

Validate the complete accept/commit/lookup/reopen workflow and update user-facing
guidance. This is cross-feature verification, not a replacement for per-task tests.

## Acceptance criteria

- [x] An end-to-end disposable-project test accepts multiple children, archives them, completes/archives their container, resolves dependencies, and reopens content with historical evidence intact.
- [x] Exercise explicit/fallback branches, unrelated staged/unstaged work, failure recovery, missing history, and a squash carrying approved records; record results and limitations against the epic criteria.
- [x] README, focused format/Git/lifecycle docs, CLI help, and canonical skills explain done queues, explicit archival, staged-snapshot semantics, history preservation, and recovery without claiming remote publication.
- [x] Installed toolkit behavior is checked from an unrelated working directory; instructions remain self-contained and do not require a global service or third-party Python package.
- [x] Full unit suite and dogfood check pass; provide evidence for human review without auto-checking acceptance or claiming reviewer approval.

## Approach and decisions

Keep durable guidance in docs/ and canonical skill sources in skills/. Replace
planned-feature disclaimers only for functionality actually implemented.

## Verification

`python3 -m unittest discover -s tests -v` → **154 tests, OK** (~101s). This
suite is the primary exercise of criterion 2: explicit/fallback branch
selection (test_cleanup.py: explicit-branch-current, explicit-branch-elsewhere,
unset-branch-current), unrelated staged/unstaged work
(test_retained.py::test_approval_queues_and_commit_retains_exact_handoff),
failure recovery (test_failed_commit_restores_implemented_files_and_index,
test_interrupted_*, test_failed_cleanup_resumes_*, test_failed_integration_*),
missing history (test_fresh_main_only_clone_can_show_and_reopen_without_feature_history),
squash carrying records (test_merge_*), and legacy v1/v2 readability (test_archive.py).

`./work --root . check` → **OK: 27 tickets**.

Isolated end-to-end exercise (`/tmp/opencode/wt-e2e`, disposable git repo,
`main` base + `feature/e2e-demo` branch):

- Created epic `E-39ecf9b1` "Demo feature" and tasks `T-d64df66b` (First
  change), `T-c2223c35` (Second change); `T2` depends on `T1`.
- Approved each (check criteria, `assign agent/agent`, `start`/`review`/`done`)
  then `work commit` retained both tasks in `done/`; approved and committed the
  epic next. Dependency gate held: `T2` could not start until `T1` was completed.
- `work merge E-39ecf9b1` produced a squash integration commit
  (`ea6fc26 feat: Demo feature [E-39ecf9b1]`) plus a separate cleanup commit
  (`4c963ba chore: archive completed epic [E-39ecf9b1]`); source branch and
  checkout unchanged, nothing pushed. A dirty checkout (an untracked scratch
  script) correctly blocked the first merge with "clean checkout" guidance.
- From a fresh `--single-branch --branch main` clone (no feature history):
  `work show T-d64df66b` resolved the archived record with its acceptance
  evidence intact; `work check` passed; `work reopen T1` was correctly blocked
  by its completed dependent ("Reopen completed dependents first: T-c2223c35"),
  and reopening `T2` then `T1` restored the epic to `wip` and both tasks to
  `backlog` (final check OK: 3).

Installed-toolkit check (`/tmp/opencode/wt-install`, unrelated cwd): `work
install` into a fresh project, then `./.workkit/work --version` (0.2.0), an
epic/task create, and `check` all succeeded from that directory. The runtime
imports only the Python standard library (argparse, base64, contextlib,
datetime, hashlib, json, math, os, pathlib, re, shutil, subprocess, sys,
tempfile, uuid); no third-party package or global service is required.

Documentation review: README.md, docs/FORMAT.md, docs/GIT.md, docs/LIFECYCLE.md,
the `commit`/`merge` CLI help, and skills/work-commit + work-execute already
describe done queues, explicit archival, staged-snapshot semantics, history
preservation, and recovery accurately. One stale claim remained and was fixed:
docs/OPENCODE.md line 44 ("The planned archive CLI is still unavailable") now
points to the terminal-only `work commit`/`work merge` verbs.

Limitations/notes: (1) the success path of `work commit`/`work merge` prints a
"Recovered: …" journal-cleanup line that reads oddly during a normal,
non-recovery run — cosmetic, behavior is correct and test-covered, left
unchanged here. (2) Automatic group-release orchestration is still unsupported
(documented in GIT.md/MIGRATIONS.md; expected scope). (3) The broader stale-wording
sweep for other docs is a separate backlog task (T-d190ce5e); this task fixed
only the OPENCODE.md contradiction it found while verifying the workflow.

## Handoff

All five acceptance criteria are met and evidenced above; epic acceptance
criteria 53–61 (archive behavior) are exercised by the 154-test suite plus the
manual end-to-end run. Handing off into review: a separately requested agent
reviewer should read the actual diff, re-verify the criteria against this
evidence, and then record acceptance. No acceptance is claimed here, and this
does not accept the parent epic.

## Acceptance record

2026-11-07T12:40:56+00:00 — agent: Agent review: read the full diff (docs/OPENCODE.md stale-claim fix plus the ticket's verification evidence). Independently re-ran the suite (154 tests OK in 91.6s) and dogfood check (27 tickets OK). Confirmed the e2e scratch repos: merge commits ea6fc26/4c963ba on main, archived show/reopen dependency behavior, and install 0.2.0 from an unrelated cwd with stdlib-only imports. Verified all five criteria against evidence; no blocking findings. Non-blocking notes: cosmetic 'Recovered:' line on normal commit/merge success, group-release still unsupported, and stale-doc sweep tracked separately in T-d190ce5e.
