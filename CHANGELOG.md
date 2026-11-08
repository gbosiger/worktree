# Changelog

## Unreleased

- `work merge` now accepts groups as well as epics. Epic-to-WIP-group integration
  uses explicit regular merges, retaining all records and sibling lifecycle state;
  final group/standalone epic integration shares squash-plus-cleanup machinery.
  Final integration recursively materializes archived descendants and verifies
  accepted epic revisions. Follow-ups, conflicts, hook failures, and interrupted
  integration/cleanup resume through shared journals; version-1 epic journals
  remain recoverable. No ticket-format/status change, push, or branch deletion.
- Incompatible CLI default: `work list` now shows backlog stories/tasks in the
  current branch's unique epic. Use `--all` for the old complete live board,
  `--epic ID` for explicit scope, and `--status review`/`wip` for action queues.
  Missing or ambiguous context requires explicit scope. `--ready` computes
  dependency/lifecycle-unblocked backlog work without adding a stored status;
  canonical skills guide request-specific discovery before preflight.
- Accepted work now queues in `implemented/`. `work commit` derives its message
  from that queue and retains committed records in `done/`, instead of deleting
  them. `work merge EPIC` squash-integrates a complete epic, including older
  archived children, then automatically creates a separate cleanup commit.
  Journals support interrupted retained commits and merge/cleanup retries without
  resetting progress.
- Git-native file history finds accepted done tickets deleted by ordinary commits,
  without special message markers. Parent IDs restore missing epic/group chains.
  Batched commit/file reads replace per-commit Git processes; a repeatable benchmark
  covers thousands of commits/tickets.
- Readable ticket commit messages use a short subject and one Markdown ID/title
  list without embedded ticket JSON or a version trailer. Ordinary ticket commits
  retain done files in the same commit, without a separate archive snapshot.
  Integration materializes previously deleted accepted files before cleanup.
- First-release docs describe only the supported file-history contract. Removed
  prototype message codecs/readers and board migration instructions. Message-only
  records are unsupported; messages never substitute for committed ticket files.
  Current retained-commit and merge-cleanup recovery journals remain supported.
- `work preflight ID` consolidates read-only execution-context checks for agents;
  role, dirty-work ownership, and authorization decisions remain explicit.
- Project-local OpenCode shortcuts prepare groups, epics, stories, and tasks;
  canonical templates are linked, not duplicated. Query/lifecycle wrappers and
  the general dispatcher have been removed; use terminal CLI commands instead.
- Repository skill discovery uses relative links to canonical sources, including
  installed projects' `.workkit/skills/`, rather than duplicate skill files.
- Executable `work` launcher and explicit command setup; copied projects include
  their own launcher.
- Focused references replace the monolithic convention. Repository skills load
  only operation-relevant references.
- Shorter, example-led introduction with explicit archive workflow guidance.
- Lifecycle commands understand tickets archived in Git history: `show`,
  `check`, dependency and cycle validation, and ID allocation resolve archived
  records, and `reopen` restores them without overwriting live files.
- The post-integration cleanup backend archives accepted done tickets using readable
  messages and parent-tree records (snapshot then archive when necessary).
  `--dry-run` previews without writes, and `--recover` restores an interrupted
  operation from its journal without rewinding retained snapshot commits.
- Ticket commits generate subjects from ticket titles, accept optional ticket
  IDs and `-m` overrides, and offer explicit upstream-only `--push`. Help includes
  command/option descriptions and examples; work-commit documents retained commits
  and post-integration cleanup.
- Cleanup recovery proves the exact commit rather than matching archived IDs;
  preserves concurrent edits/staging, blocks mutations pending recovery, and
  refuses unknown journals. Container archival refuses ancillary files.
- Recovery refuses concurrent file-mode changes as well as content changes.
  SSH-signing integration verifies both snapshot and archive signatures without
  changing the user's Git configuration.

## Draft v0.2.0

- Child status folders inside epics and groups replace the flat prototype layout.
- Reopening preflights completed dependents of affected ancestors.
- Cycle validation includes parent/child completion prerequisites.
- Completion recognizes unchecked bullet and numbered Markdown checklist items.

## Draft v0.1.0

- Initial Markdown convention, lifecycle CLI, templates, repository skills,
  copy-based installation, and workflow regression tests.
