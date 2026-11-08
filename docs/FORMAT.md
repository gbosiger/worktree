# Ticket format

`.work/{backlog,wip,review,implemented,done}/` contains top-level epics or optional groups.
Each group/epic has its own `{backlog,wip,review,implemented,done}/` child folders. Group
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

## Committed records and file-history archive

`implemented` means accepted and waiting for a ticket-linked commit; `done`
means committed and retained with the feature. `work commit` moves selected
implemented records to done in the implementation commit, using their IDs/titles
for its message. Ordinary ticket commits never delete these records.

`work merge ID` integrates a fully committed group or epic into its recorded base.
An epic targeting its WIP parent group's branch uses a regular two-parent merge
and retains its done tree. Final integration (standalone epic or group) uses a
squash commit containing the complete done tree, followed by a separate automatic
cleanup commit. Previously archived descendants are restored recursively first.
Thus both final-base commits survive even if feature/release branches are
discarded, and no intermediate feature commit is required for recovery. This
extends the draft epic-only merge interface without changing ticket metadata or
status folders; existing standalone-epic recovery journals remain supported.

An archived ticket is a previously committed, accepted done file that a later
commit removes. Its immutable filename ID locates it in Git's file changes;
the deleted file's blob contains the complete ticket. No commit-message marker,
ticket list, or special subject is required. Ordinary Git deletion commits work
as well as the post-merge cleanup.

The reader validates the saved ticket's done status, reviewer, checked criteria,
timestamped acceptance evidence, and original done path. A rename/status move
that leaves the ID present in the resulting tree is not an archive. Unfinished,
invalid, or non-regular deleted files do not become accepted records.
If a later/conflicting unfinished deletion would expose an older approval as
current completion, lookup fails until the saved ticket is restored/reconciled;
it does not silently reuse that stale approval.

The cleanup creates a readable message for people:

```text
task: archive 2 completed tickets

## Completed tickets

- T-1234abcd — Add search tests
- T-5678abcd — Document search
```

The list is a human summary, not a lookup index. The cleanup's first-parent tree
stores accepted files as ordinary UTF-8 Markdown under their done paths; the
cleanup commit removes those paths. Ordinary implementation commits never delete
the queue; new tickets are first retained as done files in their commit.

Parent links remain the `parent` IDs inside the saved metadata. Reopening follows
those links to live or deleted epics/groups; containers need not have been removed
in the same commit as their children. Missing parent records block restoration
rather than inventing a container. Lookup records include a computed SHA-256
and the deletion commit's provenance.

Keep the integration and cleanup commits separate on the base branch. Squashing
those two together would remove the only saved ticket tree. Copying a message
cannot preserve deleted content. Files never committed before deletion cannot
be recovered by this reader.

History reads all commits reachable from HEAD. A descendant record supersedes
older occurrences; identical incomparable contents coalesce with their commit
provenance, while divergent contents require explicit descendant reconciliation.
Live reopened content takes precedence for current status. Missing IDs, missing
objects, and shallow history never imply acceptance; no automatic fetch occurs.
