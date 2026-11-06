# Changelog

## Unreleased

- Project-local OpenCode shortcuts for ticket creation, browsing, lifecycle,
  assignment, and dependencies; canonical templates are linked, not duplicated.
- Repository skill discovery uses relative links to canonical sources, including
  installed projects' `.workkit/skills/`, rather than duplicate skill files.
- Executable `work` launcher and explicit command setup; copied projects include
  their own launcher.
- Focused references replace the monolithic convention. Repository skills load
  only operation-relevant references. Migrations and historical notes are separate.
- Shorter, example-led introduction; commit-message archiving is identified as
  planned rather than presented as an available command.

## Draft v0.2.0

- Child status folders inside epics and groups replace the flat child layout.
  See [migration instructions](docs/MIGRATIONS.md).
- Reopening preflights completed dependents of affected ancestors.
- Cycle validation includes parent/child completion prerequisites.
- Completion recognizes unchecked bullet and numbered Markdown checklist items.

## Draft v0.1.0

- Initial Markdown convention, lifecycle CLI, templates, repository skills,
  copy-based installation, and workflow regression tests.
