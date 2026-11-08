---
{
  "id": "T-5079b576",
  "kind": "task",
  "title": "Review the convention and human-agent handoffs",
  "status": "done",
  "parent": "E-1a88a55f",
  "depends_on": [
    "T-663511bc"
  ],
  "implementer": "agent",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Review the convention and human-agent handoffs

## Purpose and scope

Make the final human release-readiness decision on the convention and agent
handoffs after archive implementation and automated verification. This is a
review of the combined toolkit, not another implementation or test task.

## Acceptance criteria

- [x] Review CONVENTION.md and its linked format, authoring, lifecycle, Git, and installation rules for consistency with the implemented toolkit.
- [x] Read the canonical work-execute skill and decide whether its branch checks, ancestor-start sequence, and dirty-work safeguards are clear enough to follow.
- [x] Confirm that implemented queues, retained done records, post-merge cleanup, reviewer ownership, and acceptance evidence are understandable; record approval or concrete findings.

## Evidence to use

T-060729db verifies retained commits and merge/cleanup; T-663511bc verifies the
end-to-end workflow; T-d190ce5e verifies maintained docs. T-341cb396 reconciles
this checklist and closes the CI/preview audit findings; wait for its review.
The canonical work-execute skill replaces removed lifecycle slash prompts.
Tests establish technical behavior, not your judgment that the guidance is usable.

## Handoff

Human implementer/reviewer; agent may prepare evidence or fixes, not accept on
the maintainer's behalf. Review after T-663511bc; record findings and resolve
blocking issues before completion. This checklist update records no human review,
approval, or publication and leaves ownership/status unchanged.

## Review

* FORMAT.md has legacy content. This is not needed it is a first epic so tool is not in use yet. And we do not care if there are some older commits in the old format.
* Handling of groups should be functional as epics with all the features they cover - created T-7ff2dcbf for this.
* work-execute skill - I think there are some instructions that the script could take over, like checking if we are on a git repo and for consistency. By instructing LLMs to do this all the time burns tokens. Create a ticket for this. Consider other places like that.




## Acceptance record

2026-11-08T12:58:51+00:00 — human: N/A
