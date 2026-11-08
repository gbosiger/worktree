---
{
  "id": "T-64380128",
  "kind": "task",
  "title": "Prepare repository metadata for the first public release",
  "status": "backlog",
  "parent": "E-d0124ce3",
  "depends_on": [
    "E-1a88a55f"
  ],
  "implementer": "agent",
  "reviewer": "human",
  "branch": null,
  "base_branch": null
}
---
# Prepare repository metadata for the first public release

## Purpose and scope

Give the first release a presentable landing page and clean source: badges, About
text and topics, and a quick pass over the files a new contributor first reads.

## Acceptance criteria

- [ ] README shows a CI status badge and a version/release badge that resolve to this repository (a "latest release" badge works before the tag exists; it may point at `v0.1.0` once tagged).
- [ ] LICENSE has the correct year and copyright holder; CONTRIBUTING and the Get-started instructions still match this repository and Python 3.10+.
- [ ] `.gitignore` excludes `__pycache__/` and other generated/cache files, and no such files are tracked.
- [ ] GitHub repository About text, description, and topics are set, or the exact `gh repo edit` commands are prepared for the maintainer to run. Issue/PR templates and SECURITY.md are decided as optional, not silently added.

## Approach and decisions

Small-project hygiene: badges and accurate About text are enough. Do not add
bots, Dependabot, or template machinery the maintainer has not requested.

## Verification

Render the README, confirm the badge URLs and repository visibility, and list
tracked files for cache artifacts.

## Handoff

Hand the README/metadata diff to the human reviewer. Any account-only settings
(About/topics) that the agent cannot apply are listed as steps for the maintainer,
not claimed as done.
