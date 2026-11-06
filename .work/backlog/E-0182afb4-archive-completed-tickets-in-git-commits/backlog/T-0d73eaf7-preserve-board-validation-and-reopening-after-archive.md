---
{
  "id": "T-0d73eaf7",
  "kind": "task",
  "title": "Preserve board validation and reopening after archive",
  "status": "backlog",
  "parent": "E-0182afb4",
  "depends_on": ["T-7147e599"],
  "implementer": "agent",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Preserve board validation and reopening after archive

## Purpose and scope

Make archived tickets usable by existing board operations before an archive
writer can remove files. Preserve current acceptance and reopening rules.

## Acceptance criteria

- [ ] show resolves an archived ID and displays its complete record with archive provenance instead of claiming it has an active file path.
- [ ] check, dependency validation, cycle detection, and ID allocation account for archived records; missing evidence is not treated as completion and archived IDs are not reused.
- [ ] Containers can complete with accepted archived children, but archiving a child neither accepts its parent nor hides active descendants.
- [ ] reopen restores archived content to the correct backlog location with the same ID, unknown metadata, and historical acceptance; restore required ancestor structure without overwriting active files.
- [ ] Completed ancestors reopen to WIP as required, completed dependents still block reopening, and dry runs leave files/index/history unchanged.
- [ ] Regression tests cover mixed active/archived descendants, grouped epics, restored ancestors, collisions, dependencies, and repeated reopen/accept/archive cycles.

## Approach and decisions

Integrate T-7147e599 with records/get/check/create/transition behavior in work.py.
Do not weaken the explicit reviewer/evidence gate or introduce implicit Git writes.

## Verification

Exercise existing lifecycle tests plus disposable histories containing archived
tasks and containers. Run the full unit suite and board check.

## Handoff

Document restoration behavior and unresolved recovery limits for human review.
