---
{
  "id": "E-f44b10c1",
  "kind": "epic",
  "title": "Improve terminal workflows with Bash completion and state history",
  "status": "backlog",
  "parent": null,
  "depends_on": [],
  "implementer": null,
  "reviewer": null,
  "branch": null,
  "base_branch": null
}
---
# Improve terminal workflows with Bash completion and state history

## Outcome and value

People using `work` in Bash can discover commands and relevant ticket IDs without
copying them from a board listing. People inspecting stories and epics can see
when their states changed, with structured history that a future timeline or
animation can consume without reconstructing every transition from Git commits.

## Scope

Included:

- Opt-in Bash completion for commands, options, and command-relevant ticket IDs.
- Discovery of the nearest `.work` directory walking upward from the current
  directory, with explicit `--root` taking precedence, consistent with the CLI.
- A documented, timestamped state-change log in a separate ticket section,
  covering stories and epics and deciding consistent handling for tasks/groups.
- Installation guidance, compatibility rules, and automated regression coverage.
- An opt-in, warning-and-confirmation path to accept WIP directly into implemented,
  useful for review-purpose tasks with completed checklists; other acceptance
  safeguards remain in place.
- Assess a focused split of the growing Python module during this work; restructure
  only where it is likely to reduce agent reading/token costs and maintenance effort.

Excluded:

- Building the animation, a dashboard, or a history visualization/export service.
- Other shells, editor completion, or lifecycle/acceptance-gate changes beyond
  the explicitly confirmed WIP acceptance exception.
- Inventing past transitions for existing tickets or tracking arbitrary prose edits.
- A mandatory package rewrite, arbitrary file-size targets, or speculative abstractions.

## Acceptance criteria

- [ ] Bash completion suggests commands/options and IDs appropriate to the current command from the selected board, including from nested project directories.
- [ ] `work start` suggests backlog IDs and review IDs that can return to WIP; `work review` suggests WIP IDs rather than unrelated backlog or completed work.
- [ ] Completion is read-only, tolerates missing/invalid boards, and never runs a transition or changes shell startup files without explicit opt-in.
- [ ] A documented history format lets readers identify each recorded transition's ticket, previous state, next state, and timezone-aware timestamp in a stable order.
- [ ] Successful story/epic state changes preserve earlier history and append the appropriate event; rejected operations and dry runs append nothing.
- [ ] Existing tickets remain usable without a history section, and acceptance records and archived/reopened history remain preserved.
- [ ] Automated checks and a documented Bash smoke test demonstrate both workflows; limitations and supported Bash versions are stated.
- [ ] The module-structure assessment records concrete agent reading/navigation tradeoffs; either a justified small split is verified or keeping the current layout is explicitly justified.
- [ ] WIP acceptance requires explicit opt-in, a warning, and confirmation; the normal review flow remains the default and all other acceptance gates are retained.

## Stories and dependencies

- S-5299cba3 — Complete work commands with relevant board ticket IDs.
- T-f7d4aef3 — Define a timestamped ticket state history format.
- S-56c90e4f — Record ticket state changes for later timeline playback;
  depends on T-f7d4aef3.
- T-6bab2842 — Verify and document terminal completion and state history;
  depends on S-5299cba3, S-56c90e4f, T-10e609cd, and S-8ce9abfb.
- T-10e609cd — Assess and selectively split Python code for agent-efficient maintenance.
  Assess alongside feature implementation; not a mandatory up-front refactor.
- S-8ce9abfb — Allow explicitly confirmed acceptance directly from WIP.
  Coordinate completion filtering and state-history coverage with the other stories.

Completion and history design can proceed independently. No external epic is a
hard prerequisite. E-1c6791d9 covers editor completion, not Bash; reuse a shared
read contract where sensible without making either feature depend on the other.

## Decisions and open questions

- Completion narrows candidates but never guarantees a later command succeeds:
  required evidence, reviewer identity, dependencies, and concurrent changes
  remain enforced by the CLI. Define which eligibility gates filter suggestions.
- Decide archived-ID completion and its latency/failure policy explicitly;
  do not imply that ordinary live-board scanning finds archived tickets.
- T-f7d4aef3 decides event syntax, timestamp precision/order, creation events,
  tasks/groups, automatic ancestor changes, and manual-edit expectations before
  implementation. Keep the log separate from existing acceptance records.
- Preserve editable Markdown and the standard-library-only runtime. No mandatory
  completion framework, background service, or remote request.
- Branch/base and implementer/reviewer remain unset. Intended execution is a
  dedicated branch for E-f44b10c1 from a maintainer-confirmed base, not implicitly
  the current initial-toolkit feature branch.

## Verification and handoff

Prepared in backlog on `feature/E-1a88a55f-initial-toolkit`; no feature work,
acceptance, Git branch setup, or publication is authorized by this preparation.
Next: confirm execution branch/base and roles, then select completion or history
design under the work-execute preflight. Collect temporary-board test results,
Bash smoke-test steps, sample history, and limitations before requesting review.
