# Write a ticket someone can pick up

Give the ticket a title you could use to ask a colleague for the work.
Open with who needs what and why. For a task, name the thing the assignee
will deliver and the decision or action it enables.

Under `## Acceptance criteria`, put one observable result on each checkbox.
Use a real example when the rule is easier to see in action. For a human
review, say what to inspect and what decision to make. Give a behavior its own box when a reviewer needs to accept it
independently. Put variations that exercise the same outcome in a short
verification note. For example, preserving a draft on cancellation is one
outcome. Trying it with a new draft and an edited draft gives two ways to
verify it. Link the shared test matrix when several tickets use it. Check a box only when evidence supports it.

> **Open a ticket after it moves**
>
> A Neovim user can leave the picker open while a teammate moves a ticket
> into review.
>
> - [ ] Selecting the old result opens the ticket at its new location.
> - [ ] If the ticket was deleted, the picker explains what happened.

## Prepare at the right level

**Epic.** Explain the problem as it exists today, who encounters it, and what
will change for them. Draw the boundary where a reader could reasonably expect
more. Describe a first useful increment and the later capabilities it enables.
Use a demonstration across the feature as the acceptance check. For example,
a Neovim epic might start with finding and opening a live ticket, add ID
completion, then let a reviewer act on the ticket from its buffer. Archived
ticket browsing would be a separate scope decision. Keep the sequence flexible
as you learn. [Atlassian’s guide to epics](https://www.atlassian.com/agile/project-management/epics)

**Story.** Describe the person, the situation that triggers the need, and why
the result matters. Prefer a slice someone could use on its own. Walk through a
representative case and the exception that would most surprise that person.
For the picker example above, “search by title and open the result” is a
demonstrable slice. “Build the search index” is a supporting task if it needs
its own deliverable. [GOV.UK’s guide to user stories](https://www.gov.uk/service-manual/agile-delivery/writing-user-stories)

**Task.** Identify the output, its consumer, the inputs they already have,
and how the recipient can inspect the result. Bound open-ended research by
the decision it must support. For example, “Decide how to identify a moved
ticket” could deliver a short design note showing how lookup by ID behaves
after a move and a deletion. Those two examples tell the reviewer when the
investigation has answered its question. When downstream work needs an agreed
choice, write the acceptance criterion from the consumer’s perspective:
“The design note names the selected lookup key and shows how to use it after
a move.” A reviewable proposal is a useful intermediate result. Keep the
decision criterion open until the choice is recorded. If deferred, name the
blocked consumer tickets in the handoff. [Bill Wake on INVEST stories and SMART tasks](https://xp123.com/invest-in-good-stories-and-smart-tasks/)

**Group.** Explain why the member epics belong together and what the combined
release must demonstrate. Record a dependency when work truly must wait for
another ticket's result. The board already lists member tickets.

## Refine before picking up work

An early backlog idea can carry an open question. As it approaches execution,
try explaining the assignment to the next person using just the ticket. Can
they tell what happens today, where the change ends, and what example would
convince the reviewer? Add the missing rule or example there. If two outcomes
can ship separately, consider splitting them. If a choice changes the size
or acceptance of the work, record who needs to decide and what it blocks.
Use a linked requirement for the full rule set. Replace template prompts and
drop inapplicable examples when preparing the ticket.

## Decide what goes where

Keep the goal, acceptance checks, and any decision blocking this assignment
in the ticket. Link to a specific section of the project's maintained docs
for shared requirements, design choices, or a test matrix. Label proposed
behavior as planned until it ships. Mention exclusions only when someone
might reasonably do the wrong work. Use ticket IDs for related work.

## Leave a handoff when there is work to resume

Before pausing, changing owners, or requesting review, update the ticket's
`## Handoff`. Give the next person the current result, where to inspect it,
what you actually checked, any blocker or untested case, and their next action.
Include branch/worktree context for work in progress. Before carrying a prerequisite into the handoff, check its current status
with `work show ID`. Replace stale directions.
A backlog ticket usually needs no handoff until a real decision or finding
changes where to start.

For example: “The picker now follows moved tickets in the checkout on
`feature/picker`. The headless move test passed. Deletion is still untested.
Next implementer: delete a result while the picker is open and check the
message.” Use repository paths or reproducible commands for evidence.
Keep the current resume instructions in the ticket so they survive the
loss of chat history, scratch files, or a session-specific directory.
