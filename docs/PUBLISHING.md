# Publishing Worktree Tickets

The public repository is [gbosiger/worktree](https://github.com/gbosiger/worktree),
with default branch `master`. Publishing is an explicit maintainer action; local
preparation never creates a repository, pushes, or changes account settings.

## Repository presentation

The README links its CI badge and version badge to this repository. The version
badge describes the prepared source version, not an assertion that a release has
already been published. Keep it in sync when preparing future releases.

After reviewing the target account/repository, the maintainer can apply these
optional About settings (these commands mutate GitHub; preparation does not run
them):

```sh
gh repo edit gbosiger/worktree \
  --description 'Editable Markdown work tickets with explicit human-agent review and Git-native history.' \
  --homepage 'https://github.com/gbosiger/worktree#readme' \
  --add-topic 'markdown,git,cli,python,developer-tools,task-management,ai-agents'
```

The MIT license retains `2026 Worktree Tickets contributors`, matching the
project's first year and contributor ownership notice. Issue/PR templates,
SECURITY.md, dependency bots, and other automation are deliberately deferred as
optional: none is required for this small first release. Contributors can use
GitHub issues/PRs and the instructions in CONTRIBUTING.md.

## Prepare and approve

1. Review the intended version in `.work/tools/work.py`, README, and CHANGELOG.
   The first public release normalizes the unpublished drafts to **0.1.0**.
2. Keep an empty `## Unreleased` section above a nonempty dated
   `## 0.1.0 - YYYY-MM-DD` section. Confirm the date before tagging; change it
   if publication occurs later than the prepared date. Notes are extracted only
   from the matching section; missing notes or a version mismatch fail closed.
3. Integrate reviewed release preparation onto `master` before selecting its
   exact approved commit. Keep publication/final artifact tickets unfinished until
   evidence exists; do not accept the whole release epic merely to integrate
   preparation. Use a separately authorized ordinary Git merge for this staged
   release, not `work merge`'s fully-done-container gate.
4. From a clean, full-history checkout of that commit:

   ```sh
   python3 -m unittest discover -s tests -v
   ./work --root . check
   ./work --version
   git status --short
   ```

## Tag and publish (requires explicit approval)

Confirm the exact commit on the default branch, repository/account, signing
availability, and that no release/tag with this version already exists:

```sh
git switch master
git rev-parse HEAD
gh auth status
gh release list --repo gbosiger/worktree
git tag --list v0.1.0
git config --get gpg.format
git config --get user.signingkey
```

After approval, prefer a signed annotated tag:

```sh
git tag -s v0.1.0 -m 'Worktree Tickets 0.1.0' APPROVED_COMMIT
git tag -v v0.1.0
git push origin refs/tags/v0.1.0
```

Replace `APPROVED_COMMIT` with the approved full OID. If signing is unavailable,
explicitly choose and record `git tag -a` instead of `git tag -s`; do not silently
retag, force-push, or change signing configuration. Ensure the approved default
branch commit/workflow is already published before pushing the tag.

`.github/workflows/release.yml` tests the exact tag on Python 3.10/3.12/3.13 and
validates the board with full history. Only after all pass does the release job
prepare notes and versioned source archives and smoke-test both formats. It
creates a draft, uploads assets, then publishes as latest/non-prerelease. Reruns
update the same release and replace only the two generated assets. Validation
has read-only permissions; only the release job has `contents: write`, using
the standard `GITHUB_TOKEN`. Actions are pinned to reviewed commit SHAs. Never
move a published tag: correcting a release's code requires a new version.

### Manual fallback

Only use this after the exact tag's matrix/board checks have passed, with explicit
publication authorization. In a full-history checkout at that annotated tag:

```sh
assets=$(mktemp -d)
python3 .github/scripts/prepare-release.py v0.1.0 --output "$assets"
bash .github/scripts/smoke-release.sh v0.1.0 "$assets"
GH_REPO=gbosiger/worktree bash .github/scripts/publish-release.sh v0.1.0 "$assets"
```

The scripts use GitHub CLI's `gh release create --verify-tag --draft`,
`gh release upload`, and `gh release edit`. Preparation/smoke checks are local;
only the last script publishes. A failed upload can be retried without creating
a duplicate release. Inspect existing assets before intentionally replacing them.

## Verify the published release

Clone with complete history, then detach at the tag (do not use `--depth`):

```sh
git clone https://github.com/gbosiger/worktree.git release-check
cd release-check
git checkout --detach v0.1.0
python3 -m unittest discover -s tests -v
./work --root . check
assets=$(mktemp -d)
gh release download v0.1.0 --repo gbosiger/worktree --dir "$assets" \
  --pattern 'worktree-tickets-*'
bash .github/scripts/smoke-release.sh v0.1.0 "$assets"
```

Compare each extracted asset's file contents, executable bits, and symlink targets
with `git archive v0.1.0`; archive container bytes can differ by compression tool.
Check the release page's first/latest status, non-prerelease flag, notes, assets,
tag commit, changelog date, and successful tag workflow run. Record this evidence
in the publication and final verification tickets; only then accept the epic.

## Install from a source asset

On Unix-like systems, prefer the versioned `.tar.gz`; `tar -xzf` preserves
executable bits and symlinks. ZIP users should extract with a Unix-compatible
`unzip` (not Python's `zipfile.extractall` or an extractor that flattens links).
Run the extracted `./work --version`, then `./work install /path/to/project`.
Review and commit `.workkit/`, `.work/`, `.agents/skills/`, `.opencode/commands/`,
and the AGENTS.md addition. Python 3.10+ and Git are needed for Git workflows.

Source archives contain no `.git` history. They support installation into a fresh
project, but cannot resolve archived development tickets: do not expect the
bundled dogfood board's `work check` or historical `show` to work without history.
Initializing a new Git repository does not restore missing archives. Use the
full-history clone above for development-board and released-commit verification.
