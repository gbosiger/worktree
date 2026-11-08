---
{
  "id": "S-56c90e4f",
  "kind": "story",
  "title": "Record ticket state changes for later timeline playback",
  "status": "backlog",
  "parent": "E-f44b10c1",
  "depends_on": ["T-f7d4aef3"],
  "implementer": null,
  "reviewer": null,
  "branch": null,
  "base_branch": null
}
---
# Record ticket state changes for later timeline playback

## Required behavior and value

People reading stories and epics can inspect a timestamped record of actual state
changes. Future tools can replay those events using the contract defined by
T-f7d4aef3 — Define a timestamped ticket state history format.

## Acceptance criteria

- [ ] Implement the agreed state-history section for stories and epics, and tasks/groups if included by T-f7d4aef3; existing prose and unknown metadata are preserved.
- [ ] Successful start, review, acceptance, commit, and reopen changes append events with the agreed previous/next states, timestamp, and ordering rules.
- [ ] Automatic ancestor state changes are recorded on those ancestors; moving a container does not falsely record a transition for unchanged descendants.
- [ ] Dry runs, rejected operations, and no-op calls create no events. Failure/rollback tests demonstrate history consistent with the states actually persisted.
- [ ] Prior events and acceptance evidence survive repeated review/reopen cycles, retained done commits, archive cleanup, and restoration from archive.
- [ ] Tickets without historical logs still work; recording begins according to the agreed initial-state rules without inventing earlier transitions.
- [ ] Tests cover timestamp ties/order, malformed sections, manual-edit expectations, and every supported ticket kind according to the agreed contract.
- [ ] Format, lifecycle, and migration guidance describe the implemented behavior and limitations for future timeline consumers.

## Approach and decisions

Follow the reviewed contract from T-f7d4aef3. Inspect all status writers, including
reopen restoration and commit/merge preparation, rather than instrumenting only
`transition()`. Preserve acceptance validation and archived record compatibility.
Do not add playback UI, infer unrecorded events from Git, or treat clocks as proof
of causal order beyond the agreed event-order rule.

## Verification

Use controlled-clock tests and temporary Git repositories for commit, merge,
archive, reopen, and injected failures. Compare recorded histories with actual
states and verify existing acceptance/archive regression tests still pass.

## Handoff

Backlog; blocked on T-f7d4aef3. No timestamp format or recording implementation
is claimed by preparation.
