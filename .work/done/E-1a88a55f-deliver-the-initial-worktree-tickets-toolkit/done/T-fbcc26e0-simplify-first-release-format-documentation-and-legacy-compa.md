---
{
  "id": "T-fbcc26e0",
  "kind": "task",
  "title": "Simplify first-release format documentation and legacy compatibility",
  "status": "done",
  "parent": "E-1a88a55f",
  "depends_on": [],
  "implementer": "agent",
  "reviewer": "agent",
  "branch": null,
  "base_branch": null
}
---
# Simplify first-release format documentation and legacy compatibility

## Purpose and scope

Address the maintainer's T-5079b576 review finding: this is the first release,
not an installed public format migration. Users should learn the current format
and workflow, not obsolete prototype archive versions and migration history.
The maintainer explicitly does not require compatibility with older prototype
commits. Simplify docs and assess/remove code and tests maintained solely for
those obsolete contracts, without rewriting Git history or historical tickets.

## Acceptance criteria

- [x] docs/FORMAT.md describes the current ticket, metadata, lifecycle-storage, and file-history archive contract without legacy v1/v2 specifications or prototype migration instructions.
- [x] Related Git/lifecycle/install guidance, help, skills, and reference links consistently describe the first-release contract; obsolete migration guidance is removed from the current user path rather than copied elsewhere as required reading.
- [x] Legacy codecs, readers, journal compatibility, and their tests are audited; obsolete-only support is removed where unnecessary, and any retained behavior has a concrete current-format safety rationale recorded in the handoff.
- [x] Current retained commits, post-integration cleanup, ordinary accepted-file deletion lookup, dependency validation, and parent-chain reopening remain supported and tested.
- [x] Existing unsupported prototype artifacts produce actionable errors when encountered rather than silently implying completion or triggering destructive automatic migration.
- [x] The handoff reports any effect on this repository's dogfood archive lookup and identifies needed decisions before removing data or changing live ticket records; no history rewrite, fabricated approvals, or silent conversion occurs.
- [x] Documentation/reference checks, current-format regression tests, and board validation pass, with any pre-existing obsolete-history limitation explicitly reported.

## Approach and decisions

Read docs/FORMAT.md before format changes and docs/LIFECYCLE.md before lifecycle
changes. Audit actual references and code before deleting compatibility paths:
the current Git common-directory merge journal, interrupted current transactions,
and native file-history lookup are not obsolete simply because some supporting
code also handles legacy versions.

Keep historical ticket evidence historical; do not rewrite old records to make
them appear current. The goal is a smaller honest first-release contract, not
moving a large legacy appendix to a different mandatory document. Coordinate
with T-7ff2dcbf on archive and recovery changes to avoid contradictory contracts.

### Implemented contract and compatibility audit

- Removed runtime `encode_archive`, `decode_archive`, and `archive_file_records`.
  Native lookup no longer loads/parses commit messages; only validated accepted
  files deleted from reachable commit trees supply records. A copied prototype
  payload/trailer cannot establish approval or resurrect stale evidence.
- Removed the legacy specification sections from docs/FORMAT.md and deleted
  docs/MIGRATIONS.md rather than moving its steps to another required guide.
  Updated focused docs, index/contributor/install guidance, changelog, skill
  references, and board-layout errors to describe the current format only.
- Converted codec tests to strict saved-file validation tests, preserving
  malformed metadata/path/content rejection. Converted historical envelope
  fixtures to committed accepted files followed by deletion commits; retained
  ancestry/conflict/dependency/reopen/install and byte-preservation coverage.
  Removed three obsolete envelope-writer/framing tests, added a documentation
  contract regression, and dropped the benchmark's prototype-marker mode.
- Kept strict JSON, accepted-ticket, path/hash, duplicate-ID, and provenance
  validation: these protect current ordinary deleted files, not old messages.
- Kept retained-commit journal version 3, cleanup journal version 2, and the
  Git-common-directory merge journal version 1. These are CURRENT transaction
  formats: `merge_command` calls `commit_apply`, which still writes cleanup
  journal version 2 and relies on its exact-commit/index/file/mode recovery.
  Treating those numbers as obsolete release versions would break current merge
  recovery. Cleanup preparation/snapshot guards and their backend safety tests
  remain; the public commit CLI only consumes implemented work and retains done.
  Unknown/ambiguous transaction formats still fail with manual-recovery guidance
  without discarding their journal. No compatibility converter was added.
- This is an intentional incompatible pre-release internal API change: callers
  must use native file-history lookup, not the removed prototype codecs. Archived
  files with old message trailers remain readable solely from their valid files;
  message-only tickets now fail lookup with guidance to restore original accepted
  files explicitly. Historical messages/tickets are not edited or converted.

### Dogfood history impact

