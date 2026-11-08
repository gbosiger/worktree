---
{
  "id": "T-0e7c2a61",
  "kind": "task",
  "title": "Link repository skills to canonical sources",
  "status": "done",
  "parent": "E-1a88a55f",
  "depends_on": [],
  "implementer": "agent",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Link repository skills to canonical sources

## Purpose and scope

Eliminate duplicate repository/discovery skill files while keeping installed
projects self-contained and preserving custom skills on installation conflicts.

## Acceptance criteria

- [x] Toolkit discovery entries link to canonical skills/ directories using relative links.
- [x] Installed discovery entries link to the local .workkit/skills/ copy, not the toolkit checkout or a global installation.
- [x] Editing canonical installed skills is immediately reflected by discovery links, which remain valid after relocation.
- [x] Installation preserves conflicting custom skills and dangling links without partial toolkit writes.
- [x] Documentation describes the single-source model and safe migration; tests and board validation pass.

## Approach and decisions

Compare all existing source/development skill pairs before replacing only the
verified duplicates. Use relative directory symlinks so full skill directories
(including future resources) have one source of truth. Keep canonical files in
skills/ for development/export and .workkit/skills/ for installed projects.
Test discovery readability, local edit propagation, project relocation, and
conflict refusal. No personal/global skill installation or Git operations.

## Verification

- All three existing discovery/source pairs were byte-identical before removing
  the duplicates. Only their verified duplicate SKILL.md files and empty parent
  directories were replaced with links.
- `python3 -m unittest discover -s tests -v`: all 24 tests pass.
- `./work --root . check`: all 8 tickets validate.
- Tests verify relative links, shared canonical files, discoverable SKILL.md
  paths, installed edit propagation, relocation, and refusal of custom/dangling
  skill or toolkit conflicts. OpenCode rediscovered all three linked skills.
- No personal/global installation or Git changes were performed.

## Handoff

Ready for human review of work.py installation, repository discovery links,
regression tests, and the single-source documentation/migration instructions.
Find this task in the epic's review/ folder via `./work show T-0e7c2a61`.
No human acceptance, commit, or publication is claimed.

## Acceptance record

2026-11-06T19:19:31+00:00 — human: The maintainer clarified in this conversation that moving these existing tickets to done was their approval, and requested staging, committing, and archival. This records that current confirmation for this already-done ticket; earlier handoff prose is retained as historical evidence, not backdated or replaced. No additional human test run is claimed.
