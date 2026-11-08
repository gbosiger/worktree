---
{
  "id": "T-b5d61768",
  "kind": "task",
  "title": "Review the CLI and project adoption",
  "status": "done",
  "parent": "E-1a88a55f",
  "depends_on": [
    "T-663511bc"
  ],
  "implementer": "agent",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Review the CLI and project adoption

## Purpose and scope

Prepare an agent usability assessment in a disposable project after automated
archive verification, for final human review. Assess whether the CLI and installed
guidance are usable; do not duplicate T-663511bc's full automated regression
campaign. The recorded roles are agent implementer and human reviewer.

## Acceptance criteria

- [x] Try create/start/review/done/reopen and board validation in a disposable project; check that outputs, errors, and required reviewer/evidence inputs are understandable.
- [x] Preview and commit accepted implemented work with deliberately staged changes; confirm the planned paths are clear and committed tickets remain in done.
- [x] In the disposable project, integrate a completed epic with work merge, then locate and reopen a ticket after cleanup; decide whether lookup and recovery guidance are clear.
- [x] Review installation from another working directory, preserved project instructions, local skill/command links, and the documented branch/ancestor workflow.
- [x] Record usability findings or release readiness; resolve blocking findings before completion.

## Approach and decisions

2026-11-07: resumed the existing WIP task with its updated agent/human roles.
Branch/worktree matched the epic: feature/E-1a88a55f-initial-toolkit, base master,
at 966752cfb33946237cf2f6629a497e2c01fcfc54. Preserved the pre-existing moves of
this task to WIP and T-7fba91a2 to backlog. Parent already WIP; no siblings started.
T-663511bc and T-341cb396 are accepted done records, so their gates are satisfied.

Use an installed copy, paths containing spaces, an unrelated working directory,
and synthetic fixture acceptance only. Git branches/commits/merge/clone in this
exercise belong solely to the disposable project, not this checkout. No network
remote was contacted and global Git configuration was not changed.

## Verification and findings

Installed source revision: 966752c. Reproduction script:
`/tmp/opencode/t-b5d61768-usability.py`.
Saved local fixture, command transcript, and report:
`/tmp/opencode/cli-usability-qp4wp85w/{transcript.json,report.json}`.
These are local diagnostic artifacts, not required project assets.

Observed results:

- Install from an unrelated directory succeeded, preserving the existing
  AGENTS.md prefix and custom command. Three skill links and four creation
  command links were valid relative links. A repeated install refused overwrite
  with "review and replace it explicitly to update". Installed version: 0.2.0.
- Reviewed help for create/start/review/done/reopen/commit/merge. Used --root
  with the installed launcher from outside the project. Created epic E-6f2875e7
  and task T-aa9d3b84; recorded feature/usability and main as fixture branches,
  started the epic before its child, and re-resolved moved paths with show.
- Missing evidence produced "Completion requires --by REVIEWER and --evidence
  TEXT"; unchecked items produced "Unchecked acceptance/completion items remain";
  wrong reviewer produced "Completion --by must match the recorded reviewer;
  use work assign first". Each failed without advancing the task. These explain
  the required correction; reviewer/evidence requirements are also in help.
- After synthetic fixture verification, done reported implemented. Commit preview
  clearly separated the selected ID, exact retained done path, staged changes,
  and generated subject/list. All fixture file bytes (including Git index/refs/
  objects) matched before/after preview. Explicit commit included staged
  example.txt and retained the task in done. Board check passed.
- Completing/committing the fixture epic then merging produced integration
  c83beb6 and cleanup a26432c on main. Feature HEAD/branch stayed unchanged,
  main gained exactly two commits, and source tickets stayed retained. Merge
  dry run also preserved all fixture file bytes. No push occurred.
- A fresh main-only clone, without the feature branch, could show the archived
  task and its evidence. Reopen restored the epic to WIP and task to backlog;
  board check passed. docs/GIT.md describes this two-commit preservation and the
  --recover route; failure/recovery regressions remain evidenced by T-663511bc
  and T-341cb396 rather than rerunning that full campaign here.
- docs/INSTALLATION.md and docs/GIT.md match the tested installed layout and
  branch/pinned-runtime behavior; canonical work-execute guidance covers the
  explicit ancestor sequence and preservation of dirty work. The CLI does not
  itself enforce agent branch/ancestor orchestration, as documented.
- The real checkout's HEAD and exact index bytes were unchanged by the exercise.
  No runtime, tests, or lasting docs were changed for this task.
- `python3 /tmp/opencode/t-b5d61768-usability.py`: passes all exercise assertions.
  `./work --root . check`: passes (28 tickets); `git diff --check`: clean.
  Full regression suite was not rerun for this ticket-only assessment; accepted
  T-341cb396 records 159 passing tests for the current runtime.

Agent assessment: no blocking usability findings in this exercise. One Low,
non-blocking finding: ordinary successful commits print "Recovered: retained done
tickets committed" and successful merge cleanup also uses recovery wording.
The final success/retention messages are correct, but the extra line can suggest
an interruption occurred. This was already noted in T-663511bc; no behavior
change is introduced here. Human review should decide whether that wording is
acceptable for this draft release or needs a follow-up.

The checked criteria record the performed agent assessment, not human approval.
Final human usability judgment and parent-epic acceptance remain outstanding.

## Handoff

Use T-060729db and T-663511bc for existing technical/e2e evidence, and
T-d190ce5e for the docs audit. Accepted T-341cb396 adds exact retained-path previews
and fixes CI; its review gate is satisfied. Acceptance goes
review -> implemented, commits retain done records, and only epic integration
performs cleanup. No removed lifecycle slash command is required. This task is
human usability judgment, not a request to repeat the full automated test suite.

Agent implementation is complete; hand off into review to the recorded human
reviewer. Review the findings above, especially the recovery-wording nit, and
record approval or concrete changes needed. Do not infer human approval from
the checked execution criteria. No push or parent acceptance is authorized.

Actual worktree: /home/gbo/Projects/worktree-tickets on
feature/E-1a88a55f-initial-toolkit. Parent E-1a88a55f stays WIP; T-7fba91a2 stays
backlog as found. This ticket moves to review. No real Git commit, branch setup,
merge, publication, or human acceptance was performed.

## Acceptance record

2026-11-07T16:49:13+00:00 — human: reviewed output from the agent
