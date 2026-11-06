# Board migrations

Historical upgrade instructions only. These are not required context for
ordinary ticket authoring, implementation, review, or commits.

## Duplicate skill copies to canonical links

Older installations have regular skill directories under both `.agents/skills/`
and `.workkit/skills/`. Stop concurrent skill edits and compare each pair first.
Preserve unique customizations in the canonical `.workkit/skills/` copy before
removing any duplicate. Replace only the verified duplicate discovery directories
with relative directory symlinks, for example:

```text
.agents/skills/work-execute -> ../../.workkit/skills/work-execute
```

In the toolkit source repository, the target is `../../skills/work-execute`
instead. Repeat for work-prepare and work-commit. Commit the canonical sources
and links together; never link to another developer's home/global installation.
Verify each link's `SKILL.md` is readable and resolves inside the same project.
The installer does not automatically convert an existing installation.

## v0.1 flat children to v0.2 status folders

**Incompatible draft change:** v0.2 requires child status folders. Older boards
are rejected by `check` until migrated; commands do not silently migrate them.
Top-level container paths and ticket metadata do not change.

With no other board commands running, use your editor or filesystem tools:

1. For each epic, move immediate story/task files into folders matching each
   ticket's metadata `status`. For example,
   `E-a1b2c3d4-search/S-1234abcd-title.md` in review becomes
   `E-a1b2c3d4-search/review/S-1234abcd-title.md`.
2. For each group, move immediate epic directories into folders matching the
   epic's own status, taking their entire trees with them.
3. Preserve IDs, metadata, prose, and acceptance records. Never overwrite a
   conflicting destination. Repair prose path links affected by moves.
4. Run `work --root /path/to/project check` (or the installed
   `./.workkit/work`) and review the moves before committing.

Empty status folders are optional; the CLI creates missing ones when needed.

## Stricter completion validation

Validation rejects cycles involving parent/child completion prerequisites, even
if the explicit dependency graph is acyclic. Remove or revise conflicting
dependencies. Unchecked alternative Markdown list markers also block completion;
review the criteria rather than simply changing markers to bypass the gate.
