# Changelog

All notable changes are documented here, following Keep a Changelog.

## Unreleased

## 0.1.0 - 2026-11-08

### Added

- Editable Markdown groups, epics, stories, and tasks, with child status folders,
  explicit dependencies, implementer/reviewer ownership, and acceptance evidence.
- A dependency-free Python 3.10+ CLI for creating, finding, validating, and moving
  tickets through backlog, WIP, review, implemented, and done.
- Scoped work queues: `work list` finds the current branch's epic;
  `--epic`, `--all`, `--status`, and computed `--ready` select other queues.
- Read-only `work preflight` checks execution branches, ancestor/dependency gates,
  ownership, and dirty paths before implementation or commits.
- Reviewed ticket commits retain done records. Epic/group integration preserves
  them before a separate final-base cleanup; journals support interrupted commits
  and merges without rewinding progress. Push remains explicit.
- Git-native archived-ticket lookup and reopening, including missing parent
  chains, squash-safe integration, and batched history reads.
- Copy-based project installation, an executable launcher, explicit PATH setup,
  project-local agent skills, and linked OpenCode ticket-preparation commands.
- Focused authoring, lifecycle, Git, installation, and contribution documentation,
  workflow regression tests, and an archive-history benchmark.

### Compatibility

- This first public release consolidates the unpublished 0.1.0/0.2.0 drafts.
  `work list` defaults to the current epic's backlog stories/tasks; use
  `work list --all` for the complete live board.
- The supported archive is committed accepted ticket files in Git history.
  Prototype message-only archives and automatic board conversions are unsupported;
  commit messages do not substitute for retained ticket content.
- Acceptance is explicit and review-gated; neither a script nor a parent status
  automatically accepts children. Git setup, integration, and publication require
  authorization. No mandatory service or third-party Python package is required.
