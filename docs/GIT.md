# Git workflow

## Branches and execution context

Default epic branch: `feature/E-<id>-slug`, based on `main` or the actual default
branch. Record actual `branch` and `base_branch` in epic metadata. Optional group
branches may use `feature/G-<id>-slug` or a long-lived name such as
`release/0.2.0`; child epics record that group branch as their integration base.
Stories may share the epic branch or use child branches.

Before execution edits/status changes, run `work preflight ID`. This read-only
command validates the board and reports actual Git branch/worktrees, dirty paths,
target branch/base, owners, ancestor statuses, dependency blockers, and the
outermost-first backlog start order. It makes no files, locks, objects, or refs.
An explicit task/story branch wins; otherwise use the epic's recorded branch/base.
An explicit leaf branch uses its own base when set, otherwise its epic's base.
Group-only work uses its group branch. Recorded branch/base targets must exist
locally. Non-Git projects skip branch checks but still validate the board/gates.

Exit status 0 means mechanical checks passed, not that execution is authorized.
`BLOCKED` findings require resolution; `Decision` findings require judgment,
including inspecting the diff for dirty-work ownership and establishing roles.
Use `work preflight ID --for commit` for authorized Git work: it checks the same
branch context but leaves lifecycle/acceptance eligibility to
`work commit ID --dry-run`, so a done ticket is not treated as new implementation work. This
does not change commit selection's current-branch fallback for unset branches.
Missing targets, detached HEAD, mismatches, and uncertain dirty-work ownership
block execution until a concrete setup plan is authorized.
Do not relabel metadata to bless a wrong checkout or commit mixed-epic work as a
workaround. Rerun preflight after setup/context changes and report actual context
with ticket/ancestor statuses in handoffs.

Preflight observes without acquiring a toolkit lock; it refuses execution when
a board lock or commit journal is present but never removes or recovers either.
It is a point-in-time check, not protection from concurrent Git/editor writes.

Branch creation, checkout, worktree creation, stash, relocation, commits, merging,
and publication are explicit Git actions. An implementation request does not
authorize setup mutations, and commit authorization is not push authorization.
Status commands never switch branches, stage, commit, push, or merge.
`work merge ID` is explicit authorization for its documented local integration
and target-worktree setup, not acceptance or publication.

## Commit messages

Use `type(scope): description [TICKET-ID]`, for example:

```text
feat(search): support title queries [S-1234abcd]
```

For multiple items, list every ID in a readable body or Tickets footer. Preserve
IDs through squash/merge and PR summaries. Never stage indiscriminately or
discard unrelated edits, and do not change the user's Git identity/configuration.

## Commit implemented work, retain done records

Approval (`work done ID --by REVIEWER --evidence TEXT`) queues a ticket in
`implemented/`. `work commit [ID ...]` generates a short subject and one ID/title
list from selected implemented tickets, commits already-staged changes, and moves
those tickets to `done/` without deleting them. Done records are not selected again.
A selected container includes eligible queued descendants and carries previously
done children with it. Active work and tickets assigned to other branches are
never silently included. An unset ticket branch selects the current branch.

```sh
work commit --dry-run                 # preview queue, retained paths, and message
work commit T-1234abcd T-5678abcd      # commit this queued work; retain tickets
work commit --push                    # explicit upstream-only publication
work merge E-a1b2c3d4 --dry-run        # preview integration plus automatic cleanup
work merge E-a1b2c3d4                  # integrate and clean up in two base commits
work merge G-11223344                  # final release integration and cleanup
```

Commit dry runs list each selected ticket ID with its exact planned retained
done path, including moves of selected ancestor containers. These planned paths
are separate from the already-staged changes shown in the same preview.

Tickets must be staged byte-for-byte without Git filters, with .work at the Git
root. The command commits **all already-staged changes**; stage only authorized
work. Unrelated unstaged files remain unchanged. Unknown ancillary files,
symlinks, conflicts, missing identity, detached HEAD, unstaged board files, and
stale selections fail rather than losing content. `--dry-run` changes no files,
index, refs, or objects. Hooks and signing are honored; modifying hooks are
outside the supported transaction contract. Unexpected results retain the
journal rather than resetting refs or discarding concurrent work.

`--push` requires a configured upstream. It never force-pushes, publishes extra
tags, recurses into submodules, or uses mirror remotes. If push fails, the local
commit remains successful; retry `git push`, not `work commit`.

Before ticket moves, a journal at `.work/.commit-journal.json` is fsynced with
original/expected file bytes, modes, index, branch, HEAD, tree, and message.
Ordinary failure restores implemented tickets and original staging. After
interruption, inspect any stale `.work/.lock`, then use `work commit --recover`
alone. Recovery verifies the exact commit, preserves concurrent edits, and never
creates a commit or rewinds a ref. The same recovery command handles cleanup
transactions used by merge; unknown journal formats require manual recovery.
Pending commit journals block mutations, while readable boards still permit show/list/check.

## Integrate a container

`work merge ID` accepts an epic or group. Both require the recorded source branch,
a different existing local `base_branch`, clean source/target checkouts, and a done container whose descendants
are all committed done records. It uses an existing clean target worktree or
creates an isolated temporary one, leaving the source checkout/branch unchanged.

