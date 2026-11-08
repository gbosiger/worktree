---
{
  "id": "E-54e9139e",
  "kind": "epic",
  "title": "Integrate GitHub pull requests with ticket lifecycle",
  "status": "backlog",
  "parent": null,
  "depends_on": [
    "E-1a88a55f"
  ],
  "implementer": "agent",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Integrate GitHub pull requests with ticket lifecycle

## Outcome and value

Maintainers and agents publish task and epic work through GitHub pull requests
using short CLI/OpenCode requests. Accepted work leaves the active board only
after its content is safely archived. GitHub retains readable discussion while
the default branch has a clean feature-level history with recoverable task IDs
and content.

## Scope

Included:

- Explicit CLI operations and matching OpenCode shortcuts to create/update PRs,
  check readiness, publish assigned agent reviews, and perform authorized merges.
- Task/story PRs into their epic's feature branch; epic PRs into the repository's
  detected default branch, including main or master.
- PR descriptions reflecting ticket content; task archive comments; durable Git
  archive records; an opt-in pre-merge cleanup workflow/action.
- Draft PRs while epic work continues, with an idempotent readiness operation.
- The authenticated user's identity, with clearly labelled agent-authored output.

Excluded:

- Making GitHub mandatory for local work, inventing acceptance, bypassing branch
  protection, or treating agent-labelled output as an independent human review.
- Unrequested pushes/merges, unrelated ticket cleanup, replacing Git identity or
  global configuration, or executing untrusted PR code with write credentials.
- Other hosting providers and implicit installation of workflows/protection rules.
## Acceptance criteria

- [ ] CLI and OpenCode operations select an explicit epic or done task/story and create or update the matching PR without duplicates on retries. Preview mode reports targets, selected IDs, remote writes, cleanup, and merge messages without mutating local or remote state.
- [ ] Task PRs target the recorded epic feature branch. Epic PRs target the selected repository's actual default branch rather than guessing main/master. Ambiguous repositories, remotes, or branches require clarification; unexpected default branches are surfaced for confirmation.
- [ ] A task batch selects only explicitly scoped, accepted done items for that epic. Backlog/WIP/review children and unrelated epics remain untouched. Other unfinished children do not prevent completed tasks from merging into the feature branch.
- [ ] Epic merge is blocked if that epic's backlog contains work; unrelated repository backlog is irrelevant. Existing completion gates also apply: no unfinished children/dependencies, explicit epic acceptance, and required GitHub checks/reviews satisfied.
- [ ] An epic can have a draft PR before completion. A readiness operation rechecks the selected epic and current PR head before marking it ready for review; repeating it is safe and never merges. All gates are checked again at merge time, including work added or reopened after readiness.
- [ ] PR descriptions reflect the selected ticket definitions, including IDs, scope, criteria, and verification/acceptance evidence. Updating them preserves user-authored discussion outside clearly marked managed sections and identifies the source revision.
- [ ] Each task merge publishes a managed GitHub archive comment containing its ID and complete ticket record, and preserves that record in the feature branch's Git commit message. The corresponding file is removed only after archival is verified and cleanup is included in the merged PR head.
- [ ] Before epic merge, the workflow verifies durable archive records, archives the epic content, and commits only eligible ticket removals onto the PR branch. New cleanup commits trigger fresh checks and any required reapproval; a post-merge action is not used to pretend files were removed before merge.
- [ ] The recommended merge policy is squash task PRs into the epic and squash the epic into the default branch. The final epic commit includes its ID/full record and all task archive records, including tasks merged earlier, so squash cannot discard task history. GitHub comments supplement rather than replace the Git archive, and lookup/dependencies/reopening work from a normal clone without GitHub access.
- [ ] Never rely on GitHub's automatically generated squash message to retain archive data. Generate and preview the archive-preserving message explicitly; detect missing/altered records and block the tool's merge rather than silently lose history. Unsupported merge methods/policies produce actionable errors instead of falling back silently.
- [ ] GitHub writes use the user's authenticated identity. Agent-generated PR sections, comments, and reviews have a consistent visible AGENT marker and ticket/revision attribution. Do not expose credentials or alter authorship to imply a different authenticated reviewer.
- [ ] After opening a PR, an assigned agent reviewer performs a real review of that head and publishes labelled findings and actual verification evidence. It does not post a canned approval or claim human review. A human-assigned review is not silently replaced by an agent review.
- [ ] If the user's identity also authored the PR, agent findings are published as advisory comments when formal self-review is unavailable. They do not count as independent approval or bypass required GitHub reviewers; blocked merges explain the missing approval.
- [ ] Archive comments/reviews/cleanup are idempotent per ticket and revision. On authentication, permission, network, comment-size, cleanup, or merge failure, preserve recoverable ticket content and report completed versus pending actions. Never delete unarchived records or overwrite unrelated local/index changes.
- [ ] An explicitly installed pre-merge workflow handles only validated scoped paths and does not execute untrusted PR code with write credentials. Document required branch protection/check setup; the tool must not claim arbitrary UI merges are protected when repository enforcement is absent.
- [ ] Regression/integration tests cover the scenarios below; focused documentation, CLI help, linked OpenCode commands, and recovery guidance describe actual behavior. No real publication is required by automated tests.

## Stories and dependencies

Depends on E-1a88a55f (the initial toolkit, including local commit archiving). Reuse its
machine-readable records, identity resolution, dependency handling, and reopening
instead of creating a second incompatible archive format. This epic adds remote
PR/review/cleanup orchestration; the local archive command does not push.

Backlog tasks:

1. T-8818c75d — Define GitHub operation and publication contract (after E-1a88a55f).
2. T-dc9a8fcd — Create and update scoped ticket pull requests.
3. T-266c67e6 — Recheck epic readiness and merge gates.
4. T-e769d578 — Publish archive records and prepare safe PR cleanup.
5. T-5dae58cb — Merge PRs with archive-preserving squash messages.
6. T-e1ca1d63 — Publish attributed assigned-agent review findings.
7. T-5be95d1c — Add an opt-in safe pre-merge archive workflow.
8. T-0940d06c — Validate and document the GitHub ticket workflow.

Readiness, cleanup, and agent-review work can proceed independently after PR
operations. Merge depends on readiness and cleanup; final verification covers
all paths. Explicit metadata dependencies record this ordering.

## Decisions and open questions

Confirmed with the maintainer:

- Backlog gating is scoped to the epic merging to default, not the whole board.
  Task merges take done items even while the epic still has backlog work.
- Draft PRs are acceptable if promotion to ready is straightforward. Use one
  explicit rechecking readiness operation; ready does not mean accepted/merged.
- PR descriptions mirror ticket content. Task merges add archive comments and
  remove task files; epic merges retain the epic ID/content in the commit.
- Use the user's identity and visibly label agent-authored messages.
- Implementer agent, reviewer human, consistent with the agreed project roles.

Recommended design, to verify during implementation:

- Squash at both levels, carrying task archive records into the final epic
  commit. This keeps default history concise without depending on unreachable
  feature-branch commits or GitHub-only comments for task recovery.
- An empty backlog is necessary but not sufficient for epic acceptance. Keep
  existing WIP/review/dependency/explicit-review gates rather than weaken them.

Scenarios to cover:

| Scenario | Expected result |
| --- | --- |
| Done task, epic still has backlog | Task may merge; epic remains blocked. |
| Empty epic backlog, unfinished review/WIP | Epic remains blocked. |
| Done file already archived by E-1a88a55f's local workflow | Resolve its record; do not archive/delete it twice. |
| Draft opened, then all work accepted | Recheck current state, mark ready, and recheck again before merge. |
| Work added/reopened or PR head changes after readiness | Stale evidence is invalid; recompute gates/reviews. |
| Cleanup commit changes the reviewed head | Rerun required checks/reviews; do not bypass protections. |
| Retry after comment succeeds but cleanup fails | Reuse verified record and resume without duplicate comments. |
| Same GitHub account opens and agent-reviews PR | Label advisory findings; independent approval remains required if configured. |
| Closed/reopened/already merged PR or conflicting PR candidates | Report/reconcile state explicitly; never create an accidental duplicate or second merge. |
| Fork, protected branch, insufficient permissions, or merge conflict | Fail safely with recovery steps; do not grant privileges or weaken rules. |
| Ticket too large for one GitHub comment | Preserve the full record via a documented bounded/chunked strategy, or block before deletion; never truncate silently. |
| Squash message edited, shallow clone, or missing archive history | Detect incomplete history and explain recovery; never treat missing evidence as acceptance. |

Open questions before implementation:

- Exact CLI/shortcut names and minimum GitHub permissions/authentication mechanism.
- Where task comments live (task PR, epic PR, or cross-linked both) and the
  revision/idempotency markers used for managed content and AGENT attribution.
- How merge-queue/auto-merge policies are supported or explicitly rejected, and
  which opt-in required checks enforce archive-preserving merges outside the CLI.
- Compatibility with grouped epics and repositories whose existing policy
  prohibits the recommended squash method; no silent target/method overrides.
- Public archive content must be reviewed for secrets before publishing. Define
  a safe failure path for prohibited content rather than publish or discard it.

## Verification and handoff

Prepared in backlog only. No feature implementation, branch creation, PR,
workflow installation, push, merge, or human acceptance is claimed. Next action:
implementer prepares T-8818c75d after the archive dependency is accepted, then
follows the dependent tasks. Child roles are agent implementer/human reviewer;
these assignments do not authorize publication or replace human review.
