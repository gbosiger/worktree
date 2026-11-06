---
{
  "id": "T-0940d06c",
  "kind": "task",
  "title": "Validate and document the GitHub ticket workflow",
  "status": "backlog",
  "parent": "E-54e9139e",
  "depends_on": ["T-5dae58cb", "T-e1ca1d63", "T-5be95d1c"],
  "implementer": "agent",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Validate and document the GitHub ticket workflow

## Purpose and scope

Prove the complete draft/task/epic workflow and provide concise CLI/OpenCode
entry points plus operational recovery guidance. No real publication is required.

## Acceptance criteria

- [ ] Map every epic acceptance criterion and scenario to automated coverage or clearly identified manual verification; record gaps instead of declaring untested behavior accepted.
- [ ] End-to-end tests cover task merges with epic backlog, draft-to-ready, reopened work/changed heads, cleanup reapproval, retries, self-review limits, fork/protection failures, oversized records, and edited squash messages.
- [ ] Verify normal-clone offline lookup/dependencies/reopening after both squash levels and safe failure for shallow/missing history; local-only users retain existing commands without GitHub access.
- [ ] CLI help, focused Git/GitHub/recovery docs, and canonical skills describe actual permissions, authorization, managed content, merge policy, secret review, and enforcement limits.
- [ ] Add the agreed OpenCode shortcuts in canonical commands/ with repository links and installation coverage; no duplicate templates or shell interpolation of user arguments.
- [ ] Full unit suite, installed-project smoke checks, and dogfood check pass using fakes/disposable repositories; provide human-review evidence without opening PRs, installing remote workflows, pushing, or merging real branches.

## Approach and decisions

Update documentation only for implemented behavior. Maintain commands/ and
skills/ as canonical sources and keep integration assets project-local.

## Verification

Run python3 -m unittest discover -s tests -v and ./work --root . check.
Exercise installed shortcuts and the documented recovery paths in isolated projects.

## Handoff

Present scenario coverage, remaining limitations, and the next explicitly
authorized manual verification step to the human reviewer.
