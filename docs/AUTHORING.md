# Writing useful work

Epics explain the beneficiary, outcome/value, included and excluded scope,
observable acceptance criteria, dependencies, and open questions. Prefer
independently useful features; record unavoidable dependencies explicitly.
Do not nest epics merely because one needs another. Use a group only for a
shared larger outcome.

Stories describe small behavior increments with concrete acceptance examples,
including material failure and edge cases. Split by behavior/value by default.
Use supporting tasks for substantial research, implementation, testing,
maintenance, or review deliverables when a real handoff warrants it; four phase
tickets are never mandatory. Small fixes can use tasks in a maintenance epic.

Keep tickets concise. Record decisions and handoff summaries, not chat
transcripts, raw logs, or binaries. Put lasting architecture and user guidance
in maintained documentation and reference it from the ticket. Completed tickets
describe history, not necessarily current behavior.

Templates under `templates/` provide the headings. Replace placeholder criteria
with verifiable outcomes; do not auto-check criteria or invent reviewer approval.
Use IDs for references rather than paths that will change with status moves.
