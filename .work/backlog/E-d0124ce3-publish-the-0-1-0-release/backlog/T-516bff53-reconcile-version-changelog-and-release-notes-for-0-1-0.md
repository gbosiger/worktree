---
{
  "id": "T-516bff53",
  "kind": "task",
  "title": "Reconcile version, changelog, and release notes for 0.1.0",
  "status": "backlog",
  "parent": "E-d0124ce3",
  "depends_on": [
    "E-1a88a55f"
  ],
  "implementer": "agent",
  "reviewer": "human",
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

- [ ] `VERSION` in `.work/tools/work.py` is `0.1.0` (currently draft `0.2.0`), and `./work --version` prints `0.1.0`.
- [ ] `README.md` no longer reads "Draft v0.2.0"; it states the `0.1.0` release (or a version badge resolves it).
- [ ] `CHANGELOG.md` has a `## 0.1.0 - YYYY-MM-DD` section that folds the current "Unreleased", "Draft v0.2.0", and "Draft v0.1.0" entries into concise user-facing bullets, with a new empty `## Unreleased` section above it.
- [ ] A fresh `work install` into a scratch project writes a `.workkit/VERSION` of `0.1.0`, and `./.workkit/work --version` prints `0.1.0`.
- [ ] The test suite and `./work --root . check` still pass after the version change.

## Approach and decisions

Confirm the maintainer intends the first public release to be `0.1.0` (the
repository currently labels itself draft `0.2.0`). Keep the changelog
Keep-a-Changelog-style, with one dated release section and an "Unreleased" section
on top, rather than carrying draft headings into the release.

## Verification

Show `./work --version`, the `git diff` of the version/changelog/README edits, and
the scratch-install version output; report the full test and board-check results.

## Handoff

Hand the diff and a proposed release-notes section to the human reviewer. Do not
tag or publish.
