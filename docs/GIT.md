# Git workflow

## Branches

Default epic branch: `feature/E-<id>-slug`, based on `main` or the actual default
branch. Record the actual `branch` and `base_branch` in epic metadata. An optional
group branch is `feature/G-<id>-slug`: child epics target the group, which targets
the default branch. Stories may share the epic branch or use short child branches.

Branch creation and merging are explicit. Status commands never switch
branches, stage code, commit, push, or merge. Commit authorization does not
authorize publication.

## Commit messages

Use `type(scope): description [TICKET-ID]`, for example:

```text
feat(search): support title queries [S-1234abcd]

Explain the behavior, acceptance, and verification relevant to this change.
```

Use meaningful types such as feat, fix, docs, test, refactor, or chore. For
multiple tickets, a `Tickets:` footer lists every ID. Preserve IDs through
squash/merge messages and PR summaries. Do not create meaningless tickets for
initial bootstrapping.

Inspect status and diffs; stage only intended code, documentation, and ticket
changes. Preserve unrelated work and existing Git identity/configuration.

## Limits

The board is branch-local: changes are visible elsewhere only after merging.
The local `.work/.lock` serializes helper commands in one worktree, not direct
editor writes, independent worktrees, or separate machines. Review status and
moves during merges; run `check` afterwards. There are no live assignments or
cross-worktree locks.

## Planned commit archive

The intended next workflow archives accepted ticket content in commit-message
bodies and removes completed ticket files, instead of keeping `done/` folders.
Automatic concatenation, branch-based selection, archive lookup, and restoring
archived tickets are **not implemented**. Today completion still uses `done/`;
do not delete completed tickets or claim archive support exists.
