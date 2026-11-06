# Ticket format

`.work/{backlog,wip,review,done}/` contains top-level epics or optional groups.
Each group/epic has its own `{backlog,wip,review,done}/` child folders. Group
status folders contain epic directories; epic status folders contain story and
task Markdown files. Every group/epic has a `README.md` describing its scope.

One optional group level; no recursive groups. Group = larger outcome; epic =
feature; story = behavioral increment; task = supporting work.

Every ticket's immediate status folder must match its metadata. For example:

```text
.work/wip/E-a1b2c3d4-search/README.md
.work/wip/E-a1b2c3d4-search/review/S-1234abcd-title.md
.work/wip/E-a1b2c3d4-search/done/T-87654321-tests.md
.work/wip/G-11223344-discovery/backlog/E-55667788-filters/README.md
```

Names are `E-<8 hex digits>-slug/README.md`, `G-<8 hex digits>-slug/README.md`,
`S-<8 hex digits>-slug.md`, and `T-<8 hex digits>-slug.md`. IDs are immutable,
random, checked for local uniqueness, and never deliberately reused. `check`
detects duplicate IDs after merges. Use ID references in prose; repair path links
after moves. Empty status folders are optional; new containers include `.gitkeep`
files, and the CLI creates missing folders when needed.

## Metadata

Metadata is a JSON object between `---` lines. JSON is a YAML-compatible subset;
use double-quoted strings, arrays, and null, not unrestricted YAML. Human prose
follows the closing line. Preserve unknown keys and the prose body when editing.

Required fields: `id`, `kind`, `title`, `status`, `parent`, `depends_on`.
Optional fields: `implementer`, `reviewer`, `branch`, `base_branch`.
`parent` is an ID or null. `depends_on` is an array of ticket IDs, not paths.

```markdown
---
{
  "id": "T-1234abcd",
  "kind": "task",
  "title": "Verify search behavior",
  "status": "backlog",
  "parent": "E-a1b2c3d4",
  "depends_on": []
}
---
# Verify search behavior

## Acceptance criteria

- [ ] Search returns matching titles.
```
