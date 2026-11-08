---
{
  "id": "T-516bff53",
  "kind": "task",
  "title": "Reconcile version, changelog, and release notes for 0.1.0",
  "status": "done",
  "parent": "E-d0124ce3",
  "depends_on": [
    "E-1a88a55f"
  ],
  "implementer": "agent",
  "reviewer": "agent",
  "branch": null,
  "base_branch": null
}
---
# Reconcile version, changelog, and release notes for 0.1.0

## Purpose and scope

Make every place that names the toolkit's version agree on `0.1.0` and turn the
changelog into a dated, release-ready `0.1.0` section so the release notes are
mechanical to produce. No tag or release is created here.

## Acceptance criteria

- [x] `VERSION` in `.work/tools/work.py` is `0.1.0` (previously draft `0.2.0`), and `./work --version` prints `0.1.0`.
- [x] `README.md` no longer reads "Draft v0.2.0"; it states the `0.1.0` release (or a version badge resolves it).
- [x] `CHANGELOG.md` has a `## 0.1.0 - YYYY-MM-DD` section that folds the current "Unreleased", "Draft v0.2.0", and "Draft v0.1.0" entries into concise user-facing bullets, with a new empty `## Unreleased` section above it.
- [x] A fresh `work install` into a scratch project writes a `.workkit/VERSION` of `0.1.0`, and `./.workkit/work --version` prints `0.1.0`.
- [x] The test suite and `./work --root . check` still pass after the version change.

## Approach and decisions

Confirm the maintainer intends the first public release to be `0.1.0` (the
repository currently labels itself draft `0.2.0`). Keep the changelog
Keep-a-Changelog-style, with one dated release section and an "Unreleased" section
on top, rather than carrying draft headings into the release.

## Verification

Show `./work --version`, the `git diff` of the version/changelog/README edits, and
the scratch-install version output; report the full test and board-check results.

## Handoff

The maintainer authorized agent implementation, review, and completion for local
preparation in this run. Independent review (session
`ses_e433e9c37ffejEf1Tf4z1OJVKX`) approved the actual diff without blocking
findings, conditional on the main agent's verification. No tag or publication.

Evidence (2026-11-08): `./work --version` printed `0.1.0`; a temporary project
under `/tmp/opencode` installed successfully, its `.workkit/VERSION` equaled
`0.1.0`, and its local launcher printed `0.1.0`. `./work --root . check`
reported 30 valid tickets. `git diff --check` passed.
`python3 -m unittest discover -s tests -v` passed all 192 tests (146.800s,
Python 3.14.8). Python 3.10/3.12/3.13 remain CI verification, not local claims.

## Acceptance record

2026-11-08T20:05:05+00:00 — agent: Independent diff review ses_e433e9c37ffejEf1Tf4z1OJVKX approved; 192 tests passed on Python 3.14.8; board check passed; fresh install and both version outputs verified as 0.1.0.
