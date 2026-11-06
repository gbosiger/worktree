# Contributing

Keep the default workflow useful for a solo maintainer using an editor and Git.
Discuss format/lifecycle changes through an epic before adding machinery. Prefer
small behavior increments and standard-library Python. Document compatibility
changes and preserve unknown metadata fields and existing project instructions.

Add regression tests for meaningful file mutations, validation, installation, and
lifecycle behavior. Run the test suite and dogfood board validation. Do not commit
cache files, local lock directories, generated archives, or secrets.

Use `./work --help` for commands. Read only relevant references from the
CONVENTION.md index. Historical changes belong in CHANGELOG.md and upgrade
instructions in docs/MIGRATIONS.md, not ordinary skill context.

Use the .work board for substantial changes. Commit messages retain the item ID.
Bug reports and public contributions may also use GitHub issues/PRs; maintainers
can translate accepted work into local tickets without requiring every visitor
to learn the system first.
