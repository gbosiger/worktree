#!/usr/bin/env python3
"""Worktree Tickets: a dependency-free Markdown work board. Python 3.10+."""
import argparse
import base64
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
import uuid

VERSION = '0.2.0'
TOOLKIT = Path(__file__).resolve().parents[2]
STATES = ('backlog', 'wip', 'review', 'implemented', 'done')
COMPLETED = ('implemented', 'done')
KINDS = {'group': 'G', 'epic': 'E', 'story': 'S', 'task': 'T'}
ARCHIVE_HEADING = '## Completed tickets'


def fail(message):
    raise ValueError(message)


def _archive_json(text):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                fail(f'Duplicate JSON key: {key}')
            result[key] = value
        return result
    def invalid(value):
        fail(f'Invalid JSON constant: {value}')
    def finite(value):
        number = float(value)
        if not math.isfinite(number):
            fail(f'Nonfinite JSON number: {value}')
        return number
    return json.loads(text, object_pairs_hook=unique, parse_constant=invalid, parse_float=finite)


def _archive_ticket(content, accepted=True, completed=('done',)):
    """Validate a standalone record without normalizing its stored content."""
    if not isinstance(content, str):
        fail('Ticket content must be a UTF-8 string')
    content.encode('utf-8')  # Reject lone surrogates, including JSON escape forms.
    parts = content.replace('\r\n', '\n').split('---\n', 2)
    if len(parts) != 3 or parts[0]:
        fail('Expected JSON ticket frontmatter between --- lines')
    meta = _archive_json(parts[1])
    if not isinstance(meta, dict):
        fail('Ticket frontmatter must be an object')
    identity, kind = meta.get('id'), meta.get('kind')
    if not isinstance(identity, str) or not re.fullmatch(r'[GEST]-[0-9a-f]{8}', identity):
        fail('Invalid ticket ID')
    if not isinstance(kind, str) or kind not in KINDS or not identity.startswith(KINDS[kind] + '-'):
        fail(f'{identity}: kind and ID disagree')
    if not isinstance(meta.get('title'), str) or not meta['title'].strip():
        fail(f'{identity}: title is required')
    if meta.get('status') not in STATES:
        fail(f'{identity}: invalid status')
    parent = meta.get('parent')
    if 'parent' not in meta or (parent is not None and
                               (not isinstance(parent, str) or not re.fullmatch(r'[GE]-[0-9a-f]{8}', parent))):
        fail(f'{identity}: invalid parent')
    if ((kind == 'group' and parent is not None) or
            (kind in ('story', 'task') and (parent is None or not parent.startswith('E-'))) or
            (kind == 'epic' and parent is not None and not parent.startswith('G-'))):
        fail(f'{identity}: invalid parent kind')
    deps = meta.get('depends_on')
    if (not isinstance(deps, list) or
            not all(isinstance(dep, str) and re.fullmatch(r'[GEST]-[0-9a-f]{8}', dep) for dep in deps) or
            len(set(deps)) != len(deps) or identity in deps):
        fail(f'{identity}: invalid dependencies')
    if accepted:
        reviewer = meta.get('reviewer')
        if meta['status'] not in completed or not isinstance(reviewer, str) or not reviewer.strip() or '\n' in reviewer or '\r' in reviewer:
            fail(f'{identity}: archive requires done status and a recorded reviewer')
        body = parts[2]
        if re.search(r'^[ \t]*(?:[-+*]|[0-9]{1,9}[.)])[ \t]+\[ \](?=[ \t\r\n]|$)', body, re.MULTILINE):
            fail(f'{identity}: unchecked acceptance/completion items remain')
        sections = re.split(r'^## Acceptance record[ \t]*\n', body, flags=re.MULTILINE)
        latest = sections[-1].split('\n## ', 1)[0].strip() if len(sections) > 1 else ''
        match = re.fullmatch(r'([^\n]+) — ' + re.escape(reviewer) + r': ([\s\S]+)', latest)
        if not match or not match[2].strip():
            fail(f'{identity}: missing acceptance evidence for recorded reviewer')
        try:
            stamp = datetime.fromisoformat(match[1])
        except ValueError:
            fail(f'{identity}: invalid acceptance timestamp')
        if stamp.tzinfo is None:
            fail(f'{identity}: acceptance timestamp must include a timezone')
    return meta, parts[2]


def _archive_record(record):
    if not isinstance(record, dict) or set(record) != {'id', 'path', 'sha256', 'content'}:
        fail('Archive ticket requires id, path, sha256, and content')
    meta, _ = _archive_ticket(record['content'])
    if record['id'] != meta['id']:
        fail('Archive ID disagrees with ticket content')
    path = record['path']
    if (not isinstance(path, str) or '\\' in path or '\x00' in path or
            not path.startswith('.work/') or any(part in ('', '.', '..') for part in path.split('/'))):
        fail(f'{meta["id"]}: unsafe archive path')
    parts = path.split('/')
    expected = 'README.md' if meta['kind'] in ('group', 'epic') else None
    if (len(parts) < 3 or (expected and (parts[-1] != expected or not parts[-2].startswith(meta['id'] + '-'))) or
            (not expected and (not parts[-1].startswith(meta['id'] + '-') or not path.endswith('.md')))):
        fail(f'{meta["id"]}: archive filename disagrees with ticket kind/ID')
    status_index = -3 if expected else -2
    if parts[status_index] != 'done':
        fail(f'{meta["id"]}: archived file must come from a done folder')
    parent_parts = parts[:status_index]
    if meta['parent'] is None:
        if parent_parts != ['.work']:
            fail(f'{meta["id"]}: archive path disagrees with top-level parent')
    elif not parent_parts or not parent_parts[-1].startswith(meta['parent'] + '-'):
        fail(f'{meta["id"]}: archive path disagrees with parent ID')
    digest = hashlib.sha256(record['content'].encode('utf-8')).hexdigest()
    if record['sha256'] != digest:
        fail(f'{meta["id"]}: archive SHA-256 mismatch')


def _archive_git(root, *args, input=None):
    # Git reads must not inherit another checkout's routing or fetch missing objects.
    env = dict(os.environ, GIT_NO_LAZY_FETCH='1', GIT_OPTIONAL_LOCKS='0')
    for key in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_COMMON_DIR', 'GIT_INDEX_FILE',
                'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES',
                'GIT_SHALLOW_FILE', 'GIT_NAMESPACE'):
        env.pop(key, None)
    result = subprocess.run(['git', '--no-replace-objects', '-C', str(root), *args],
                            input=input, capture_output=True, env=env)
    if result.returncode:
        error = result.stderr.decode('utf-8', errors='replace').strip()
        fail(f'Cannot read archive history ({" ".join(args)}): {error}. '
             'Verify the local repository, HEAD, and available Git objects; no fetch was attempted.')
    return result.stdout


class ArchiveObjects:
    """Read Git objects in batches; cache only for this command, never on disk."""

    def __init__(self, root):
        self.root = root
        self.cache = {}

    def load(self, specs):
        missing = list(dict.fromkeys(spec for spec in specs if spec not in self.cache))
        if not missing:
            return
        raw = _archive_git(self.root, 'cat-file', '--batch',
                           input=('\n'.join(missing) + '\n').encode('ascii'))
        offset = 0
        for spec in missing:
            end = raw.index(b'\n', offset)
            header = raw[offset:end].split()
            offset = end + 1
            if header[-1] == b'missing':
                fail(f'Missing archive Git object: {spec}; obtain complete history explicitly; no fetch was attempted')
            oid, kind, size = header
            size = int(size)
            entry = (kind.decode('ascii'), raw[offset:offset + size])
            self.cache[spec] = self.cache[oid.decode('ascii')] = entry
            offset += size + 1
        if offset != len(raw):
            fail('Malformed batched archive object response')

    def blob(self, oid):
        self.load([oid])
        kind, content = self.cache[oid]
        if kind != 'blob':
            fail(f'{oid}: archive source is not a regular file')
        return content


def _ticket_path_id(path):
    name = PurePosixPath(path)
    value = name.parent.name if name.name == 'README.md' else name.name if name.suffix == '.md' else ''
    match = re.match(r'([GEST]-[0-9a-f]{8})-', value)
    return match[1] if match else None


class TicketFileHistory:
    """Git-native file changes with a compact, per-ID in-memory lookup.

    Each commit's first-parent diff describes its exact file state, including
    merge results. Side-branch commits are indexed too. Only IDs changed at a
    commit need a new entry; we never copy a whole board for every revision.
    """

    def __init__(self, root, parents):
        self.events = {}
        self.deleted = {}
        self.intervals = {}
        # DFS intervals make first-parent ancestry checks constant-time without
        # walking thousands of unrelated commits once per ticket.
        children, roots = {}, []
        for oid, links in parents.items():
            if links:
                children.setdefault(links[0], []).append(oid)
            else:
                roots.append(oid)
        pending = [(oid, False) for oid in roots]
        clock = 0
        while pending:
            oid, leaving = pending.pop()
            if leaving:
                self.intervals[oid][1] = clock
            else:
                self.intervals[oid] = [clock, None]
                clock += 1
                pending.append((oid, True))
                pending.extend((child, False) for child in children.get(oid, []))

        pairs = [f'{oid} {links[0]}\n' if links else f'{oid}\n' for oid, links in parents.items()]
        raw = _archive_git(root, 'diff-tree', '--stdin', '--root', '--always', '-r', '-z',
                           '--no-renames', '--no-abbrev', '--', '.work',
                           input=''.join(pairs).encode('ascii'))
        fields, index, changes = raw.split(b'\0'), 0, {}
        while index < len(fields) - 1:
            field = fields[index]
            index += 1
            if not field.startswith(b':'):
                oid = field.decode('ascii')
                continue
            old_mode, mode, old_blob, blob, status = field[1:].decode('ascii').split()
            path = fields[index].decode('utf-8')
            index += 1
            identity = _ticket_path_id(path)
            if not identity:
                continue
            changes.setdefault(oid, {}).setdefault(identity, []).append((path, mode, blob))
            name = PurePosixPath(path)
            stage = name.parent.parent.name if name.name == 'README.md' else name.parent.name
            if status == 'D' and stage == 'done':
                self.deleted.setdefault(oid, []).append((path, old_mode, old_blob))

        # rev-list topological order is descendants first; construct file states
        # in the opposite order so a commit's first-parent state is available.
        for oid in reversed(parents):
            for identity, entries in changes.get(oid, {}).items():
                links = parents[oid]
                state = dict(self.at(links[0], identity)) if links else {}
                for path, mode, blob in entries:
                    if mode == '000000':
                        state.pop(path, None)
                    else:
                        state[path] = (mode, blob)
                self.events.setdefault(identity, []).append((oid, state))

    def at(self, oid, identity):
        position = self.intervals[oid][0]
        for commit, state in reversed(self.events.get(identity, [])):
            begin, end = self.intervals[commit]
            if begin <= position < end:
                return state
        return {}


def _git(root, *args, env=None, input=None):
    """Run git in `root`, returning the text-mode CompletedProcess (captured)."""
    full = dict(os.environ, GIT_NO_LAZY_FETCH='1', GIT_TERMINAL_PROMPT='0', GIT_OPTIONAL_LOCKS='0')
    for key in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_COMMON_DIR', 'GIT_INDEX_FILE',
                'GIT_OBJECT_DIRECTORY', 'GIT_ALTERNATE_OBJECT_DIRECTORIES',
                'GIT_SHALLOW_FILE', 'GIT_NAMESPACE'):
        full.pop(key, None)
    if env:
        full.update(env)
    return subprocess.run(['git', '-c', 'diff.autoRefreshIndex=false', '-C', str(root), *args],
                          capture_output=True, text=True, input=input, env=full)


def _git_ok(root, *args, env=None, input=None):
    result = _git(root, *args, env=env, input=input)
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        fail(f'git {" ".join(args)} failed: {detail}')
    return result


