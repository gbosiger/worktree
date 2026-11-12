# Planned terminal workflows

These are backlog requirements for Bash completion, ticket history, and two explicit lifecycle shortcuts. The current CLI behavior is described in [Lifecycle](../LIFECYCLE.md) and [Git workflow](../GIT.md).

## Bash completion

Support opt-in setup and removal in a checkout and an installed project. Document supported Bash versions. Leave startup files under user control. Complete subcommands, options, fixed values, and ID prefixes. Discover the nearest ancestor board, including nested boards, or honor an explicit quoted `--root` in supported positions.

For start, suggest backlog and review IDs. For review, suggest WIP. For done, suggest review unless the direct-acceptance option is selected. For commit, suggest implemented IDs excluding prior selections. Document kinds, statuses, self-exclusion, and archive support for show, reopen, assign, depend, create --parent, and merge. Identify checks deferred to the CLI, including reviewer/evidence and races. Suggestions never grant permission.

Read the board without running transitions, evaluating shell data, contacting a remote, or scanning all Git history on each keystroke. Set an interactive latency target and decide how archived IDs participate. Missing/invalid boards and unavailable history should yield quiet, safe results. Test quoted paths, multiple roots, prefixes, and moves between attempts.

## History format

Design a separate, editable Markdown section associated with the immutable ID. Specify event syntax, versioning, timezone and precision (UTC proposed), and stable order for tied or backward clocks. Decide how to represent creation and which kinds besides stories and epics use the log. Distinguish missing history from a known initial state.

Give examples for start, return from review, acceptance into implemented, commit into done, archive restoration, and reopening accepted ancestors. Container moves alone do not change descendant states. Describe malformed logs, manual edits, older tickets/toolkits, and incompatible draft changes. Keep existing acceptance evidence valid. No reconstructed timestamps or playback UI.

## Recording transitions

Append events only for actual persisted state changes, including automatic ancestor changes. Dry runs, refusals, and no-ops leave history untouched. Account for partial multi-ticket operations, commit rollback, and recovery. Preserve unknown metadata, prose, prior events, and acceptance records through repeated review, commit, final integration, and reopen. Test older tickets without logs, every supported kind, ordering, and failure injection.

## Direct acceptance from WIP

Choose explicit opt-in syntax, eligible kinds, and noninteractive behavior. The motivating case is a completed review task. Ordinary acceptance still requires review status. Warn which ticket and review handoff will be skipped and require affirmative confirmation. Refusal, empty input, cancellation, and EOF leave the ticket untouched. Noninteractive use must neither hang nor silently confirm.

Revalidate the ticket after prompting. Require checked criteria, matching assigned reviewer, evidence, dependencies, and accepted children. Record normal acceptance evidence and the actual WIP-to-implemented event. Preview describes the pending confirmation without a write. Cover completion only in the opt-in context and retain explicit review authorization in agent guidance.

## Branch setup on start

Offer an explicit local setup-and-start operation for backlog epics and groups. Choose its syntax before implementation. Present proposed branch and base when unset, honoring recorded values and resolving ambiguity. Use the actual default branch when proposing a standalone base. Create from the selected base or check out the existing branch without resetting it. Reuse the current branch when appropriate. Re-read the board after switching before writing metadata or starting the container.

Start a group on its chosen base, then its epics on distinct branches based on the group's recorded branch. Starting one leaves its siblings and WIP group alone. Explain missing group branches and blocked ancestors/dependencies. Only successful setup records actual targets and starts the selected item. Plain starts, review returns, leaf tickets, and other status commands keep their existing behavior.

Preview branch, metadata, and status changes without changing files, index, refs, or objects. Refuse dirty work, detached HEAD, missing bases, other-worktree conflicts, and non-Git requests. Report partial Git results and safe recovery if a switch or write fails. No automatic stash, relocation, worktree creation, fetch, commit, publication, merge, or branch reset/deletion. Cover option completion and history for success and refusal.

## Python module layout

While implementing completion and history, compare the code needed to find candidates, trace state writes, and verify archive preservation. Estimate relevant lines/bytes or measure tokens and account for imports and cross-file navigation. Extract a cohesive responsibility only when the reading and maintenance savings justify the change. Record the decision and a short code map if files move. Verify launcher, installer, imports, and CLI behavior in both layouts as applicable.

## Verification

On disposable boards, walk through Bash setup, nested directories, explicit roots, refreshed suggestions, review returns, acceptance, commit, and archive reopening. Exercise ordinary and opt-in acceptance and branch setup, including two sibling epics, existing branches, cancellation, and recovery. Check read-only actions leave history untouched. Record supported versions, commands, limitations, full suite and board-check results.