Before changes, audited all nine archived IDs:
T-0d73eaf7, T-0e7c2a61, T-289852f6, T-2c08fd6d, T-4e1573f6,
T-7147e599, T-8c250b3f, T-a40da41b, and T-b0097cfe. An in-memory audit
ignoring commit messages found identical files and provenance for all of them.
After removing message support, the full sorted-JSON fingerprint of all archive
records (including content, paths, hashes, and provenance) is still
`c08d7e117600d77373814fa188ab80edf1985ddfcf8327d1b26da56ac9ce3dfa`.
No archived ID disappeared or changed, no history rewrite or ticket conversion
was necessary, and no live ticket evidence was changed to preserve compatibility.

## Verification

Exercise fresh-repository and installed-toolkit current-format workflows,
including commit, merge/cleanup, lookup, dependencies, and reopen after a
base-only clone. Test clear refusal of unsupported legacy artifacts where
relevant. Check links and search maintained guidance for stale version/migration
requirements. Run `python3 -m unittest discover -s tests -v`,
`./work --root . check`, and `git diff --check`; report results and limitations.

## Handoff

Follow-up to human review T-5079b576, prepared 2026-11-08 and started on the
parent E-1a88a55f's recorded feature/E-1a88a55f-initial-toolkit / master context.
Agent implementation is recorded below; no acceptance of this task has occurred.

Implementation evidence (2026-11-08):

- Focused archive suite: 49 tests passed (70.997 s).
- First full run: 166 tests, one stale installation assertion still required
  docs/MIGRATIONS.md. Updated that assertion to require only supported guides
  and verify the deleted migration document is absent. Full rerun:
  `python3 -m unittest discover -s tests -v` passed all 166 tests (244.794 s),
  including installed-toolkit and base-only clone lookup/reopening checks.
- Markdown audit: all 17 local links across 15 maintained docs/skills resolve;
  none references the removed migration guide.
- Packed native-history benchmark: 3,000 commits / 2,000 tickets / 20 deletion
  commits, one run: 0.258 s, 7 Git processes. This is a sanity measurement,
  not a statistical performance claim.
- Actual board check passed (45 live tickets); whitespace check passed.
- Context: /home/gbo/Projects/worktree-tickets on
  feature/E-1a88a55f-initial-toolkit, base master; parent E-1a88a55f remains WIP.
  Existing preflight implementation, accepted records, user review remarks, and
  unrelated backlog epics are preserved. No commits, publication, or acceptance
  of this task have been performed. T-7ff2dcbf remains backlog.

Ready for separate review of the runtime, docs, and fixture changes. The lower
test count (166 versus 168 before this task) reflects removal of three obsolete
message-codec tests and addition of one current documentation-contract test,
not dropped lifecycle/recovery coverage. Stop at review per work-execute;
this task and the epic are not accepted by the implementation handoff.

## Review

Agent review (2026-11-08). Compared the full working-tree diff against the seven
acceptance criteria rather than trusting the implementation handoff.

- Runtime: `encode_archive`, `decode_archive`, `archive_file_records`, and the
  `ARCHIVE_START`/`ARCHIVE_END`/`ARCHIVE_V2` constants are gone; `archive_history`
  no longer loads/parses commit messages and derives records solely from accepted
  files deleted from reachable trees. No dangling references remain in the runtime
  or maintained docs/skills (grep-verified).
- Docs: FORMAT.md's two "Legacy" sections are removed; MIGRATIONS.md is deleted;
  GIT/INSTALLATION/LIFECYCLE/CONVENTION/CONTRIBUTING and the three skills no longer
  point at migrations or legacy markers. Markdown link audit: 17 links, 0 missing.
- Retention: retained-commit, cleanup, and merge journals keep their current
  version numbers with a recorded rationale that `merge_command` still writes
  cleanup journal v2; treating them as obsolete would break merge recovery.
- Unsupported artifacts: message-only prototype archives now yield an actionable
  `Message-only prototype archives are unsupported; restore the original accepted
  files explicitly` error, covered by test_message_only_prototype_cannot_supply_completion.
- Dogfood: all nine archived IDs (T-0d73eaf7, T-0e7c2a61, T-289852f6, T-2c08fd6d,
  T-4e1573f6, T-7147e599, T-8c250b3f, T-a40da41b, T-b0097cfe) still resolve via
  `work show`. (The handoff's exact fingerprint hash was not independently
  reproducible from the unspecified serialization, but record count, IDs, and
  resolvability were verified directly.)
- Checks: `python3 -m unittest discover -s tests -v` -> 166 passed (243.9s);
  `./work --root . check` -> OK (45 tickets); `git diff --check` clean.

Observation (non-blocking): the working tree also carries uncommitted work for
already-implemented T-cd66778b/T-6824d1dc and the preflight CLI, entangled in
shared files (work.py, CHANGELOG.md, work-execute/SKILL.md). The commit step for
this ticket must stage only its own changes to avoid bundling those tickets.

Verdict: acceptance criteria met; no blocking findings. Accept into implemented.

## Acceptance record

2026-11-08T12:55:36+00:00 — agent: Agent review 2026-11-08: diff compared against all 7 criteria; legacy codecs removed with no dangling refs; docs/skills migration-free (17 links resolve); journals retained with rationale; unsupported prototypes fail actionably; 9 dogfood records resolve; 166 tests pass, board check OK (45), git diff --check clean. No blocking findings.