def archive_history(root, revision='HEAD'):
    """Read HEAD-reachable archives, returning records with maximal commit provenance.

    No board, index, ref, object, or configuration writes. An unborn HEAD has
    no reachable archives; missing objects behind existing refs remain errors.
    """
    if _archive_git(root, 'rev-parse', '--is-shallow-repository').strip() == b'true':
        fail('Incomplete archive history: shallow repository; obtain full history explicitly before retrying')
    try:
        branch = _archive_git(root, 'symbolic-ref', '-q', 'HEAD').decode('utf-8', errors='surrogateescape').strip()
    except ValueError:
        branch = None  # Detached HEAD still requires a readable commit below.
    if branch:
        refs = _archive_git(root, 'for-each-ref', '--format=%(refname)', branch).decode('utf-8', errors='surrogateescape').splitlines()
        if branch not in refs:
            return {}  # Unborn HEAD: there are no reachable commits to archive.
    head = _archive_git(root, 'rev-parse', '--verify', f'{revision}^{{commit}}').decode('ascii').strip()
    rows = _archive_git(root, 'rev-list', '--topo-order', '--parents', head).decode('ascii').splitlines()
    parents = dict((parts[0], parts[1:]) for parts in (row.split() for row in rows))
    objects = ArchiveObjects(root)
    occurrences = {}
    files = TicketFileHistory(root, parents)
    blobs = [blob for entries in files.deleted.values() for _, mode, blob in entries
             if mode in ('100644', '100755')]
    objects.load(blobs)
    for oid, entries in files.deleted.items():
        for path, mode, blob in sorted(entries):
            identity = _ticket_path_id(path)
            if files.at(oid, identity) or mode not in ('100644', '100755'):
                continue  # Renames/status moves and non-regular files are not archives.
            try:
                content = objects.blob(blob).decode('utf-8')
                record = dict(id=identity, path=path, content=content,
                              sha256=hashlib.sha256(content.encode('utf-8')).hexdigest())
                _archive_record(record)
            except (ValueError, UnicodeError):
                continue  # Ordinary deletion is never evidence of acceptance by itself.
            source = files.at(parents[oid][0], identity)
            if len(source) != 1:
                fail(f'{oid}: {identity}: duplicate snapshot records')
            occurrences.setdefault(identity, []).append((oid, record))

    order = {oid: index for index, oid in enumerate(parents)}

    def is_ancestor(older, newer):
        begin, end = files.intervals[older]
        if begin <= files.intervals[newer][0] < end:
            return True
        if order[older] < order[newer]:
            return False
        pending, seen = [newer], set()
        while pending:
            oid = pending.pop()
            if oid == older:
                return True
            if oid not in seen:
                seen.add(oid)
                pending.extend(parents[oid])
        return False

    result = {}
    for identity, entries in occurrences.items():
        maximal = []
        # rev-list's topo order visits descendants before their ancestors.
        for oid, record in sorted(entries, key=lambda entry: order[entry[0]]):
            if not any(is_ancestor(oid, newer) for newer, _ in maximal):
                maximal.append((oid, record))
        if not files.at(head, identity):
            for oid, state in files.events.get(identity, []):
                if not state and not any(is_ancestor(oid, newer) for newer, _ in maximal):
                    fail(f'{identity}: later or conflicting deletion at {oid} lacks accepted done evidence; '
                         'restore and reconcile the saved ticket before treating it as completed')
        if len({record['content'] for _, record in maximal}) != 1:
            fail(f'{identity}: conflicting archive records in incomparable commits: '
                 + ', '.join(sorted(oid for oid, _ in maximal))
                 + '; reconcile explicitly in a descendant archive commit')
        maximal.sort(key=lambda entry: entry[0])
        result[identity] = dict(maximal[0][1], commits=[oid for oid, _ in maximal])
    return result


def resolve_archive(history, identity, live=None):
    """Resolve against validated history and optional {ID: full live content}.

    Live content wins (including reopened backlog status), but callers must read
    history first so a live file cannot conceal corrupted/conflicting archives.
    A missing ID is unresolved, never evidence of completion.
    """
    if live is not None and identity in live:
        content = live[identity]
        meta, _ = _archive_ticket(content, accepted=False)
        if identity != meta['id']:
            fail('Live ID disagrees with ticket content')
        return dict(id=identity, path=None, content=content, source='live', commits=[],
                    sha256=hashlib.sha256(content.encode('utf-8')).hexdigest())
    if identity not in history:
        fail(f'Unresolved ticket: {identity}; absent from live board and reachable archive history')
    return dict(history[identity], source='archive')


class Archives:
    """Lazily resolved HEAD-reachable archive records for one board.

    Outside any Git work tree no archives can exist, so reads return {}.
    Unreadable history (shallow clones, missing objects) fails with guidance
    rather than implying absence; callers trigger it only when archives matter.
    """

    def __init__(self, root):
        self.root = root
        self.history = None
        self.error = None

    def _inside_git(self):
        try:
            return _archive_git(self.root, 'rev-parse', '--is-inside-work-tree').strip() == b'true'
        except ValueError:
            return False

    def read(self):
        if self.history is None and self.error is None:
            if not self._inside_git():
                self.history = {}
            else:
                try:
                    self.history = archive_history(self.root)
                except ValueError as error:
                    self.error = str(error)
        if self.error is not None:
            fail(self.error)
        return self.history


def lookup(items, archives, identity):
    """Resolve a live or archived ticket to (path, meta, body, record).

    Live tickets return their file path and record=None; archived tickets
    return path=None and their history record. A missing ID is an error, never
    evidence of completion; unreadable history fails with its own guidance.
    """
    if identity in items:
        path, meta, body = items[identity]
        return path, meta, body, None
    record = archives.read().get(identity)
    if record is not None:
        meta, body = _archive_ticket(record['content'], accepted=False)
        return None, meta, body, record
    fail(f'Unknown ticket: {identity}; no live or accepted committed done file was found. '
         'Message-only prototype archives are unsupported; restore the original accepted files explicitly.')


def archived_children(archives, identity):
    return [record['id'] for record in archives.read().values()
            if _archive_ticket(record['content'], accepted=False)[0].get('parent') == identity]


def ensure_container_states(container):
    for stage in STATES:
        folder = container / stage
        if not folder.exists():
            folder.mkdir()
            (folder / '.gitkeep').touch()


def read(path):
    text = path.read_text(encoding='utf-8')
    parts = text.split('---\n', 2)
    if len(parts) != 3 or parts[0]:
        fail(f'{path}: expected JSON frontmatter between --- lines')
    try:
        meta = json.loads(parts[1])
    except json.JSONDecodeError as exc:
        fail(f'{path}: invalid JSON frontmatter: {exc}')
    if not isinstance(meta, dict):
        fail(f'{path}: frontmatter must be an object')
    return meta, parts[2]


