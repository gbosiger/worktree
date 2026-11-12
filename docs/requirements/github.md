# Planned GitHub pull requests

Maintainers can publish selected tickets through pull requests while local board operations continue to work offline. These requirements describe proposed GitHub behavior. The current local archive contract is in [Git workflow](../GIT.md#reading-deleted-tickets-and-reopening-parents).

## Publication decisions

Agree on CLI and OpenCode command names, authentication, minimum permissions, and which explicit actions authorize pushes, comments, review, cleanup, or merge. Decide how to select a repository/remote, handle grouped epics and unexpected defaults, and identify a ticket revision. Choose where archive comments live, how managed text is marked, and how large records are preserved. Define checks for public-content suitability and a recoverable refusal for prohibited content. Keep credentials out of output.

The earlier proposal requested full ticket records in squash messages at both merge levels plus comments on GitHub. The released local reader requires committed files in reachable history. Resolve this difference with the maintainer before building remote cleanup or merge. Demonstrate offline lookup, dependencies, and reopening from a fresh default-branch clone, including children landed earlier. Specify supported merge methods, edited messages, branch policies, queues and auto-merge. Refuse configurations that could lose approved records.

## Opening pull requests

A task/story batch contains only explicitly selected, accepted done items from one epic. Target its recorded feature branch even with unfinished siblings. An epic PR targets the repository's actual default branch under the agreed grouping policy. Resolve ambiguous remotes/targets and confirm unexpected defaults. Allow a draft while work continues.

Preview the targets, IDs, and local and remote writes. Create or update one matching PR. Reconcile closed, reopened, merged, or conflicting candidates before retrying. Update only managed text with ticket IDs, scope, criteria, evidence, source revision, and visible AGENT attribution. Preserve human discussion and unrelated working/index changes.

## Readiness and merge checks

An epic can become ready after its own backlog clears, children and dependencies finish, and the epic is accepted. Ignore unrelated backlog. Recheck the current PR head, required checks, and reviews. Explain each blocker. Repeating readiness is safe and promotion never merges. Recompute gates immediately before merge, including after reopened work, a changed head, or a cleanup commit. A task merge can proceed alongside unfinished siblings.

## Archive and cleanup

Publish complete, attributed managed comments keyed by ticket and revision. Preserve oversize records in full or stop before removal. Verify the durable Git record before deleting only eligible paths on the selected PR branch. Reuse already archived children. Epic cleanup must include earlier merged children in the final recoverable history. Preview comments, records, paths, commits, and exact proposed messages. Report completed and pending actions on failures so a retry after partial publication avoids duplicates.

## Merging

Preview the exact archive-preserving merge on each branch. Validate the approved record and supported merge policy instead of trusting GitHub's generated squash message. Missing or modified records block the operation. After cleanup commits change the head, require fresh checks and required reapproval. Reconcile uncertain network outcomes and already-merged PRs before retrying. Keep recoverable state on a conflict or permission failure.

## Agent review

Use the authenticated user's identity. An assigned agent reviews the actual head and publishes findings and checks with a visible AGENT label, ticket IDs, and reviewed revision. A human-owned review stays with its reviewer. Where formal self-review is unavailable, publish advisory comments and identify outstanding independent approval. Preview publication, deduplicate per ticket/revision, and reject stale heads. A failed remote action cannot imply local acceptance.

## Optional pre-merge workflow

Preview installation and preserve existing workflows and branch protections. Validate the repository, head, ticket IDs, and scoped paths. Never run untrusted PR code with write credentials. Refuse unsafe forks or permissions. Cleanup must land before merge and trigger checks on the new head. State which protection settings enforce the process for UI merges and which configurations are unsupported.

## Verification

Use fakes and disposable repositories for both merge levels, installed commands, changed heads, retries, partial cleanup, forks, insufficient permissions, secret/size refusals, and reapproval. Test offline recovery from a normal clone and safe refusal with missing/shallow history. Exercise canonical OpenCode links and literal arguments. Document tested permissions, protection settings, recovery, CLI help, and local-only use. Automated checks need no remote writes.
