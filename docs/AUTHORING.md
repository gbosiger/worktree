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

## Write for the assignee

Use plain language and explain necessary technical terms. Each acceptance item
should describe one clear outcome or decision, not a bundle of implementation
details. For a review, identify what to read or try, where to find it, and what
the reviewer must decide. Name prerequisite reviews by ID and readable title.

Separate human judgment from agent verification. The agent should prepare a
short evidence summary with links, results, and limitations; the human should
not have to decode logs or carry out unexplained specialist checks. Keep
technical safeguards and authorization limits in verification/handoff notes or
linked documentation rather than overloading the human checklist.

For example, replace "Verify remote revision parity and archive provenance"
with "Review the agent's evidence that GitHub contains the version you approved."
Put the version comparison and archive-preservation checks in the agent's
verification instructions, and identify any evidence still missing.

Before handoff, ask whether the assignee can understand the next action and
success condition without a translation. Fix the ticket itself if not. Rewriting
a ticket does not approve its work or justify checking its criteria.
Use IDs for references rather than paths that will change with status moves.
