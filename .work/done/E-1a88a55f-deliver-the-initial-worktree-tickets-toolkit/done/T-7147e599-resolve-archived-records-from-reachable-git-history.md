---
{
  "id": "T-7147e599",
  "kind": "task",
  "title": "Resolve archived records from reachable Git history",
  "status": "done",
  "parent": "E-1a88a55f",
  "depends_on": [
    "T-4e1573f6"
  ],
  "implementer": "agent",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Resolve archived records from reachable Git history

## Purpose and scope

Provide reusable local archive encoding and lookup so later removals do not
make ticket definitions inaccessible. This task does not remove tickets.

## Acceptance criteria

- [x] Encode/decode the approved record format with lossless metadata/prose round trips and actionable malformed/unsupported-record errors.
- [x] Resolve IDs using only history reachable from the current branch, including records carried forward in squash commits, without GitHub access.
- [x] Apply the agreed precedence for repeated records and active reopened tickets; detect conflicting records rather than arbitrarily accepting one.
- [x] Missing or incomplete history never implies a prerequisite is accepted; report recovery guidance for shallow clones and unavailable records.
- [x] Tests cover multiple records, unknown metadata, Unicode/delimiter-like prose, corruption, unreachable commits, shallow history, and rearchiving.

## Approach and decisions

Use the T-4e1573f6 contract. Keep archive reads separate from mutable board paths
so downstream lifecycle and PR operations share one implementation.

Implementation notes (not a separate human approval document):

- Use one `Worktree-Tickets-Archive: 1` / `Worktree-Tickets-Archive-End` block
  containing one JSON line: version 1 and an ID-sorted tickets array. Each record
  stores ID, safe repository-relative provenance path, complete UTF-8 content,
  and its SHA-256. Escape embedded delimiters/newlines; preserve unknown metadata,
  Unicode, CRLF, and missing final newline. Reject duplicate keys/IDs, bad hashes,
  invalid accepted records, unsupported versions, and malformed/multiple blocks.
- Resolve across all commits reachable from HEAD, not other refs or timestamps.
  A descendant record supersedes ancestors; identical incomparable contents
  coalesce; divergent incomparable contents require explicit reconciliation in a
  descendant commit. Live reopened status takes precedence over archived done.
- Diagnose shallow/unavailable history without fetching or inventing acceptance.
  Squash must combine records into one envelope, preserving the latest accepted
  content/history per ID; ID footers alone are insufficient. Archive identity is
  not an authenticated reviewer signature. Document the tested format in
  docs/FORMAT.md when implemented.

## Verification

Tests in tests/test_archive.py use disposable Git histories for merged side
branches, identical/divergent records, explicit reconciliation, copied squash
records, ancestry versus timestamps, shallow linked worktrees, missing objects,
unreachable records, and rearchiving. Codec tests cover exact content, unknown
metadata, Unicode/delimiters, CRLF/no final newline, acceptance evidence, malformed
records/versions, duplicate keys/IDs, and hashes/paths. Live reopening overrides
old completion without erasing history. A filesystem snapshot confirms lookup
preserves staged/unstaged/untracked bytes and Git files; installed APIs are tested.

2026-11-06 verification:

- `python3 -m unittest discover -s tests -v`: all 51 tests pass (20 archive tests).
- `./work --root . check`: OK, 31 tickets.
- `git diff --check`: passes.

## Handoff

Implementation is in .work/tools/work.py: encode_archive, decode_archive,
archive_history, and resolve_archive. docs/FORMAT.md documents the format and
docs/GIT.md describes API use and current CLI limitations. No archive command,
file removal, or lifecycle integration is claimed; those belong to dependent
tasks. The history scan is uncached and invokes Git per commit; large-history
performance is not benchmarked.

Ready for human review on feature/E-1a88a55f-initial-toolkit in
/home/gbo/Projects/worktree-tickets. Epic E-1a88a55f stays WIP. Stop at review;
do not self-review, mark done, or start T-0d73eaf7 until review/acceptance is
explicitly authorized. No commit or publication is claimed.

## Acceptance record

2026-11-06T01:28:08+00:00 — human: Human reviewer checked implementation, all five criteria, and re-ran verification on 2026-11-06: 51/51 tests pass, work check OK (31 tickets), git diff --check clean. No blockers.