def write(path, meta, body):
    content = '---\n' + json.dumps(meta, indent=2, ensure_ascii=False) + '\n---\n' + body
    # Same-directory replacement prevents partial ticket contents after interruption.
    fd, name = tempfile.mkstemp(prefix='.work-write-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(content)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def root_at(start):
    start = start.resolve()
    for candidate in (start, *start.parents):
        if (candidate / '.work').is_dir():
            return candidate
    fail('No .work directory found. Run work init first.')


def records(root):
    result = {}
    for stage in STATES:
        for path in sorted((root / '.work' / stage).rglob('*.md')):
            # Board contains tickets only; prose belongs in its root README.
            meta, body = read(path)
            identity = meta.get('id', '')
            if not isinstance(identity, str) or not re.fullmatch(r'[GEST]-[0-9a-f]{8}', identity):
                fail(f'{path}: invalid or missing id')
            if identity in result:
                fail(f'Duplicate ID: {identity}')
            result[identity] = (path, meta, body)
    return result


@contextmanager
def locked(root):
    lock = root / '.work' / '.lock'
    try:
        lock.mkdir()
    except FileExistsError:
        fail('Another work command is active. If it crashed, remove .work/.lock after checking.')
    try:
        yield
    finally:
        lock.rmdir()


def get(items, identity):
    if identity not in items:
        fail(f'Unknown ticket: {identity}')
    return items[identity]


def children(items, identity):
    return [m['id'] for _, m, _ in items.values() if m.get('parent') == identity]


def ancestors(items, identity, archives=None):
    seen = set()
    _, meta, _, _ = lookup(items, archives, identity)
    parent = meta.get('parent')
    while parent:
        if parent in seen:
            fail('Parent cycle detected')
        seen.add(parent)
        yield parent
        _, meta, _, _ = lookup(items, archives, parent)
        parent = meta.get('parent')


def check(root, items, archives=None):
    for identity, (path, meta, _) in items.items():
        kind, status = meta.get('kind'), meta.get('status')
        if not isinstance(kind, str) or not isinstance(status, str):
            fail(f'{identity}: kind/status must be strings')
        if meta.get('parent') is not None and not isinstance(meta['parent'], str):
            fail(f'{identity}: parent must be an ID or null')
        if kind not in KINDS or not identity.startswith(KINDS[kind] + '-'):
            fail(f'{identity}: kind and ID disagree')
        if status not in STATES:
            fail(f'{identity}: invalid status')
        if not isinstance(meta.get('title'), str) or not meta['title'].strip():
            fail(f'{identity}: title is required')
        list(ancestors(items, identity, archives))  # Validate ancestry before using parent paths.
        parent = meta.get('parent')
        if parent:
            pp, pm, _, parent_record = lookup(items, archives, parent)
            if (kind == 'epic' and pm['kind'] != 'group') or (kind in ('story', 'task') and pm['kind'] != 'epic') or kind == 'group':
                fail(f'{identity}: invalid parent kind')
            if parent_record is None:
                expected = pp.parent / status
        elif kind in ('story', 'task'):
            fail(f'{identity}: stories/tasks require an epic')
        else:
            expected = root / '.work' / status
        # A live ticket under an archived container keeps its file in the
        # container's leftover directory; there is no live parent path to
        # compare against, so directory agreement is skipped for that state.
        # The archive writer must not produce it, and reopening the ticket
        # restores the ancestor structure.
        if not (parent and parent_record is not None):
            actual = path.parent.parent if kind in ('epic', 'group') else path.parent
            if actual != expected:
                fail(f'{identity}: parent/directory/status disagree; expected under {expected}. '
                     'Use the status-folder layout in docs/FORMAT.md; repair the board explicitly without overwriting files.')
        if kind in ('group', 'epic') and (path.name != 'README.md' or not path.parent.name.startswith(identity + '-')):
            fail(f'{identity}: containers require README.md')
        if kind in ('story', 'task') and not path.name.startswith(identity + '-'):
            fail(f'{identity}: filename must start with its ID')
        if not path.resolve().is_relative_to((root / '.work').resolve()):
            fail(f'{identity}: ticket escapes .work')
        deps = meta.get('depends_on', [])
        if not isinstance(deps, list) or not all(isinstance(d, str) for d in deps):
            fail(f'{identity}: depends_on must be a list of IDs')
        for dep in deps:
            lookup(items, archives, dep)
            if dep == identity:
                fail(f'{identity}: cannot depend on itself')
        if status in COMPLETED and any(get(items, c)[1]['status'] not in COMPLETED for c in children(items, identity)):
            fail(f'{identity}: done container has unfinished children')
        if status in COMPLETED and any(lookup(items, archives, d)[1]['status'] not in COMPLETED for d in deps):
            fail(f'{identity}: done ticket has unfinished dependencies')
    visiting, visited = set(), set()
    def visit(identity):
        if identity in visiting:
            fail(f'Dependency cycle at {identity}')
        if identity in visited:
            return
        visiting.add(identity)
        # Completing a container also requires completing its children. Include
        # those implicit prerequisites to catch otherwise unfinishable boards.
        # Archived records are immutable and were validated when live; archived
        # children of an archived ticket still participate, but a live parent's
        # archived children were complete at archive time and cannot close a
        # new cycle through live tickets.
        _, meta, _, record = lookup(items, archives, identity)
        prerequisites = meta.get('depends_on', []) + children(items, identity)
        if record is not None:
            prerequisites += archived_children(archives, identity)
        for dep in prerequisites:
            visit(dep)
        visiting.remove(identity)
        visited.add(identity)
    for identity in items:
        visit(identity)


def execution_target(chain):
    """Resolve branch context without changing ordinary commit selection rules."""
    selected = chain[0]
    container = next(meta for meta in chain if meta['kind'] in ('group', 'epic'))
    owner = selected if selected['kind'] in ('story', 'task') and selected.get('branch') else container
    for meta in (selected, container):
        for key in ('branch', 'base_branch'):
            value = meta.get(key)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                fail(f'{meta["id"]}: {key} must be a nonempty string or null')
    branch = owner.get('branch')
    base = owner.get('base_branch') or container.get('base_branch')
    return branch, base, owner['id']


def list_tickets(root, items, archives, args):
    """Select an action queue, never guess scope from WIP or branch spelling."""
    epic, current = args.epic, None
    if epic:
        if get(items, epic)[1]['kind'] != 'epic':
            fail('--epic requires a live epic ID')
    elif not args.all:
        git = _git(root, 'rev-parse', '--show-toplevel')
        if git.returncode:
            if 'not a git repository' not in git.stderr.lower():
                fail(f'Cannot inspect Git context: {git.stderr.strip()}')
            fail('No Git branch context; use --epic ID or --all')
        branch = _git(root, 'symbolic-ref', '--quiet', 'HEAD')
        if branch.returncode == 1:
            fail('Detached HEAD; use --epic ID or --all')
        if branch.returncode:
            fail(f'Cannot inspect branch: {branch.stderr.strip()}')
        current = branch.stdout.strip().removeprefix('refs/heads/')
        matches = set()
        for identity, (_, meta, _) in items.items():
            if meta['kind'] == 'group':
                continue
            chain = [meta, *[lookup(items, archives, i)[1]
                             for i in ancestors(items, identity, archives)]]
            if execution_target(chain)[0] == current:
                matches.add(next(m['id'] for m in chain if m['kind'] == 'epic'))
        if len(matches) != 1:
            detail = ', '.join(sorted(matches)) or 'none'
            fail(f'Branch {current!r} has no unique epic (matches: {detail}); use --epic ID or --all')
        epic = matches.pop()

    status = args.status or ('backlog' if args.ready or not args.all else None)
    leaves_only = args.ready or (not args.all and args.status is None)
    for identity, (path, meta, _) in sorted(items.items()):
        if status and meta['status'] != status:
            continue
        if leaves_only and meta['kind'] not in ('story', 'task'):
            continue
        chain = [meta, *[lookup(items, archives, i)[1]
                         for i in ancestors(items, identity, archives)]]
        if epic and not any(m['id'] == epic for m in chain):
            continue
        if current and execution_target(chain)[0] != current:
            continue
        if args.ready:
            if any(m['status'] not in ('backlog', 'wip') for m in chain[1:]):
                continue
            if any(lookup(items, archives, dep)[1]['status'] not in COMPLETED
                   for m in chain for dep in m.get('depends_on', [])):
                continue
        print(f'{identity}  {meta["status"]:8}  {meta["title"]}  {path.relative_to(root)}')


def preflight(root, identity, purpose='execute'):
    """Observe execution context only: no toolkit lock, journal, or Git writes."""
    blockers, decisions = [], []
    print(f'Preflight {identity} ({purpose}); board: {root}')
    git = _git(root, 'rev-parse', '--show-toplevel')
    current = None
    in_git = git.returncode == 0
    if in_git:
        branch_result = _git(root, 'symbolic-ref', '--quiet', 'HEAD')
        if branch_result.returncode not in (0, 1):
            fail(f'Cannot inspect branch: {branch_result.stderr.strip()}')
        current = branch_result.stdout.strip().removeprefix('refs/heads/') if branch_result.returncode == 0 else None
        print(f'Git: {git.stdout.strip()}; branch: {current or "DETACHED"}')
        if not current:
            blockers.append('Detached HEAD; authorize a concrete branch/worktree setup plan')
        worktrees = _git_ok(root, 'worktree', 'list', '--porcelain').stdout
        for entry in worktrees.strip().split('\n\n'):
            fields = dict(line.partition(' ')[::2] for line in entry.splitlines())
            print(f'Worktree: {fields.get("worktree", "?")} '
                  f'[{fields.get("branch", "detached").removeprefix("refs/heads/")}]')
        dirty = _git_ok(root, 'status', '--short', '--untracked-files=normal').stdout.splitlines()
        print(f'Dirty: {len(dirty)} entries' if dirty else 'Dirty: clean')
        for line in dirty[:12]:
            print(f'  {line}')
        if len(dirty) > 12:
            print('  ... inspect the diff/status for remaining paths')
        if dirty:
            decisions.append('Confirm dirty-work ownership from the diff before edits; preserve unrelated work')
    elif 'not a git repository' in git.stderr.lower():
        print('Git: not a Git repository; branch/worktree checks not applicable')
    else:
        blockers.append(f'Cannot inspect Git context: {git.stderr.strip() or git.stdout.strip()}')

    for relative in ('.work/.lock', f'.work/{JOURNAL_NAME}'):
        if (root / relative).exists():
            blockers.append(f'{relative} needs attention; inspect active work/recovery before mutations')
    try:
        items, archives = records(root), Archives(root)
        check(root, items, archives)
        print(f'Board: valid ({len(items)} live tickets)')
        _, selected, _, archived = lookup(items, archives, identity)
        chain = [selected, *[lookup(items, archives, i)[1] for i in ancestors(items, identity, archives)]]
        for meta in reversed(chain):
            print(f'Ticket: {meta["id"]} {meta["kind"]} {meta["status"]}')
        print(f'Owners: implementer={selected.get("implementer") or "unset"}; '
              f'reviewer={selected.get("reviewer") or "unset"}')
        if not selected.get('implementer') or not selected.get('reviewer'):
            decisions.append('Establish unset implementer/reviewer roles before execution')
        branch, base, owner = execution_target(chain)
        print(f'Target: branch={branch or "unset"}; base={base or "unset"}; from={owner}')
        if in_git:
            for label, name in (('branch', branch), ('base_branch', base)):
                if not name:
                    blockers.append(f'Missing {label}; resolve and record the intended target, not the current checkout')
                elif _git(root, 'check-ref-format', f'refs/heads/{name}').returncode:
                    blockers.append(f'Invalid {label}: {name!r}')
                elif _git(root, 'show-ref', '--verify', '--quiet', f'refs/heads/{name}').returncode:
                    blockers.append(f'Missing local {label} {name!r}; obtain explicit setup authorization')
            if branch and current and current != branch:
                blockers.append(f'Wrong branch: actual {current!r}, expected {branch!r}; authorize a setup/relocation plan')
        if archived is not None:
            blockers.append(f'{identity} is archived; reopen it before execution')
        if purpose == 'execute':
            for meta in chain:
                if meta is not selected and meta['status'] not in ('backlog', 'wip'):
                    blockers.append(f'Ancestor {meta["id"]} is {meta["status"]}; resolve its lifecycle gate or obtain an explicit exception')
                if meta is selected and meta['status'] in COMPLETED:
                    blockers.append(f'{identity} is {meta["status"]}; reopen before implementation')
                for dep in meta.get('depends_on', []):
                    if lookup(items, archives, dep)[1]['status'] not in COMPLETED:
                        blockers.append(f'{meta["id"]}: unfinished dependency {dep}')
            starts = [meta['id'] for meta in reversed(chain) if meta['status'] == 'backlog']
            if starts:
                print('Start order (not performed): ' + ' -> '.join(starts))
        else:
            print('Commit context only: lifecycle/acceptance eligibility is checked by work commit --dry-run')
    except ValueError as error:
        blockers.append(str(error))
    for decision in decisions:
        print(f'Decision: {decision}')
    for blocker in blockers:
        print(f'BLOCKED: {blocker}')
    print('Read-only snapshot; no Git setup, status transition, commit, or approval is authorized.')
    if blockers:
        fail('Preflight blocked; resolve the reported issues before execution')
    print('OK: mechanical checks passed; required decisions still belong to the user/agent.')


def persist(root, items, identity, meta, body):
    path, old, _ = get(items, identity)
    if old['status'] != meta['status']:
        base = get(items, old['parent'])[0].parent if old.get('parent') else root / '.work'
        source = path.parent if old['kind'] in ('group', 'epic') else path
        destination = base / meta['status'] / source.name
        if not destination.resolve().is_relative_to((root / '.work').resolve()):
            fail(f'Destination escapes .work: {destination}')
        if destination.exists() or destination.is_symlink():
            fail(f'Destination exists: {destination}')
        destination.parent.mkdir(parents=True, exist_ok=True)
        # Update before rename; roll back if the filesystem rejects the move.
        write(path, meta, body)
        try:
            source.rename(destination)
        except OSError:
            write(path, old, items[identity][2])
            raise
    else:
        write(path, meta, body)


def initialize_states(board):
    for stage in STATES:
        (board / stage).mkdir()
        (board / stage / '.gitkeep').touch()


def initialize(root):
    board = root / '.work'
    if board.exists():
        fail('.work already exists; nothing changed')
    board.mkdir()
    initialize_states(board)
    (board / '.gitignore').write_text('.lock/\n.work-write-*\n', encoding='utf-8')
    (board / 'README.md').write_text('# Project work\n\nUse the installed CONVENTION.md. IDs survive moves. Read the current ticket and its ancestors, not the entire archive.\n', encoding='utf-8')
    print(board)


def create(root, items, args, archives=None):
    parent = args.parent
    if args.kind in ('story', 'task') and not parent:
        fail('A story/task needs --parent EPIC_ID')
    if parent:
        pp, pm, _, parent_record = lookup(items, archives, parent)
        if parent_record is not None:
            fail(f'Parent {parent} is archived; reopen the parent first')
        expected = 'group' if args.kind == 'epic' else 'epic'
        if args.kind == 'group' or pm['kind'] != expected:
            fail(f'{args.kind} requires a {expected} parent')
        if pm['status'] in COMPLETED:
            fail('Reopen the parent before adding work')
    identity = KINDS[args.kind] + '-' + uuid.uuid4().hex[:8]
    while identity in items or identity in archives.read():
        identity = KINDS[args.kind] + '-' + uuid.uuid4().hex[:8]
    slug = re.sub(r'[^a-z0-9]+', '-', args.title.lower()).strip('-')[:60] or 'ticket'
    base = (get(items, parent)[0].parent if parent else root / '.work') / 'backlog'
    if not base.resolve().is_relative_to((root / '.work').resolve()):
        fail(f'Destination escapes .work: {base}')
    base.mkdir(parents=True, exist_ok=True)
    path = base / f'{identity}-{slug}'
    if args.kind in ('epic', 'group'):
        path.mkdir()
        initialize_states(path)
        path = path / 'README.md'
    else:
        path = path.with_suffix('.md')
    meta = dict(id=identity, kind=args.kind, title=args.title, status='backlog', parent=parent,
                depends_on=[], implementer=None, reviewer=None, branch=None, base_branch=None)
    template = TOOLKIT / 'templates' / f'{args.kind}.md'
    body = template.read_text(encoding='utf-8').replace('{{title}}', args.title)
    write(path, meta, body)
    print(identity)


def restore(root, items, archives, record, status):
    """Recreate an archived ticket as a live file, preserving ID and content.

    The archive path is provenance, not a restore target: placement follows the
    current live parent structure. Existing files are never overwritten, and an
    existing container directory missing its README is completed in place.
    """
    meta, body = _archive_ticket(record['content'], accepted=False)
    identity = record['id']
    provenance = PurePosixPath(record['path'])
    if meta['parent']:
        pp, _, _, parent_record = lookup(items, archives, meta['parent'])
        if parent_record is not None:
            fail(f'{identity}: parent {meta["parent"]} is archived; reopen the parent first')
        base = pp.parent / status
    else:
        base = root / '.work' / status
    if meta['kind'] in ('group', 'epic'):
        container = base / provenance.parent.name
        destination = container / 'README.md'
        if container.is_symlink() or (container.exists() and not container.is_dir()):
            fail(f'Destination exists: {container}')
        if (container / 'README.md').exists() or (container / 'README.md').is_symlink():
            fail(f'Destination exists: {destination}')
        moves = []
        for child in children(items, identity):
            path, cm, _ = items[child]
            source = path.parent if cm['kind'] in ('group', 'epic') else path
            target = container / cm['status'] / source.name
            if source == target:
                continue
            if target.exists() or target.is_symlink():
                fail(f'Destination exists: {target}')
            if not target.resolve().is_relative_to((root / '.work').resolve()):
                fail(f'Destination escapes .work: {target}')
            moves.append((source, target))
        if not destination.resolve().is_relative_to((root / '.work').resolve()):
            fail(f'Destination escapes .work: {destination}')
        container.mkdir(parents=True, exist_ok=True)
        ensure_container_states(container)
        for source, target in moves:
            source.rename(target)  # Moving a live child container carries its descendants.
    else:
        destination = base / provenance.name
        if destination.exists() or destination.is_symlink():
            fail(f'Destination exists: {destination}')
        destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.resolve().is_relative_to((root / '.work').resolve()):
        fail(f'Destination escapes .work: {destination}')
    write(destination, dict(meta, status=status), body)


def transition(root, items, args, archives=None):
    target = {'start': 'wip', 'review': 'review', 'done': 'implemented', 'reopen': 'backlog'}[args.command]
    allowed = {'backlog': ('wip',), 'wip': ('review', 'backlog'),
               'review': ('implemented', 'wip', 'backlog'), 'implemented': ('backlog',), 'done': ('backlog',)}
    path, old, body, archived = lookup(items, archives, args.id)
    if args.command == 'reopen':
        return reopen_tickets(root, items, args, archives, old, body, archived)
    if archived is not None:
        fail(f'{args.id} is archived; reopen it first')
    if target not in allowed[old['status']]:
        fail(f"Cannot move {old['status']} to {target}")
    blocked = [d for d in old.get('depends_on', []) if lookup(items, archives, d)[1]['status'] not in COMPLETED]
    if blocked:
        fail('Unfinished dependencies: ' + ', '.join(blocked))
    if target == 'implemented':
        unfinished = [c for c in children(items, args.id) if get(items, c)[1]['status'] not in COMPLETED]
        if unfinished:
            fail('Unfinished children: ' + ', '.join(unfinished))
        if not args.evidence or not args.by:
            fail('Completion requires --by REVIEWER and --evidence TEXT')
        if old.get('reviewer') != args.by:
            fail('Completion --by must match the recorded reviewer; use work assign first')
        if re.search(r'^[ \t]*(?:[-+*]|[0-9]{1,9}[.)])[ \t]+\[ \](?=[ \t\r\n]|$)', body, re.MULTILINE):
            fail('Unchecked acceptance/completion items remain')
        stamp = datetime.now(timezone.utc).isoformat(timespec='seconds')
        body += f'\n## Acceptance record\n\n{stamp} — {args.by}: {args.evidence}\n'
    if old.get('parent'):
        _, _, _, parent_record = lookup(items, archives, old['parent'])
        if parent_record is not None:
            fail(f'Parent {old["parent"]} is archived; reopen the parent first')
    if args.dry_run:
        print(f'{args.id}: {old["status"]} -> {target}')
        return
    persist(root, items, args.id, dict(old, status=target), body)
    print(f'{args.id}: {target}')


def reopen_tickets(root, items, args, archives, old, body, archived):
    """Reopen a live or archived ticket, restoring archived ancestors as needed.

    Completed live ancestors move to WIP; archived ancestors are restored to
    WIP so the reopened ticket always has a live parent path. Archived records
    count as completed dependents and block reopening until they are reopened.
    """
    reopen = list(ancestors(items, args.id, archives))
    if (archived is None and old['status'] == 'backlog' and
            not any(lookup(items, archives, ancestor)[3] is not None for ancestor in reopen)):
        fail('Cannot move backlog to backlog')
    reopening = set()
    archived_records = {}
    for identity in [args.id, *reopen]:
        _, meta, _, record = lookup(items, archives, identity)
        if record is not None:
            archived_records[identity] = record
            reopening.add(identity)
        elif meta['status'] in COMPLETED:
            reopening.add(identity)
    dependents = [i for i, (_, m, _) in items.items()
                  if i not in reopening and m['status'] in COMPLETED
                  and reopening.intersection(m.get('depends_on', []))]
    for record in archives.read().values():
        if record['id'] in items:
            continue  # A live reopened copy supersedes the archived record.
        meta, _ = _archive_ticket(record['content'], accepted=False)
        if record['id'] not in reopening and reopening.intersection(meta.get('depends_on', [])):
            dependents.append(record['id'])
    if dependents:
        fail('Reopen completed dependents first: ' + ', '.join(dependents))
    if args.dry_run:
        for identity in [args.id, *reopen]:
            if identity in archived_records:
                print(f'{identity}: archived -> {"backlog" if identity == args.id else "wip"}')
            elif identity == args.id:
                print(f'{identity}: {old["status"]} -> backlog')
            elif get(items, identity)[1]['status'] in COMPLETED:
                print(f'{identity}: {get(items, identity)[1]["status"]} -> wip')
        return
    for ancestor in reversed(reopen):
        if ancestor in archived_records:
            items = records(root)
            restore(root, items, archives, archived_records[ancestor], 'wip')
        else:
            items = records(root)
            _, am, ab = get(items, ancestor)
            if am['status'] in COMPLETED:
                persist(root, items, ancestor, dict(am, status='wip'), ab)
    if args.id in archived_records:
        items = records(root)
        restore(root, items, archives, archived_records[args.id], 'backlog')
    else:
        items = records(root)
        persist(root, items, args.id, dict(old, status='backlog'), body)
    print(f'{args.id}: backlog')


JOURNAL_NAME = '.commit-journal.json'


def commit_branch(root):
    result = _git(root, 'symbolic-ref', '--quiet', '--short', 'HEAD')
    if result.returncode:
        head = _git(root, 'rev-parse', '--verify', 'HEAD')
        if head.returncode:
            fail('Cannot commit: the repository has no commits yet')
        fail('Cannot commit on a detached HEAD; check out a branch first')
    return result.stdout.strip()


def commit_select(items, branch, requested=None):
    """Return {identity: (path, meta, body)} for removable done tickets.

    A done leaf is removable when its explicit branch (if any) matches the
    current branch; an unset branch means the current branch. A done container
    is removable only when every live child is itself removable; archived
    children are already complete and never block removal.
    """
    removable = {}

    def eligible(identity):
        path, meta, body = items[identity]
        explicit = meta.get('branch')
        if meta['status'] != 'done' or (explicit and explicit != branch):
            return False
        if meta['kind'] in ('group', 'epic'):
            for child in children(items, identity):
                if not eligible(child):
                    return False
        removable[identity] = (path, meta, body)
        return True

    selected = {}
    for identity in sorted(items):
        if eligible(identity):
            selected[identity] = removable[identity]
    if requested:
        for identity in requested:
            if identity not in selected:
                fail(f'{identity}: unknown, unfinished, or not eligible for branch {branch}')
        selected = {identity: selected[identity] for identity in sorted(set(requested))}
        for identity in selected:
            missing = set(children(items, identity)) - selected.keys()
            if missing:
                fail(f'{identity}: select all live descendants explicitly or omit the container: '
                     + ', '.join(sorted(missing)))
    return selected


def commit_prepare(root, items, branch, requested=None, selection=None, merging=False):
    """Validate the board and return (entries, units) ready to archive.

    entries: list of (identity, path, relpath, content, meta).
    units: list of (relpath, identity) removal units (container dirs or files).
    """
    selected = commit_select(items, branch, requested) if selection is None else selection
    if not selected:
        fail('No accepted done tickets are eligible for the current branch')
    for state in ('MERGE_HEAD', 'CHERRY_PICK_HEAD', 'REVERT_HEAD', 'rebase-merge', 'rebase-apply', 'sequencer'):
        if merging and state == 'MERGE_HEAD':
            continue
        path = _git_ok(root, 'rev-parse', '--path-format=absolute', '--git-path', state).stdout.strip()
        if Path(path).exists():
            fail(f'Finish the in-progress Git operation ({state}) before archiving')
    unmerged = _git(root, 'ls-files', '-u')
    if unmerged.returncode == 0 and unmerged.stdout.strip():
        fail('Resolve merge conflicts before archiving')
    untracked = _git(root, 'ls-files', '--others', '--exclude-standard', '--', '.work')
    if untracked.returncode == 0 and untracked.stdout.strip():
        names = [n for n in untracked.stdout.splitlines() if not n.endswith(JOURNAL_NAME)]
        if names:
            fail('Unstaged board files detected; run `git add .work` first: ' + ', '.join(names[:5]))
    if _git(root, 'diff', '--quiet', '--', '.work').returncode != 0:
        fail('The board has unstaged changes; stage them with `git add .work` first')
    entries = []
    for identity in sorted(selected):
        path, meta, body = selected[identity]
        relpath = path.relative_to(root).as_posix()
        ls = _git(root, 'ls-files', '--stage', '--', relpath)
        if ls.returncode != 0 or not ls.stdout.strip():
            fail(f'{identity}: not tracked by Git; run `git add` first')
        mode = ls.stdout.split()[0]
        if mode not in ('100644', '100755') or path.is_symlink():
            fail(f'{identity}: not a regular file (mode {mode})')
        blob = ls.stdout.split()[1]
        if _git_ok(root, 'hash-object', '--no-filters', '--', relpath).stdout.strip() != blob:
            fail(f'{identity}: staged bytes differ from working bytes; stage the exact ticket without filters')
        entries.append((identity, path, relpath, path.read_bytes().decode('utf-8'), meta))
    units = []
    for identity, path, relpath, _, meta in entries:
        if meta['kind'] in ('group', 'epic'):
            allowed = ({entry[1] for entry in entries} if selection is None else
                       {p for p, m, _ in items.values() if m['status'] in COMPLETED})
            for child in path.parent.rglob('*'):
                if child.is_symlink() or (child.is_file() and child not in allowed and
                                          not (child.name == '.gitkeep' and child.stat().st_size == 0)):
                    fail(f'{identity}: unknown ancillary file in container; move it explicitly first: {child}')
            units.append((path.parent.relative_to(root).as_posix(), identity))
        else:
            units.append((relpath, identity))
    # A selected ancestor already covers its descendants. Never delete twice.
    units = [(unit, identity) for unit, identity in units
             if not any(unit.startswith(other + '/') for other, _ in units if other != unit)]
    return entries, units


def commit_message(subject, entries, verb='archive'):
    entries = sorted(entries, key=lambda entry: entry[0])
    titles = [' '.join(entry[4]['title'].split()) for entry in entries]
    # Validate complete acceptance without putting the records in the message.
    for identity, _, path, content, _ in entries:
        _archive_record(dict(id=identity, path=path, content=content,
                             sha256=hashlib.sha256(content.encode('utf-8')).hexdigest()))
    if subject is None:
        kinds = {entry[4]['kind'] for entry in entries}
        kind = 'feat' if kinds.intersection({'epic', 'story', 'group'}) else 'task'
        description = titles[0] if len(entries) == 1 else f'{verb} {len(entries)} completed tickets'
        subject = f'{kind}: {description}'
        if len(subject) > 72:
            subject = subject[:69].rstrip() + '...'
    summary = '\n'.join(f'- {entry[0]} — {title}' for entry, title in zip(entries, titles))
    return f'{subject}\n\n{ARCHIVE_HEADING}\n\n{summary}\n'


def commit_snapshot_needed(root, entries):
    for _, _, path, _, _ in entries:
        old = _git_ok(root, 'ls-tree', 'HEAD', '--', path).stdout.split()
        staged = _git_ok(root, 'ls-files', '--stage', '--', path).stdout.split()
        if len(old) < 3 or old[0] != staged[0] or old[2] != staged[1]:
            return True
    return False


def commit_snapshot_message(message):
    ids = re.findall(r'^- ([GEST]-[0-9a-f]{8}) — ', message, re.MULTILINE)
    return ('chore: preserve accepted tickets before archival\n\n'
            'Record staged changes and full ticket files before archival.\n'
            'The following archive commit lists their titles.\n\n'
            'Tickets: ' + ', '.join(ids) + '\n')


def commit_preview(root, branch, entries, units, message):
    head = _git(root, 'rev-parse', '--verify', 'HEAD')
    if head.returncode == 0:
        staged = _git(root, 'diff', '--cached', '--name-status').stdout
    else:
        staged = ''.join(f'A\t{name}\n' for name in _git(root, 'ls-files').stdout.splitlines())
    print(f'Branch: {branch}')
    print('Selected: ' + ', '.join(sorted(entry[0] for entry in entries)))
    print('Removals:')
    for unit, _ in units:
        print(f'  {unit}')
    print('Staged changes:')
    print(staged.rstrip() or '  (none)')
    if commit_snapshot_needed(root, entries):
        print('Snapshot commit required (accepted files are not yet preserved in HEAD):')
        print(commit_snapshot_message(message), end='')
    else:
        print('Snapshot: accepted files already preserved in HEAD; no extra commit.')
    print('Proposed commit message:')
    print('---')
    print(message, end='')
    print('---')


def commit_index(root):
    path = Path(_git_ok(root, 'rev-parse', '--path-format=absolute', '--git-path', 'index').stdout.strip())
    return path


def commit_journal(path, data):
    fd, name = tempfile.mkstemp(prefix='.work-write-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(data, stream, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def commit_publication(root, data):
    """Only the exact expected child commit proves this transaction published."""
    head = _git_ok(root, 'rev-parse', '--verify', 'HEAD').stdout.strip()
    if commit_branch(root) != data['branch']:
        fail('Recovery blocked: branch changed; restore the original checkout context first')
    if head == data['head_before']:
        return None
    def matches(oid, parent, tree, message):
        return (_git_ok(root, 'show', '-s', '--format=%P', oid).stdout.strip() == parent and
                _git_ok(root, 'show', '-s', '--format=%T', oid).stdout.strip() == tree and
                _git_ok(root, 'show', '-s', '--format=%B', oid).stdout.rstrip('\n') == message.rstrip('\n'))

    source = data.get('source')
    if source and matches(head, data['head_before'], source['tree'], source['message']):
        return None  # Snapshot exists, but no archival: restore files, retain it.
    parent = _git_ok(root, 'show', '-s', '--format=%P', head).stdout.strip()
    source_matches = (parent == data['head_before'] if not source else
                      bool(re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', parent)) and
                      matches(parent, data['head_before'], source['tree'], source['message']))
    if not source_matches or not matches(head, parent, data['tree_after'], data['message']):
        fail('Recovery blocked: HEAD differs from the expected archive commit; journal retained')
    return head


def commit_recover(root):
    journal_path = root / '.work' / JOURNAL_NAME
    if not journal_path.exists():
        print('Nothing to recover (no commit journal).')
        return
    data = json.loads(journal_path.read_text(encoding='utf-8'))
    if data.get('version') == 3:
        return retained_recover(root, data)
    if data.get('version') != 2:
        fail('Legacy/unknown commit journal: retain it and recover files manually; publication cannot be inferred safely')
    published = commit_publication(root, data)
    index = commit_index(root)
    before = base64.b64decode(data['index_before'])
    after = base64.b64decode(data['index_after'])
    current = index.read_bytes()
    if current != before and not (published and current == after):
        fail('Recovery blocked: index changed; preserve staged edits and journal before manual recovery')
    files = []
    for relpath, b64 in data['files'].items():
        target = root / relpath
        if (not relpath.startswith('.work/') or '..' in PurePosixPath(relpath).parts or
                not target.resolve().is_relative_to((root / '.work').resolve()) or target.is_symlink()):
            fail('Recovery blocked: unsafe journal path')
        content = base64.b64decode(b64)
        if target.exists() and (not target.is_file() or target.read_bytes() != content or
                                target.stat().st_mode & 0o777 != data['modes'][relpath]):
            fail(f'Recovery blocked: file changed: {relpath}; journal retained')
        if published and target.exists():
            fail(f'Recovery blocked: archived path exists: {relpath}; journal retained')
        files.append((target, relpath, content))
    lock_path = Path(str(index) + '.lock')
    try:
        fd = os.open(lock_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        fail('Recovery blocked: Git index is locked; journal retained')
    try:
        with os.fdopen(fd, 'wb') as stream:
            os.fchmod(stream.fileno(), index.stat().st_mode & 0o777)
            if index.read_bytes() != current:
                fail('Recovery blocked: index changed during recovery')
            stream.write(after if published else before)
            stream.flush()
            os.fsync(stream.fileno())
        if not published:
            for target, relpath, content in files:
                if not target.exists():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with target.open('xb') as stream:
                        stream.write(content)
                    target.chmod(data['modes'][relpath])
        os.replace(lock_path, index)
        journal_path.unlink()
    finally:
        if lock_path.exists():
            lock_path.unlink()
    if published:
        print(f'Recovered: the commit was already published ({published}); index resynced and journal cleared.')
    else:
        print('Recovered: restored ticket files; no archive commit was made.')
        head = _git_ok(root, 'rev-parse', 'HEAD').stdout.strip()
        if head != data['head_before']:
            print(f'Snapshot commit {head} was retained; archival did not complete. Retry after resolving the failure.')


def commit_apply(root, branch, entries, units, message):
    journal_path = root / '.work' / JOURNAL_NAME
    if journal_path.exists():
        fail('A previous commit was interrupted; run `work commit --recover` first')
    head_before = _git_ok(root, 'rev-parse', '--verify', 'HEAD').stdout.strip()
    index = commit_index(root)
    index_before = index.read_bytes()
    for identity, path, _, content, _ in entries:
        if path.is_symlink() or path.read_bytes() != content.encode('utf-8'):
            fail(f'Stale selection: {identity} changed; no commit was made')
    files = {}
    for unit, _ in units:
        path = root / unit
        if path.is_dir() and not path.is_symlink():
            for child in sorted(path.rglob('*')):
                if child.is_file():
                    files[child.relative_to(root).as_posix()] = child.read_bytes()
        elif path.exists():
            files[unit] = path.read_bytes()
    for identity, _, relpath, content, _ in entries:
        if files.get(relpath) != content.encode('utf-8'):
            fail(f'Stale selection: {identity} changed; no commit was made')
    journal = {
        'version': 2,
        'subject': message.split('\n', 1)[0],
        'branch': branch,
        'selected': [{'id': entry[0], 'path': entry[2]} for entry in entries],
        'files': {relpath: base64.b64encode(b).decode('ascii') for relpath, b in files.items()},
        'commit': None,
        'head_before': head_before,
        'message': message,
        'index_before': base64.b64encode(index_before).decode('ascii'),
        'modes': {relpath: (root / relpath).stat().st_mode & 0o777 for relpath in files},
    }
    tmpdir = None
    try:
        tmpdir = tempfile.mkdtemp(prefix='work-commit-')
        env = {'GIT_INDEX_FILE': os.path.join(tmpdir, 'index')}
        Path(env['GIT_INDEX_FILE']).write_bytes(index_before)
        source_env = {'GIT_INDEX_FILE': os.path.join(tmpdir, 'source-index')}
        if commit_snapshot_needed(root, entries):
            Path(source_env['GIT_INDEX_FILE']).write_bytes(index_before)
            journal['source'] = dict(tree=_git_ok(root, 'write-tree', env=source_env).stdout.strip(),
                                     message=commit_snapshot_message(message))
        removal_paths = [unit for unit, _ in units]
        _git_ok(root, 'rm', '-r', '-f', '--cached', '-q', '--', *removal_paths, env=env)
        journal['tree_after'] = _git_ok(root, 'write-tree', env=env).stdout.strip()
        journal['index_after'] = base64.b64encode(Path(env['GIT_INDEX_FILE']).read_bytes()).decode('ascii')
        if (index.read_bytes() != index_before or commit_branch(root) != branch or
                _git_ok(root, 'rev-parse', 'HEAD').stdout.strip() != head_before):
            fail('Stale selection: HEAD, branch, or index changed; no commit was made')
        for relpath, content in files.items():
            if (root / relpath).read_bytes() != content:
                fail(f'Stale selection: {relpath} changed; no commit was made')
        commit_journal(journal_path, journal)
        expected_head = head_before
        if journal.get('source'):
            result = _git(root, 'commit', '--cleanup=verbatim', '-F', '-',
                          input=journal['source']['message'], env=source_env)
            if result.returncode:
                fail(f'git commit failed while preserving the snapshot: {result.stderr.strip() or result.stdout.strip()}')
            expected_head = _git_ok(root, 'rev-parse', 'HEAD').stdout.strip()
            # Reject modifying hooks before any ticket deletion.
            if expected_head == head_before or commit_publication(root, journal) is not None:
                fail('Unexpected publication while preserving the snapshot')
            print(f'Recorded ticket snapshot {expected_head[:12]}')
        for unit, _ in units:
            path = root / unit
            if path.is_dir() and not path.is_symlink():
                shutil.rmtree(path)
            elif path.exists():
                path.unlink()
        head_now = _git(root, 'rev-parse', '--verify', 'HEAD')
        head_now = head_now.stdout.strip() if head_now.returncode == 0 else None
        if head_now != expected_head or commit_branch(root) != branch or index.read_bytes() != index_before:
            fail('Stale selection: HEAD moved during the commit; no commit was made')
        result = _git(root, 'commit', '--cleanup=verbatim', '-F', '-', input=message, env=env)
        if result.returncode:
            fail(f'git commit failed: {result.stderr.strip() or result.stdout.strip()}')
        oid = _git(root, 'rev-parse', 'HEAD').stdout.strip()
        journal['commit'] = oid
        commit_journal(journal_path, journal)
        commit_recover(root)
        first = result.stdout.strip().splitlines()[0] if result.stdout.strip() else message.split('\n', 1)[0]
        print(f'Committed {oid[:12]}: {first}')
        return oid
    except (ValueError, OSError) as error:
        if journal_path.exists():
            try:
                commit_recover(root)
            except (ValueError, OSError) as recovery_error:
                fail(f'{error}. Recovery needs attention: {recovery_error}. '
                     f'Commit may have published (HEAD: {_git(root, "rev-parse", "HEAD").stdout.strip()}); '
                     'retain the journal and run `work commit --recover` after resolving the conflict')
        raise error
    finally:
        if tmpdir:
            shutil.rmtree(tmpdir, ignore_errors=True)


def cleanup_command(root, items, archives, args):
    top = Path(_git_ok(root, 'rev-parse', '--show-toplevel').stdout.strip()).resolve()
    if top != root.resolve():
        fail('Archive commits require .work at the Git worktree root')
    subject = args.message.strip() if args.message is not None else None
    if subject is not None and ('\n' in subject or '\r' in subject or not subject):
        fail('Commit subject must be a single line')
    branch = commit_branch(root)
    _git_ok(root, 'var', 'GIT_AUTHOR_IDENT')
    _git_ok(root, 'var', 'GIT_COMMITTER_IDENT')
    entries, units = commit_prepare(root, items, branch, args.ids)
    message = commit_message(subject, entries)
    destination = None
    if args.push:
        remote = _git(root, 'config', '--get', f'branch.{branch}.remote').stdout.strip()
        merge = _git(root, 'config', '--get', f'branch.{branch}.merge').stdout.strip()
        if remote in ('', '.') or remote.startswith('-') or not merge.startswith('refs/heads/'):
            fail('Explicit --push requires a configured remote branch upstream; '
                 'configure it explicitly with git branch --set-upstream-to=REMOTE/BRANCH before retrying')
        if _git(root, 'config', '--bool', '--get', f'remote.{remote}.mirror').stdout.strip() == 'true':
            fail('Explicit --push does not support a mirror remote; configure a branch-only upstream first')
        destination = (remote, merge)
    if args.dry_run:
        commit_preview(root, branch, entries, units, message)
        if destination:
            print(f'Push after commit: {destination[0]} HEAD:{destination[1]} (no network in dry run)')
        return
    oid = commit_apply(root, branch, entries, units, message)
    if destination:
        result = _git(root, 'push', '--no-mirror', '--no-follow-tags', '--recurse-submodules=no',
                      destination[0], f'{oid}:{destination[1]}')
        if result.returncode:
            fail(f'Commit {oid} succeeded locally; push failed: {result.stderr.strip()}. '
                 'Retry with git push after resolving the remote error; do not repeat work commit')
        print(f'Pushed {oid} to {destination[0]}:{destination[1]}')


def completed_queue(items, branch, requested):
    selected = {i: value for i, value in items.items()
                if value[1]['status'] == 'implemented' and value[1].get('branch') in (None, '', branch)}
    if requested:
        for identity in requested:
            if identity not in selected:
                fail(f'{identity}: not implemented or not eligible for branch {branch}')
        wanted = set(requested)
        for identity in list(wanted):
            path, meta, _ = items[identity]
            if meta['kind'] in ('epic', 'group'):
                wanted.update(i for i in selected if items[i][0].is_relative_to(path.parent))
        selected = {i: value for i, value in selected.items() if i in wanted}
    for identity, (_, meta, _) in selected.items():
        if meta['kind'] in ('epic', 'group'):
            descendants = [i for i in items if i != identity and items[i][0].is_relative_to(items[identity][0].parent)]
            if any(items[i][1]['status'] not in COMPLETED or
                   (items[i][1]['status'] == 'implemented' and i not in selected) for i in descendants):
                fail(f'{identity}: all descendants must be accepted and queued for this branch')
    if not selected:
        fail('No implemented tickets are eligible; committed done tickets are retained until work merge')
    return selected


def retained_plan(root, items, selected, units):
    destinations = {}

    def destination(identity):
        if identity not in destinations:
            path, meta, _ = get(items, identity)
            if meta.get('parent') and meta['parent'] not in items:
                fail(f'{identity}: reopen its archived parent before committing')
            base = destination(meta['parent']).parent if meta.get('parent') else root / '.work'
            status = 'done' if identity in selected else meta['status']
            destinations[identity] = (base / status / path.parent.name / 'README.md'
                                      if meta['kind'] in ('epic', 'group') else base / status / path.name)
        return destinations[identity]

    for identity in selected:
        destination(identity)
    before, after = {}, {}
    containers = [(items[i][0].parent, destinations[i].parent) for i in selected
                  if items[i][1]['kind'] in ('epic', 'group')]
    containers.sort(key=lambda pair: len(pair[0].parts), reverse=True)
    paths = {p: i for i, (p, _, _) in items.items()}
    for unit, _ in units:
        source = root / unit
        for path in sorted(source.rglob('*')) if source.is_dir() else [source]:
            if not path.is_file():
                continue
            if path.is_symlink():
                fail(f'Refusing symlink: {path}')
            rel = path.relative_to(root).as_posix()
            before[rel] = (path.read_bytes(), path.stat().st_mode & 0o777)
            identity = paths.get(path)
            if identity in selected:
                _, meta, body = items[identity]
                content = ('---\n' + json.dumps(dict(meta, status='done'), indent=2, ensure_ascii=False)
                           + '\n---\n' + body).encode('utf-8')
                target = destinations[identity]
            else:
                content, target = before[rel][0], path
                for old, new in containers:
                    if path.is_relative_to(old):
                        target = new / path.relative_to(old)
                        break
            if not target.resolve().is_relative_to((root / '.work').resolve()):
                fail(f'Destination escapes .work: {target}')
            target_rel = target.relative_to(root).as_posix()
            if target_rel in after or (target != path and (target.exists() or target.is_symlink())):
                fail(f'Destination exists: {target}')
            after[target_rel] = (content, before[rel][1])
    entries = [(i, destinations[i], destinations[i].relative_to(root).as_posix(),
                after[destinations[i].relative_to(root).as_posix()][0].decode('utf-8'),
                dict(items[i][1], status='done')) for i in sorted(selected)]
    return before, after, entries


def encode_files(files):
    return {path: dict(content=base64.b64encode(content).decode('ascii'), mode=mode)
            for path, (content, mode) in files.items()}


def decode_files(files):
    return {path: (base64.b64decode(value['content']), value['mode']) for path, value in files.items()}


def file_map_apply(root, old, new):
    for rel, (content, mode) in new.items():
        path = root / rel
        if path.is_symlink() or (path.exists() and rel not in old and
                                (not path.is_file() or path.read_bytes() != content)):
            fail(f'Destination changed: {path}; refusing to overwrite it')
    for rel in old.keys() - new.keys():
        path = root / rel
        if path.exists():
            path.unlink()
        parent = path.parent
        while parent != root / '.work':
            try:
                parent.rmdir()
            except OSError:
                break
            parent = parent.parent
    for rel, (content, mode) in new.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        path.chmod(mode)


def retained_recover(root, data):
    published = commit_publication(root, data)
    before, after = decode_files(data['before_files']), decode_files(data['after_files'])
    index = commit_index(root)
    original, final = base64.b64decode(data['index_before']), base64.b64decode(data['index_after'])
    current = index.read_bytes()
    if current != original and not (published and current == final):
        fail('Recovery blocked: index changed; retain the journal and staged work')
    for rel in before.keys() | after.keys():
        path = root / rel
        if (not rel.startswith('.work/') or '..' in PurePosixPath(rel).parts or path.is_symlink() or
                not path.resolve().is_relative_to((root / '.work').resolve())):
            fail('Recovery blocked: unsafe retained-ticket path')
        if path.exists():
            if not path.is_file() or (path.read_bytes(), path.stat().st_mode & 0o777) not in (before.get(rel), after.get(rel)):
                fail(f'Recovery blocked: file changed: {rel}; journal retained')
        if published and (rel not in after and path.exists() or rel in after and not path.exists()):
            fail(f'Recovery blocked: committed ticket layout changed: {rel}')
    lock = Path(str(index) + '.lock')
    try:
        fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        fail('Recovery blocked: Git index is locked; journal retained')
    try:
        with os.fdopen(fd, 'wb') as stream:
            os.fchmod(stream.fileno(), index.stat().st_mode & 0o777)
            if index.read_bytes() != current:
                fail('Recovery blocked: index changed during recovery')
            if not published:
                file_map_apply(root, after, before)
            stream.write(final if published else original)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(lock, index)
        (root / '.work' / JOURNAL_NAME).unlink()
    finally:
        if lock.exists():
            lock.unlink()
    print('Recovered: retained done tickets committed.' if published else
          'Recovered: implemented tickets restored; no commit was made.')


def retained_apply(root, branch, before, after, message):
    index = commit_index(root)
    original = index.read_bytes()
    head = _git_ok(root, 'rev-parse', 'HEAD').stdout.strip()
    journal_path = root / '.work' / JOURNAL_NAME
    if journal_path.exists():
        fail('A previous commit needs recovery; run work commit --recover')
    with tempfile.TemporaryDirectory(prefix='work-retain-') as temp:
        private = Path(temp) / 'index'
        private.write_bytes(original)
        env = {'GIT_INDEX_FILE': str(private)}
        changes = ''.join(f'0 {"0" * len(head)}\t{path}\0' for path in before)
        for path, (content, mode) in after.items():
            blob = _git_ok(root, 'hash-object', '-w', '--stdin', input=content.decode('utf-8')).stdout.strip()
            changes += f'{"100755" if mode & 0o111 else "100644"} {blob}\t{path}\0'
        _git_ok(root, 'update-index', '-z', '--index-info', input=changes, env=env)
        data = dict(version=3, branch=branch, head_before=head, message=message,
                    tree_after=_git_ok(root, 'write-tree', env=env).stdout.strip(),
                    index_before=base64.b64encode(original).decode('ascii'),
                    index_after=base64.b64encode(private.read_bytes()).decode('ascii'),
                    before_files=encode_files(before), after_files=encode_files(after))
        if (index.read_bytes() != original or commit_branch(root) != branch or
                _git_ok(root, 'rev-parse', 'HEAD').stdout.strip() != head):
            fail('Stale selection: HEAD, branch or index changed')
        for path, (content, mode) in before.items():
            current = root / path
            if current.is_symlink() or current.read_bytes() != content or current.stat().st_mode & 0o777 != mode:
                fail(f'Stale selection: {path} changed')
        commit_journal(journal_path, data)
        try:
            file_map_apply(root, before, after)
            result = _git(root, 'commit', '--cleanup=verbatim', '-F', '-', input=message, env=env)
            if result.returncode:
                fail(f'git commit failed: {result.stderr.strip() or result.stdout.strip()}')
            oid = _git_ok(root, 'rev-parse', 'HEAD').stdout.strip()
            retained_recover(root, data)
            return oid
        except (ValueError, OSError) as error:
            try:
                retained_recover(root, data)
            except (ValueError, OSError) as recovery:
                fail(f'{error}; recovery needs attention: {recovery}. Retain the journal; run work commit --recover')
            raise


def commit_command(root, items, archives, args):
    top = Path(_git_ok(root, 'rev-parse', '--show-toplevel').stdout.strip()).resolve()
    if top != root.resolve():
        fail('Ticket commits require .work at the Git worktree root')
    branch = commit_branch(root)
    subject = args.message.strip() if args.message is not None else None
    if subject is not None and (not subject or '\n' in subject or '\r' in subject):
        fail('Commit subject must be a single line')
    _git_ok(root, 'var', 'GIT_AUTHOR_IDENT')
    _git_ok(root, 'var', 'GIT_COMMITTER_IDENT')
    selected = completed_queue(items, branch, args.ids)
    _, units = commit_prepare(root, items, branch, selection=selected)
    before, after, entries = retained_plan(root, items, selected, units)
    message = commit_message(subject, entries, verb='complete')
    destination = None
    if args.push:
        remote = _git(root, 'config', '--get', f'branch.{branch}.remote').stdout.strip()
        merge = _git(root, 'config', '--get', f'branch.{branch}.merge').stdout.strip()
        if remote in ('', '.') or remote.startswith('-') or not merge.startswith('refs/heads/'):
            fail('Explicit --push requires a configured remote branch upstream')
        if _git(root, 'config', '--bool', '--get', f'remote.{remote}.mirror').stdout.strip() == 'true':
            fail('Explicit --push does not support a mirror remote')
        destination = (remote, merge)
    if args.dry_run:
        print(f'Branch: {branch}\nSelected: ' + ', '.join(sorted(selected)))
        print('Retain tickets: implemented -> done (no deletions)')
        print('Retained ticket paths:')
        for identity, _, relative, _, _ in entries:
            print(f'  {identity} -> {relative}')
        print('Staged changes:\n' + (_git_ok(root, 'diff', '--cached', '--name-status').stdout.rstrip() or '  (none)'))
        print('Proposed commit message:\n' + message, end='')
        if destination:
            print(f'Push after commit: {destination[0]} HEAD:{destination[1]} (no network in dry run)')
        return
    oid = retained_apply(root, branch, before, after, message)
    print(f'Committed {oid[:12]}; tickets retained in done until work merge')
    if destination:
        result = _git(root, 'push', '--no-mirror', '--no-follow-tags', '--recurse-submodules=no',
                      destination[0], f'{oid}:{destination[1]}')
        if result.returncode:
            fail(f'Commit {oid} succeeded locally; push failed: {result.stderr.strip()}. Retry git push, not work commit')


def merge_journal_path(root, identity):
    common = Path(_git_ok(root, 'rev-parse', '--path-format=absolute', '--git-common-dir').stdout.strip())
    return common / 'worktree-tickets' / f'merge-{identity}.json'


def merge_target_worktree(root, branch):
    for block in _git_ok(root, 'worktree', 'list', '--porcelain', '-z').stdout.split('\0\0'):
        fields = dict(field.split(' ', 1) for field in block.split('\0') if ' ' in field)
        if fields.get('branch') == f'refs/heads/{branch}':
            return Path(fields['worktree'])
    return None


def merge_clean(root):
    if _git_ok(root, 'status', '--porcelain', '--untracked-files=all').stdout:
        fail(f'Merge requires a clean checkout: {root}; commit or preserve changes explicitly first')
    if (root / '.work' / JOURNAL_NAME).exists():
        fail(f'An interrupted ticket commit needs recovery in {root}')
    for state in ('MERGE_HEAD', 'CHERRY_PICK_HEAD', 'REVERT_HEAD', 'rebase-merge', 'rebase-apply', 'sequencer'):
        path = Path(_git_ok(root, 'rev-parse', '--path-format=absolute', '--git-path', state).stdout.strip())
        if path.exists():
            fail(f'Finish the in-progress Git operation ({state}) in {root}')


def merge_matches(root, oid, parent, tree, message):
    return (_git_ok(root, 'show', '-s', '--format=%P', oid).stdout.strip() == parent and
            _git_ok(root, 'show', '-s', '--format=%T', oid).stdout.strip() == tree and
            _git_ok(root, 'show', '-s', '--format=%B', oid).stdout.rstrip('\n') == message.rstrip('\n'))


def merge_board(root, revision):
    """Read lifecycle files only; toolkit/runtime files remain ordinary Git changes."""
    result = {}
    objects = ArchiveObjects(root)
    files = []
    listing = _git_ok(root, 'ls-tree', '-r', '-z', revision, '--', '.work').stdout
    for entry in listing.split('\0'):
        if not entry:
            continue
        header, relative = entry.split('\t', 1)
        if relative.split('/')[1] not in STATES:
            continue
        mode, kind, oid = header.split()
        if mode not in ('100644', '100755') or kind != 'blob':
            fail(f'Nonregular board file at {revision}: {relative}')
        files.append((relative, mode, oid))
    objects.load([oid for _, _, oid in files])
    for relative, mode, oid in files:
        content = objects.cache[oid][1].decode('utf-8')
        result[relative] = [content, mode]
    return result


def merge_subtree(board, identity):
    return {p: value for p, value in board.items()
            if any(part.startswith(identity + '-') for part in p.split('/'))}


def merge_signature(board, identity):
    return {_archive_ticket(value[0], accepted=False)[0]['id']: value[0]
            for p, value in merge_subtree(board, identity).items() if p.endswith('.md')}


def merge_revision_signature(root, revision, identity):
    board = merge_board(root, revision)
    signature = merge_signature(board, identity)
    history = archive_history(root, revision)
    live = {_archive_ticket(text, accepted=False)[0]['id']
            for p, (text, _) in board.items() if p.endswith('.md')}
    while True:
        additions = {i: record['content'] for i, record in history.items()
                     if i not in live and i not in signature and
                     _archive_ticket(record['content'])[0]['parent'] in signature}
        if not additions:
            return signature
        signature.update(additions)


def merge_board_plan(root, source, target, identity, retain=False):
    """Keep the target's branch-local siblings; refuse divergent source edits."""
    base = _git_ok(root, 'merge-base', source, target).stdout.strip()
    before, incoming, current = [merge_board(root, ref) for ref in (base, source, target)]
    selected = merge_subtree(incoming, identity)
    old_selected = merge_subtree(before, identity)
    target_selected = merge_subtree(current, identity)
    archived_target = not target_selected and archive_history(root, target).get(identity)
    if target_selected != old_selected and target_selected != selected and not archived_target:
        fail('Target has conflicting ticket moves/edits in the selected container; reconcile explicitly first')
    def outside(board):
        inside = merge_subtree(board, identity)
        return {p: v for p, v in board.items() if p not in inside}

    b, s, t = map(outside, (before, incoming, current))
    for relative in set(b) | set(s):
        if s.get(relative) != b.get(relative) and s.get(relative) != t.get(relative):
            if retain or t.get(relative) != b.get(relative):
                fail(f'Source changes unrelated board state: {relative}; reconcile sibling/group moves first')
            if relative in s:
                t[relative] = s[relative]
            else:
                t.pop(relative, None)
    return dict(t, **selected)


def merge_restore_board(root, planned):
    """Resolve board-only Git rename conflicts using the preflighted tree."""
    tracked = _git_ok(root, 'ls-files', '-z', '--', '.work').stdout.split('\0')
    paths = {p for p in tracked if p and p.split('/')[1] in STATES}
    for relative in sorted(paths - planned.keys()):
        path = root / relative
        if path.is_symlink() or path.is_file():
            path.unlink()
        elif path.exists():
            fail(f'Unexpected directory at board file: {path}')
        _git_ok(root, 'update-index', '--force-remove', '--', relative)
    for relative, (content, mode) in planned.items():
        path = root / relative
        if path.is_symlink() or (path.exists() and not path.is_file()):
            fail(f'Unsafe merge board destination: {path}')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8', newline='')
        path.chmod(int(mode, 8) & 0o777)
        _git_ok(root, 'add', '--', relative)


def merge_saved_descendants(root, items, archives, identity, container_path):
    """Materialize accepted descendants recursively, following saved parent IDs."""
    pending = {i: record for i, record in archives.read().items() if i not in items}
    destinations = {i: value[0].parent for i, value in items.items()
                    if value[1]['kind'] in ('group', 'epic') and
                    value[0].is_relative_to(container_path)}
    destinations[identity] = container_path
    saved, entries = {}, []
    while True:
        found = False
        for child, record in list(pending.items()):
            cm, _ = _archive_ticket(record['content'])
            if cm.get('parent') not in destinations:
                continue
            name = PurePosixPath(record['path'])
            destination = destinations[cm['parent']] / 'done' / (name.parent.name if cm['kind'] in ('group', 'epic') else name.name)
            if cm['kind'] in ('group', 'epic'):
                destinations[child] = destination
                destination /= 'README.md'
            relative = destination.relative_to(root).as_posix()
            if relative in saved:
                fail(f'Duplicate archived destination: {relative}')
            saved[relative] = record['content']
            entries.append((child, destination, relative, record['content'], cm))
            del pending[child]
            found = True
        if not found:
            return saved, entries


def merge_group_revisions(root, entries, source, saved):
    """A final release may not squash away a newer, unlanded epic approval."""
    board = merge_board(root, source)
    board.update({p: [text, '100644'] for p, text in saved.items()})
    for identity, _, _, _, meta in entries:
        if meta['kind'] != 'epic':
            continue
        branch = meta.get('branch')
        if not branch or meta.get('base_branch') != commit_branch(root):
            fail(f'{identity}: epic must record its group branch as base_branch')
        ref = _git(root, 'rev-parse', '--verify', f'refs/heads/{branch}')
        if ref.returncode == 0:
            tip = ref.stdout.strip()
            if (_git(root, 'merge-base', '--is-ancestor', tip, source).returncode or
                    merge_revision_signature(root, tip, identity) != merge_signature(board, identity)):
                fail(f'{identity}: accepted epic revision is not integrated on the group branch')
        else:
            # Deleted local branches are fine if a retained merge parent proves landing.
            landed = False
            for line in _git_ok(root, 'log', '--merges', '--format=%P', source).stdout.splitlines():
                for parent in line.split()[1:]:
                    if merge_revision_signature(root, parent, identity) == merge_signature(board, identity):
                        landed = True
                        break
                if landed:
                    break
            if not landed:
                fail(f'{identity}: no integrated accepted epic revision found; integrate the epic first')


def merge_command(root, items, archives, args):
    identity = args.id
    if not re.fullmatch(r'[GE]-[0-9a-f]{8}', identity):
        fail('work merge requires a group or epic ID')
    if Path(_git_ok(root, 'rev-parse', '--show-toplevel').stdout.strip()).resolve() != root.resolve():
        fail('Container merges require .work at the Git worktree root')
    journal_path = merge_journal_path(root, identity)
    if journal_path.exists():
        if not args.recover:
            fail(f'A container merge needs recovery; run work merge {identity} --recover')
        if args.dry_run:
            print(journal_path.read_text(encoding='utf-8'))
            return
        data = json.loads(journal_path.read_text(encoding='utf-8'))
        if data.get('version') not in (1, 2) or data.get('epic') != identity:
            fail('Unsupported or mismatched container merge journal; retain it for inspection')
    else:
        if args.recover:
            fail('No interrupted container merge to recover')
        path, meta, _ = get(items, identity)
        source = commit_branch(root)
        target = meta.get('base_branch')
        if meta.get('branch') != source or not target or target == source:
            fail('Container branch must match this checkout and have a different recorded base_branch')
        retain = False
        if meta.get('parent'):
            _, parent, _, _ = lookup(items, archives, meta['parent'])
            if target != parent.get('branch') or parent['status'] != 'wip':
                fail('A child epic must target its recorded WIP parent-group branch')
            retain = True
        if meta['status'] != 'done':
            fail('Container must be approved and committed to done before work merge; children are retained until then')
        merge_clean(root)
        _git_ok(root, 'var', 'GIT_AUTHOR_IDENT')
        _git_ok(root, 'var', 'GIT_COMMITTER_IDENT')
        source_head = _git_ok(root, 'rev-parse', 'HEAD').stdout.strip()
        target_head = _git_ok(root, 'rev-parse', '--verify', f'refs/heads/{target}').stdout.strip()
        if retain and _git(root, 'merge-base', '--is-ancestor', source_head, target_head).returncode == 0:
            fail('This accepted epic is already integrated; reopen and re-approve it before another merge')
        previous = archive_history(root, target_head).get(identity)
        if previous and previous['content'] == path.read_text(encoding='utf-8'):
            fail('This accepted container is already merged and cleaned; reopen and re-approve it before another merge')
        selected = {i: value for i, value in items.items() if value[0].is_relative_to(path.parent)}
        if any(value[1]['status'] != 'done' for value in selected.values()):
            fail('Every live container descendant must be committed to done before merging')
        entries, _ = commit_prepare(root, items, source, selection=selected)
        commit_message(None, entries)  # Validate acceptance without accepting anything.
        saved, restored = merge_saved_descendants(root, items, archives, identity, path.parent)
        entries.extend(restored)
        if meta['kind'] == 'group':
            merge_group_revisions(root, entries, source_head, saved)
        board = merge_board_plan(root, source_head, target_head, identity, retain=retain)
        if retain:
            target_board = merge_board(root, target_head)
            parent_paths = [p for p, (text, _) in target_board.items()
                            if p.endswith('/README.md') and _archive_ticket(text, accepted=False)[0]['id'] == meta['parent']]
            if len(parent_paths) != 1 or _archive_ticket(target_board[parent_paths[0]][0], accepted=False)[0]['status'] != 'wip':
                fail('Target parent group must remain WIP')
            if PurePosixPath(parent_paths[0]).parent != PurePosixPath(path.parent.parent.parent.relative_to(root).as_posix()):
                fail('Target parent-group path changed; reconcile the source group move before integration')
        target_root = merge_target_worktree(root, target)
        if target_root:
            merge_clean(target_root)
        subject = f'feat: {meta["title"][:40]} [{identity}]'
        message = commit_message(subject, entries)
        if args.dry_run:
            print(f'{"Merge commit" if retain else "Squash merge"} {source} ({source_head}) -> {target} ({target_head})')
            print('Integration commit retains the complete container and all ticket records.')
            print('Retain done records on the WIP group; no cleanup.' if retain else
                  'Then automatically create one cleanup commit; no push or source-branch deletion.')
            print(f'Restore {len(saved)} previously archived children before integration.')
            print(message, end='')
            return
        data = dict(version=2, epic=identity, retain=retain, board=board, source_branch=source, source_head=source_head,
                    target_branch=target, target_before=target_head,
                    target_root=str(target_root) if target_root else None, owned=target_root is None,
                    epic_path=path.parent.relative_to(root).as_posix(), saved=saved,
                    tickets={entry[2]: entry[3] for entry in entries},
                    stage='prepared', message=message)
        journal_path.parent.mkdir(parents=True, exist_ok=True)

    lock = journal_path.with_suffix('.lock')
    target_lock = journal_path.parent / ('target-' + hashlib.sha256(data['target_branch'].encode()).hexdigest()[:16] + '.lock')
    target_locked = False
    try:
        lock.mkdir()
    except FileExistsError:
        fail('Another container merge is active; inspect a stale merge lock before removing it')
    try:
        try:
            target_lock.mkdir()
            target_locked = True
        except FileExistsError:
            fail('Another merge is using this target branch; inspect a stale target lock before removing it')
        for pending in journal_path.parent.glob('merge-*.json'):
            if pending != journal_path and json.loads(pending.read_text())['target_branch'] == data['target_branch']:
                fail('Finish the pending merge for this target branch before integrating another container')
        if not journal_path.exists():
            actual_target = _git_ok(root, 'rev-parse', '--verify', f'refs/heads/{data["target_branch"]}').stdout.strip()
            if actual_target != data['target_before']:
                fail('Target changed during preflight; retry without discarding any work')
            commit_journal(journal_path, data)
        if (commit_branch(root) != data['source_branch'] or
                _git_ok(root, 'rev-parse', 'HEAD').stdout.strip() != data['source_head']):
            fail('Merge recovery blocked: source branch/HEAD changed; journal retained')
        if data['stage'] == 'finished' and data['owned'] and not Path(data['target_root']).exists():
            if _git_ok(root, 'rev-parse', f'refs/heads/{data["target_branch"]}').stdout.strip() != data['result']:
                fail('Target changed after integration; journal retained')
            journal_path.unlink()
            print(f'Recovered completed integration of {identity}; source unchanged; nothing pushed')
            return
        if data['target_root'] is None:
            preferred = '/tmp/opencode' if Path('/tmp/opencode').is_dir() else None
            target_root = Path(tempfile.mkdtemp(prefix='work-merge-', dir=preferred))
            data['target_root'] = str(target_root)
            commit_journal(journal_path, data)
        target_root = Path(data['target_root'])
        if data['owned'] and target_root.is_dir() and not any(target_root.iterdir()):
            _git_ok(root, 'worktree', 'add', str(target_root), data['target_branch'])
        original_common = _git_ok(root, 'rev-parse', '--path-format=absolute', '--git-common-dir').stdout.strip()
        target_common = _git_ok(target_root, 'rev-parse', '--path-format=absolute', '--git-common-dir').stdout.strip()
        if Path(original_common).resolve() != Path(target_common).resolve():
            fail('Merge target belongs to a different repository; journal retained')
        if commit_branch(target_root) != data['target_branch']:
            fail('Merge target branch changed; journal retained')
        if (target_root / '.work' / JOURNAL_NAME).exists():
            commit_recover(target_root)
        head = _git_ok(target_root, 'rev-parse', 'HEAD').stdout.strip()
        if data['stage'] == 'prepared':
            if head != data['target_before']:
                fail('Merge target HEAD changed before integration; journal retained')
            merge_head = Path(_git_ok(target_root, 'rev-parse', '--path-format=absolute', '--git-path', 'MERGE_HEAD').stdout.strip())
            if not args.recover or (not _git_ok(target_root, 'status', '--porcelain').stdout and not merge_head.exists()):
                merge_clean(target_root)
                data['started'] = True
                commit_journal(journal_path, data)
                mode = '--no-ff' if data.get('retain') else '--squash'
                result = _git(target_root, 'merge', mode, '--no-commit', '--no-overwrite-ignore', data['source_head'])
                conflicts = _git_ok(target_root, 'ls-files', '-u').stdout
                if result.returncode and not conflicts:
                    fail(f'Merge stopped in {target_root}: {result.stderr.strip() or result.stdout.strip()}. '
                         f'Inspect the target, then run work merge {identity} --recover; source is unchanged')
                if data.get('board') is not None:
                    merge_restore_board(target_root, data['board'])
                if result.returncode and _git_ok(target_root, 'ls-files', '-u').stdout:
                    fail(f'Merge stopped in {target_root}: {result.stderr.strip() or result.stdout.strip()}. '
                         f'Resolve conflicts there, then run work merge {identity} --recover; source is unchanged')
            if _git_ok(target_root, 'ls-files', '-u').stdout or _git(target_root, 'diff', '--quiet').returncode:
                fail(f'Resolve/stage merge conflicts in {target_root}, then retry --recover')
            for relative, content in data['saved'].items():
                destination = target_root / relative
                if destination.is_symlink() or (destination.exists() and
                                               (not destination.is_file() or destination.read_bytes() != content.encode('utf-8'))):
                    fail(f'Restored archive destination changed: {destination}')
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(content, encoding='utf-8', newline='')
                _git_ok(target_root, 'add', '--', relative)
            current = records(target_root)
            check(target_root, current, Archives(target_root))
            container_file = target_root / data['epic_path'] / 'README.md'
            if identity not in current or current[identity][0] != container_file:
                fail('Merge result does not preserve the approved container path')
            merged_items = {i: value for i, value in current.items() if value[0].is_relative_to(container_file.parent)}
            if any(value[1]['status'] != 'done' for value in merged_items.values()):
                fail('Merge result contains unfinished container work; resolve before retrying')
            if {value[0].relative_to(target_root).as_posix() for value in merged_items.values()} != set(data['tickets']):
                fail('Merge result changed the approved ticket selection; journal retained')
            for relative, content in data['tickets'].items():
                if (target_root / relative).read_bytes() != content.encode('utf-8'):
                    fail(f'Merge changed an approved ticket: {relative}; re-review it before integrating')
            validation, _ = commit_prepare(target_root, current, data['target_branch'], selection=merged_items,
                                           merging=data.get('retain', False))
            commit_message(None, validation)
            data['tree'] = _git_ok(target_root, 'write-tree').stdout.strip()
            if 'board' in data:
                expected = dict(data['board'])
                expected.update({p: [text, '100644'] for p, text in data['saved'].items()})
                if merge_board(target_root, data['tree']) != expected:
                    fail('Merge changed preserved sibling/group board state or staged bytes; journal retained')
            data['stage'] = 'ready'
            commit_journal(journal_path, data)
        head = _git_ok(target_root, 'rev-parse', 'HEAD').stdout.strip()
        if data['stage'] == 'ready':
            if head == data['target_before']:
                if data.get('retain'):
                    pending = _git(target_root, 'rev-parse', '--verify', 'MERGE_HEAD')
                    if pending.returncode or pending.stdout.strip() != data['source_head']:
                        fail('Expected source MERGE_HEAD is missing or changed; preserve target and journal')
                if (_git_ok(target_root, 'write-tree').stdout.strip() != data['tree'] or
                        _git(target_root, 'diff', '--quiet').returncode):
                    fail('Staged merge result changed; preserve it and the journal before recovery')
                result = _git(target_root, 'commit', '--allow-empty', '--cleanup=verbatim', '-F', '-', input=data['message'])
                if result.returncode:
                    fail(f'Merge commit failed in {target_root}: {result.stderr.strip()}; retry work merge {identity} --recover')
                head = _git_ok(target_root, 'rev-parse', 'HEAD').stdout.strip()
            parents = data['target_before'] + (' ' + data['source_head'] if data.get('retain') else '')
            if not merge_matches(target_root, head, parents, data['tree'], data['message']):
                fail('Unexpected integration commit; preserve target worktree and merge journal')
            data['integration'] = head
            data['stage'] = 'merged'
            commit_journal(journal_path, data)
        if data['stage'] in ('merged', 'finished'):
            head = _git_ok(target_root, 'rev-parse', 'HEAD').stdout.strip()
            cleaned = (data.get('retain') and head == data['integration']) or (data.get('cleanup_tree') and
                       merge_matches(target_root, head, data['integration'], data['cleanup_tree'], data['cleanup_message']))
            if not cleaned:
                if head != data['integration']:
                    fail('Target changed after integration; journal retained, do not merge again')
                merge_clean(target_root)
                current = records(target_root)
                selected = {i: value for i, value in current.items()
                            if value[0].is_relative_to(target_root / data['epic_path'])}
                entries, units = commit_prepare(target_root, current, data['target_branch'], selection=selected)
                message = commit_message(f'chore: archive completed container [{identity}]', entries)
                with tempfile.TemporaryDirectory(prefix='work-cleanup-') as temporary:
                    private = Path(temporary) / 'index'
                    private.write_bytes(commit_index(target_root).read_bytes())
                    env = {'GIT_INDEX_FILE': str(private)}
                    _git_ok(target_root, 'rm', '-r', '-f', '--cached', '-q', '--',
                            *[unit for unit, _ in units], env=env)
                    data['cleanup_tree'] = _git_ok(target_root, 'write-tree', env=env).stdout.strip()
                data['cleanup_message'] = message
                commit_journal(journal_path, data)
                with locked(target_root):
                    commit_apply(target_root, data['target_branch'], entries, units, message)
                head = _git_ok(target_root, 'rev-parse', 'HEAD').stdout.strip()
                if not merge_matches(target_root, head, data['integration'], data['cleanup_tree'], message):
                    fail('Unexpected cleanup commit; journal retained')
            merge_clean(target_root)
            check(target_root, records(target_root), Archives(target_root))
            data['stage'] = 'finished'
            data['result'] = head
            commit_journal(journal_path, data)
            if data['owned'] and not _git_ok(target_root, 'status', '--porcelain', '--ignored').stdout:
                _git_ok(root, 'worktree', 'remove', '--', str(target_root))
            elif data['owned']:
                print(f'Target worktree retained to preserve ignored files: {target_root}')
            journal_path.unlink()
            print(f'Merged {identity} into {data["target_branch"]}: {data["integration"]}')
            print('Done records retained on the WIP group; source branch unchanged; nothing pushed' if data.get('retain') else
                  f'Cleanup commit: {head}; source branch unchanged; nothing pushed')
    finally:
        if target_locked:
            target_lock.rmdir()
        lock.rmdir()


def install(source, target):
    """Copy a self-contained runtime without editing existing project instructions."""
    target = target.resolve()
    if not target.is_dir():
        fail('Target must be an existing project directory')
    destination = target / '.workkit'
    if destination.exists() or destination.is_symlink():
        fail('.workkit already exists; review and replace it explicitly to update')
    skills = source / 'skills'
    for skill in skills.iterdir():
        link = target / '.agents' / 'skills' / skill.name
        if link.exists() or link.is_symlink():
            fail(f'Skill already exists: {skill.name}; nothing changed')
    commands = source / 'commands'
    for command in commands.glob('*.md'):
        link = target / '.opencode' / 'commands' / command.name
        if link.exists() or link.is_symlink():
            fail(f'OpenCode command already exists: {command.name}; nothing changed')
    destination.mkdir()
    runtime = Path('.work') / 'tools' / 'work.py'
    (destination / runtime).parent.mkdir(parents=True)
    shutil.copy2(source / runtime, destination / runtime)
    shutil.copy2(source / 'work', destination / 'work')
    shutil.copy2(source / 'CONVENTION.md', destination / 'CONVENTION.md')
    shutil.copy2(source / 'CHANGELOG.md', destination / 'CHANGELOG.md')
    shutil.copy2(source / 'LICENSE', destination / 'LICENSE')
    shutil.copytree(source / 'templates', destination / 'templates')
    shutil.copytree(source / 'docs', destination / 'docs')
    shutil.copytree(skills, destination / 'skills')
    shutil.copytree(commands, destination / 'commands')
    for skill in skills.iterdir():
        link = target / '.agents' / 'skills' / skill.name
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(os.path.relpath(destination / 'skills' / skill.name, link.parent),
                        target_is_directory=True)
    for command in commands.glob('*.md'):
        link = target / '.opencode' / 'commands' / command.name
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(os.path.relpath(destination / 'commands' / command.name, link.parent))
    agents = target / 'AGENTS.md'
    existing = agents.read_text(encoding='utf-8') if agents.exists() else ''
    marker = '<!-- worktree-tickets -->'
    if marker not in existing:
        agents.write_text(existing + '\n' + marker + '\n## Worktree Tickets\n\nUse the project work-prepare, work-execute, and work-commit skills; each selects\nrelevant references from `.workkit/docs/`. `CONVENTION.md` is an index, not a\nrequired full-context read. Run `./.workkit/work --help` for commands.\nPreserve ticket IDs in commits.\n', encoding='utf-8')
    (destination / 'VERSION').write_text(VERSION + '\n', encoding='utf-8')
    if not (target / '.work').exists():
        initialize(target)
    print('Installed. Run: ./.workkit/work list')
    print('Agent setup: use the project skills and project AGENTS.md.')


def setup(source, bin_dir):
    """Expose this checkout's launcher without shell configuration or downloads."""
    launcher = source / 'work'
    bin_dir = bin_dir.expanduser().absolute()
    command = bin_dir / 'work'
    if command.exists() or command.is_symlink():
        if not command.is_symlink() or command.resolve() != launcher.resolve():
            fail(f'{command} already exists; nothing changed')
    else:
        bin_dir.mkdir(parents=True, exist_ok=True)
        command.symlink_to(launcher.resolve())
    print(f'Command ready: {command}')
    if str(bin_dir) not in os.environ.get('PATH', '').split(os.pathsep):
        print(f'Add {bin_dir} to your PATH to run work from anywhere.')


def main():
    parser = argparse.ArgumentParser(prog='work', description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog='Examples:\n  work list --status review\n  work show T-1234abcd\n  work commit --dry-run')
    parser.add_argument('--version', action='version', version=VERSION)
    parser.add_argument('--root', type=Path, default=Path.cwd(), help='Project directory (default: current directory)')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('init', help='Create an empty .work board in the project')
    p = sub.add_parser('setup', help='Expose work on PATH (keeps a link to this checkout)')
    p.add_argument('--bin-dir', type=Path, default=Path.home() / '.local' / 'bin', help='Launcher directory (default: ~/.local/bin)')
    p = sub.add_parser('install', help='Copy the toolkit and link project skills/commands')
    p.add_argument('target', type=Path, help='Existing project directory')
    p = sub.add_parser('create', help='Create a backlog ticket', epilog='Example: work create task "Add tests" --parent E-1234abcd')
    p.add_argument('kind', choices=KINDS, help='Ticket type')
    p.add_argument('title', help='Short ticket title')
    p.add_argument('--parent', help='Parent ID (required for stories/tasks)')
    p = sub.add_parser('list', help='Find work in the current epic (or the whole board)',
                       description='Default: backlog stories/tasks in the current branch\'s unique epic. Explicit --status includes containers. No automatic scope fallback.',
                       epilog='Examples: work list --ready; work list --status review; work list --epic E-1234abcd; work list --all')
    scope = p.add_mutually_exclusive_group()
    scope.add_argument('--epic', metavar='ID', help='Select a live epic explicitly (no branch filtering)')
    scope.add_argument('--all', action='store_true', help='List the whole live board, all statuses unless filtered')
    p.add_argument('--status', choices=STATES, help='Show only this status')
    p.add_argument('--ready', action='store_true', help='Only backlog stories/tasks with accepted dependencies and backlog/WIP ancestors; not execution authorization')
    p = sub.add_parser('show', help='Display a live or archived ticket by ID')
    p.add_argument('id', help='Ticket ID')
    sub.add_parser('check', help='Validate hierarchy, statuses, and dependencies')
    p = sub.add_parser('preflight', help='Read-only ticket, Git context, and execution checks',
                       description='Inspect branch/worktree, hierarchy, and execution gates without writes or Git setup.')
    p.add_argument('id', help='Selected ticket ID')
    p.add_argument('--for', dest='purpose', choices=('execute', 'commit'), default='execute',
                   help='Execution gates (default), or branch context only for authorized Git work')
    descriptions = {'start': 'Move backlog/review work to WIP', 'review': 'Hand WIP work to its reviewer',
                    'done': 'Accept reviewed work into implemented (awaiting commit)',
                    'reopen': 'Return work to backlog; restore archived tickets'}
    for command in ('start', 'review', 'done', 'reopen'):
        p = sub.add_parser(command, help=descriptions[command], description=descriptions[command])
        p.add_argument('id', help='Ticket ID')
        p.add_argument('--dry-run', action='store_true', help='Preview the transition without changing tickets')
        if command == 'done':
            p.add_argument('--by', help='Recorded reviewer accepting the work (required)')
            p.add_argument('--evidence', help='Review/verification evidence (required)')
    p = sub.add_parser('assign', help='Set implementer and reviewer on unfinished work')
    p.add_argument('id', help='Ticket ID')
    p.add_argument('--implementer', required=True, help='Implementer name or role')
    p.add_argument('--reviewer', required=True, help='Reviewer name or role')
    p = sub.add_parser('depend', help='Add or remove an explicit prerequisite')
    p.add_argument('id', help='Dependent ticket ID')
    p.add_argument('dependency', help='Prerequisite ticket ID')
    p.add_argument('--remove', action='store_true', help='Remove rather than add the dependency')
    p = sub.add_parser('commit', help='Commit implemented tickets and retain them in done',
                       description='Commit staged changes, generate the message from implemented tickets, and move them to done without deletion. No push by default.',
                       formatter_class=argparse.RawDescriptionHelpFormatter,
                       epilog='Examples:\n  work commit --dry-run\n  work commit T-1234abcd T-5678abcd\n  work commit --push\n  work commit --recover')
    p.add_argument('ids', nargs='*', metavar='ID', help='Implemented tickets to commit (default: all eligible); containers include queued descendants')
    p.add_argument('-m', '--message', help='Override the autogenerated one-line subject')
    p.add_argument('--dry-run', action='store_true', help='Preview selection, staged paths, retained tickets and message; no network')
    p.add_argument('--recover', action='store_true', help='Safely finish/restore an interrupted ticket commit; never creates a commit')
    p.add_argument('--push', action='store_true', help='After committing, push only this branch to its configured upstream (no force)')
    p = sub.add_parser('merge', help='Integrate a done container: retain on a group, squash and clean on the final base')
    p.add_argument('id', help='Approved, committed group or epic ID; uses recorded branch/base_branch')
    p.add_argument('--dry-run', action='store_true', help='Preview integration and cleanup without writes or network')
    p.add_argument('--recover', action='store_true', help='Resume the saved merge/cleanup without redoing a successful merge')
    args = parser.parse_args()
    if args.command == 'list' and args.ready and args.status not in (None, 'backlog'):
        parser.error('--ready requires backlog (cannot combine with another --status)')
    if args.command == 'commit' and args.recover and (args.ids or args.message is not None or args.push or args.dry_run):
        parser.error('--recover cannot be combined with IDs, -m, --push, or --dry-run')
    if args.command == 'setup':
        setup(TOOLKIT, args.bin_dir); return
    if args.command == 'install':
        install(TOOLKIT, args.target); return
    if args.command == 'init':
        initialize(args.root.resolve()); return
    root = root_at(args.root)
    if args.command == 'preflight':
        preflight(root, args.id, args.purpose)
        return
    with locked(root):
        if args.command == 'commit' and getattr(args, 'recover', False):
            commit_recover(root)
            return
        if (root / '.work' / JOURNAL_NAME).exists() and args.command not in ('show', 'list', 'check'):
            fail('A commit journal needs attention; run `work commit --recover` before further mutations')
        items = records(root)
        archives = Archives(root)
        check(root, items, archives)
        if args.command == 'check':
            print(f'OK: {len(items)} tickets')
        elif args.command == 'create':
            if not args.title.strip() or '\n' in args.title or '\r' in args.title:
                fail('Title must be a nonempty single line')
            create(root, items, args, archives)
        elif args.command == 'list':
            list_tickets(root, items, archives, args)
        elif args.command == 'show':
            path, _, _, record = lookup(items, archives, args.id)
            if record is None:
                print(path.relative_to(root)); print(path.read_text(encoding='utf-8'))
            else:
                print(f'archived: {record["path"]}')
                print(f'commits: {", ".join(record["commits"])}')
                print(record['content'])
        elif args.command in ('start', 'review', 'done', 'reopen'):
            transition(root, items, args, archives)
        elif args.command in ('assign', 'depend'):
            path, old, body, record = lookup(items, archives, args.id)
            if record is not None:
                fail(f'{args.id} is archived; reopen it first')
            meta = dict(old)
            if args.command == 'assign':
                if old['status'] in COMPLETED:
                    fail('Reopen before changing ownership')
                if not args.implementer.strip() or not args.reviewer.strip():
                    fail('Owners must be nonempty')
                meta.update(implementer=args.implementer, reviewer=args.reviewer)
            else:
                lookup(items, archives, args.dependency)
                deps = list(meta.get('depends_on', []))
                if args.remove:
                    deps = [d for d in deps if d != args.dependency]
                elif args.dependency not in deps:
                    deps.append(args.dependency)
                meta['depends_on'] = deps
            candidate = dict(items); candidate[args.id] = (path, meta, body)
            check(root, candidate, archives)
            write(path, meta, body)
            print(args.id)
        elif args.command == 'commit':
            commit_command(root, items, archives, args)
        elif args.command == 'merge':
            merge_command(root, items, archives, args)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError) as error:
        print(f'work: {error}', file=sys.stderr)
        sys.exit(1)
