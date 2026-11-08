---
{
  "id": "S-5299cba3",
  "kind": "story",
  "title": "Complete work commands with relevant board ticket IDs",
  "status": "backlog",
  "parent": "E-f44b10c1",
  "depends_on": [],
  "implementer": null,
  "reviewer": null,
  "branch": null,
  "base_branch": null
}
---
# Complete work commands with relevant board ticket IDs

## Required behavior and value

Bash users can press Tab to find `work` commands, options, and ticket IDs that
make sense for the chosen action, without locating and copying IDs manually.

## Acceptance criteria

- [ ] Completion offers subcommands, their supported options, and fixed option values where applicable; partial ID prefixes narrow candidates.
- [ ] Ticket lookup uses the nearest ancestor `.work` board from the current directory. An explicit `--root` overrides discovery, including quoted paths with spaces, in the positions supported by the CLI.
- [ ] `start` offers backlog and review IDs; `review` offers WIP IDs; `done` offers review IDs; `commit` offers implemented IDs without repeating already-selected IDs.
- [ ] A documented command/argument matrix covers `show`, `reopen`, `assign`, `depend`, `create --parent`, and `merge`, including kind/status filters, self-reference exclusions where known, and archived-ID support or its explicit limitation.
- [ ] The matrix states which dependency, child-completion, and acceptance gates filter suggestions and which remain command-time checks. Suggestions never relax CLI validation.
- [ ] No board, malformed data, or unavailable archive history produces a quiet, safe completion result rather than shell errors, remote requests, or mutations.
- [ ] Completion can be enabled and disabled explicitly for both a toolkit checkout and an installed project; supported Bash versions and installation paths are documented without silently editing startup files.
- [ ] Automated Bash tests cover commands/options, prefixes, nested directories, nested boards, explicit roots, paths with spaces, and ticket moves between completion attempts.

## Approach and decisions

Inspect `root_at`, command parsing, transition gates, setup/install, and archive
lookup in `.work/tools/work.py`. Reuse validated read logic rather than parsing
human-oriented `work list` output as a stable protocol. Decide whether a small
read-only candidate interface is needed; do not invoke mutation commands, even
with `--dry-run`, during completion. Keep shell arguments as data, never `eval`
ticket content. Define and test a practical interactive response-time target;
avoid rescanning all Git history on every ordinary completion.

## Verification

Use temporary boards with all statuses, dependencies, groups, and separate
worktrees. Test the actual Bash completion function and verify board/index
contents are unchanged. Record the command matrix and measured latency.

## Handoff

Backlog specification only. Resolve the matrix and installation approach before
implementation; no completion script or public read interface exists from this ticket yet.
