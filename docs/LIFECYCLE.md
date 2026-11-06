# Lifecycle and acceptance

`backlog -> wip -> review -> done`. Review can return to WIP with `start`.
`reopen` returns a WIP, review, or done item to backlog. Reopening completed work
reopens completed ancestors to WIP, preserving historical acceptance records.
Add a new acceptance record when the item is completed again.

The CLI moves files between status folders inside their parent. Moving a
container carries all descendants without changing their statuses. Starting a
parent does not start its children. Children being complete does not accept
their parent: each level needs explicit acceptance, and a completed container
must have all its children complete. Use `show ID` to locate tickets after moves
and `list --status review` to find review work across containers.

## Dependencies

Starting/advancing requires explicit dependencies to be done. Completion
prerequisites must be acyclic, including both explicit dependencies and the
requirement to complete a container's children. A child cannot depend on its
own parent, even indirectly. Parentage describes scope, not execution order.
Work inside a backlog parent can start; parent status is deliberate.

Reopen completed dependents before their prerequisites, including any completed
ancestor that would also reopen. Reopen rejects affected completed dependents
before writing, including in dry runs.

## Acceptance gate

`done` requires review status, checked acceptance items, a recorded reviewer,
`--by` matching that reviewer, and nonempty `--evidence`. The CLI recognizes
unchecked list items using `-`, `*`, `+`, or numbered markers such as `1.` and
`1)`, including indented items. Checked items use `[x]` or `[X]`.

This records an assertion, not authenticated identity or proof that a test
passed. Humans and agents remain responsible for accurate evidence. Do not
auto-check criteria. A script cannot judge the value or completeness of a spec.

## Human–agent handoff

Read the selected ticket, ancestor READMEs, explicit dependencies, and relevant
code/docs, not the whole archive. Establish unset implementer/reviewer roles
once with `assign`; honor agreed ownership without repeated questions.

Implementation ends with evidence and a handoff into review. Review checks
scope, acceptance criteria, tests, and documentation. Record limitations and
return to WIP when needed. The reviewer can be another agent if agreed; separate
human review is not universally mandatory. Never invent another person's review
or accept on their behalf.

Individual writes are atomic; multi-file moves are not transactional. After an
interruption, repair any path/status mismatch and run `check`.