| Container | Recorded destination | Integration | Records afterward |
| --- | --- | --- | --- |
| Epic with a parent group | WIP group's branch | Explicit two-parent merge commit (`--no-ff`) | Retained under the group's `done/` |
| Standalone epic or group | Final base branch | Squash commit, then separate cleanup commit | Archived in final-base file history |

Each container needs its own explicit approval and ticket commit. Landing an epic
does not accept the group or require its siblings to be finished. The target's
group/sibling lifecycle state is preserved; intermediate source edits to unrelated
board state or divergent changes to the selected tree are rejected for explicit
reconciliation. Final integration carries nonconflicting unrelated board changes
as ordinary Git merging does, and cleanup still removes only the selected tree.
Regular merge ancestry lets a reopened, re-approved, committed epic land follow-up
changes without replaying earlier work. An unchanged, already-landed acceptance is
rejected. Follow-ups still require the group to be WIP.

For final integration:

1. Squash-merge into the base and commit **with the full completed ticket tree**.
   Previously archived children are materialized first, preserving old feature
   archives even when their snapshot history is squashed away.
2. Automatically make a separate cleanup commit removing only that container tree.
   Its parent contains every record, so a fresh base-only clone can show/reopen
   tickets and restore their parents without feature history. Archived descendants
   are restored recursively, including epics and their children inside a group.

Final group integration checks that each accepted epic revision is present through
merge ancestry and its accepted ticket contents match. A newer local epic tip must
be integrated first; if its branch has been deleted, a retained merge parent must
prove the accepted revision. Do not manually copy done epic files onto a release
branch as a substitute for integration.

Example (branches must already exist and metadata must record these targets):

```text
G-11223344: branch release/0.2.0, base_branch main
  E-a1b2c3d4: branch feature/search, base_branch release/0.2.0
  E-55667788: branch feature/filters, base_branch release/0.2.0
```

On each epic's branch, approve/commit it and run `work merge EPIC`. The group
stays WIP with both done trees retained as they land. On `release/0.2.0`, explicitly
review/approve/commit the group only after every descendant is done, then run
`work merge G-11223344` to integrate and clean up on `main`.

Keep these two base commits separate; never squash integration and cleanup
together. No implicit push, source-branch deletion, or approval occurs. Repeating
an already-cleaned acceptance is rejected rather than re-merging it.

A durable journal in Git's common directory (`worktree-tickets/merge-ID.json`)
records the target worktree and exact integration/cleanup results. A conflict or
failed hook leaves that worktree/journal available. Resolve/stage conflicts there,
then run `work merge ID --recover`; it resumes the pending phase without
duplicating a successful merge. Failed cleanup retains the integration snapshot
and retries cleanup only. Dry runs create no target worktree or journal, and
recovery dry runs only display the saved journal. Both integration policies use
the same validation, journal, recovery, and cleanup machinery. Existing version-1
standalone epic journals remain recoverable; new version-2 journals also record
retention policy and the reconciled branch-local board tree. Unknown versions
remain untouched for inspection.

Non-interactive signing needs an existing agent. Locks coordinate local toolkit
commands, not arbitrary Git/editor writes: do not concurrently edit selected
files, target worktrees, or refs. Shallow/missing history fails explicitly when
needed; the toolkit never fetches automatically. No Git configuration is changed.

## Reading deleted tickets and reopening parents

`work show ID` and `work reopen ID` find accepted done files removed by ordinary
Git commits too. Neither the deletion subject nor message needs an ID or archive
marker. Filenames contain IDs; saved files contain titles, content, and parent IDs.

For manual archival, commit accepted done files before deleting them, and remove
them only after integration. Deleting newly staged files before their first
commit does not preserve them in reachable history. Prefer the retained
`work commit` followed by `work merge` workflow for squash safety.

Reopening follows saved `parent` IDs to the epic and optional group. Missing
archived containers are restored to WIP, the selected ticket to backlog, and
siblings stay unchanged. Parents may have disappeared in different commits.
Missing/unaccepted parents fail rather than inventing replacements; existing
files and completed-dependent guards remain protected.

Lookup uses Git-native first-parent file diffs for every reachable commit,
including side branches and merge results, with batched blob reads.
It builds a compact in-memory ticket-change lookup, not a persistent database or
one subprocess per commit. Each command still reads history, so lookup is not
constant-time. Commit messages do not determine completion: only accepted files
removed from reachable committed trees supply archive records.

Run `python3 tests/benchmark_archive.py` for reader timings/process counts on a
disposable packed repository (3,000 commits/2,000 tickets by default); use
`--batches 2000` for one deletion per ticket. This excludes CLI startup and board
validation. Read-only lookup changes no files, index, refs, or configuration.

## Compatibility and limits

The first-release contract is the retained commit queue and native file-history
archive described above. Prototype message-only archives and automatic board
conversions are not supported. Missing tickets require the original accepted
files, not a copied commit message; unsupported transaction journals are retained
for manual inspection rather than guessed at or discarded.

The board is branch-local, not a live cross-worktree assignment service. Run
`check` after moves/merges. A newly initialized unborn repository has no archives;
creation works before its first commit, but committing requires an existing HEAD.

Internal lookup helpers in `.work/tools/work.py` are
`archive_history(root, revision='HEAD')` and `resolve_archive(history, id, live=None)`.
They validate saved files, preserve full content/provenance, and never infer
approval from missing history.
