---
{
  "id": "T-10e609cd",
  "kind": "task",
  "title": "Assess and selectively split Python code for agent-efficient maintenance",
  "status": "backlog",
  "parent": "E-f44b10c1",
  "depends_on": [],
  "implementer": null,
  "reviewer": null,
  "branch": null,
  "base_branch": null
}
---
# Assess and selectively split Python code for agent-efficient maintenance

## Purpose and scope

Assess whether splitting the growing `.work/tools/work.py` into a few cohesive
modules would make completion/history work and later agent maintenance cheaper
to understand. Implement only a focused split with a credible net benefit;
retaining the current structure with a documented reason is a valid outcome.

## Acceptance criteria

- [ ] Compare the current layout with a small candidate split using representative tasks: finding completion candidates, tracing state writes, and checking archive preservation.
- [ ] Record which code an agent would need to read in each layout, approximate lines/bytes or measured tokens, and cross-file navigation/import overhead. Distinguish estimates from measured results; exact token benchmarking is not required.
- [ ] Decide whether reduced relevant context and clearer ownership outweigh restructuring effort, import indirection, and extra files. Do not split solely because the file is large.
- [ ] If beneficial, extract only cohesive responsibilities needed by this epic, with clear imports and no duplicated logic, speculative framework, or mandatory external dependency.
- [ ] If a split is made, verify checkout and installed launchers, setup/install copying, test imports, and existing CLI behavior. Run the full unit suite and board check and record outcomes.
- [ ] If no split is justified, record why and leave the layout unchanged; neither feature is blocked by a requirement to refactor.
- [ ] Provide a short code-location map for any new boundaries so future agents can find the relevant implementation without preloading all modules.

## Approach and decisions

Assess during S-5299cba3 (Bash completion) and S-56c90e4f (state history), once
the touched responsibilities are clear. Avoid a stand-alone architecture project
or broad unrelated cleanup. Inspect launcher, installer, and tests before moving
code: preserving distribution and import behavior matters more than file count.
Separate mechanical moves from behavioral changes where practical for review.

## Verification

Summarize representative reading paths, estimated context savings, and navigation
costs. For an actual split, provide regression results and a temporary-project
installation smoke test. Do not claim token savings from file size alone.

## Handoff

Backlog assessment with conditional implementation, not authorization to begin
refactoring now. Branch/base and roles follow the epic's execution preflight.
Pass the decision and any changed code locations to T-6bab2842 for final verification.
