#!/usr/bin/env python3
"""Worktree Tickets: a dependency-free Markdown work board. Python 3.10+."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import uuid

VERSION = '0.2.0'
TOOLKIT = Path(__file__).resolve().parents[2]
STATES = ('backlog', 'wip', 'review', 'done')
KINDS = {'group': 'G', 'epic': 'E', 'story': 'S', 'task': 'T'}


def fail(message):
    raise ValueError(message)


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


def ancestors(items, identity):
    seen = set()
    parent = get(items, identity)[1].get('parent')
    while parent:
        if parent in seen:
            fail('Parent cycle detected')
        seen.add(parent)
        yield parent
        parent = get(items, parent)[1].get('parent')


def check(root, items):
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
        list(ancestors(items, identity))  # Validate ancestry before using parent paths.
        parent = meta.get('parent')
        if parent:
            pp, pm, _ = get(items, parent)
            if (kind == 'epic' and pm['kind'] != 'group') or (kind in ('story', 'task') and pm['kind'] != 'epic') or kind == 'group':
                fail(f'{identity}: invalid parent kind')
            expected = pp.parent / status
        elif kind in ('story', 'task'):
            fail(f'{identity}: stories/tasks require an epic')
        else:
            expected = root / '.work' / status
        actual = path.parent.parent if kind in ('epic', 'group') else path.parent
        if actual != expected:
            fail(f'{identity}: parent/directory/status disagree; expected under {expected}. '
                 'For older boards, see docs/MIGRATIONS.md migration instructions.')
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
            get(items, dep)
            if dep == identity:
                fail(f'{identity}: cannot depend on itself')
        if status == 'done' and any(get(items, c)[1]['status'] != 'done' for c in children(items, identity)):
            fail(f'{identity}: done container has unfinished children')
        if status == 'done' and any(get(items, d)[1]['status'] != 'done' for d in deps):
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
        for dep in items[identity][1].get('depends_on', []) + children(items, identity):
            visit(dep)
        visiting.remove(identity)
        visited.add(identity)
    for identity in items:
        visit(identity)


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


def create(root, items, args):
    parent = args.parent
    if args.kind in ('story', 'task') and not parent:
        fail('A story/task needs --parent EPIC_ID')
    if parent:
        pp, pm, _ = get(items, parent)
        expected = 'group' if args.kind == 'epic' else 'epic'
        if args.kind == 'group' or pm['kind'] != expected:
            fail(f'{args.kind} requires a {expected} parent')
        if pm['status'] == 'done':
            fail('Reopen the parent before adding work')
    identity = KINDS[args.kind] + '-' + uuid.uuid4().hex[:8]
    while identity in items:
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


def transition(root, items, args):
    path, old, body = get(items, args.id)
    target = {'start': 'wip', 'review': 'review', 'done': 'done', 'reopen': 'backlog'}[args.command]
    allowed = {'backlog': ('wip',), 'wip': ('review', 'backlog'),
               'review': ('done', 'wip', 'backlog'), 'done': ('backlog',)}
    if target not in allowed[old['status']]:
        fail(f"Cannot move {old['status']} to {target}")
    if target in ('wip', 'review', 'done'):
        blocked = [d for d in old.get('depends_on', []) if get(items, d)[1]['status'] != 'done']
        if blocked:
            fail('Unfinished dependencies: ' + ', '.join(blocked))
    if target == 'done':
        unfinished = [c for c in children(items, args.id) if get(items, c)[1]['status'] != 'done']
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
    reopen = list(ancestors(items, args.id)) if target == 'backlog' else []
    reopening = set()
    if target == 'backlog':
        reopening = {i for i in [args.id, *reopen] if get(items, i)[1]['status'] == 'done'}
    if reopening:
        dependents = [i for i, (_, m, _) in items.items()
                      if i not in reopening and m['status'] == 'done'
                      and reopening.intersection(m.get('depends_on', []))]
        if dependents:
            fail('Reopen completed dependents first: ' + ', '.join(dependents))
    if args.dry_run:
        print(f'{args.id}: {old["status"]} -> {target}')
        for ancestor in reopen:
            if get(items, ancestor)[1]['status'] == 'done':
                print(f'{ancestor}: done -> wip')
        return
    for ancestor in reversed(reopen):
        items = records(root)
        _, am, ab = get(items, ancestor)
        if am['status'] == 'done':
            persist(root, items, ancestor, dict(am, status='wip'), ab)
    items = records(root)
    persist(root, items, args.id, dict(old, status=target), body)
    print(f'{args.id}: {target}')


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
    parser = argparse.ArgumentParser(prog='work', description=__doc__)
    parser.add_argument('--version', action='version', version=VERSION)
    parser.add_argument('--root', type=Path, default=Path.cwd(), help='Project directory (default: current directory)')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('init')
    p = sub.add_parser('setup', help='Expose work on PATH (keeps a link to this checkout)')
    p.add_argument('--bin-dir', type=Path, default=Path.home() / '.local' / 'bin')
    p = sub.add_parser('install'); p.add_argument('target', type=Path)
    p = sub.add_parser('create'); p.add_argument('kind', choices=KINDS); p.add_argument('title'); p.add_argument('--parent')
    p = sub.add_parser('list'); p.add_argument('--status', choices=STATES)
    p = sub.add_parser('show'); p.add_argument('id')
    sub.add_parser('check')
    for command in ('start', 'review', 'done', 'reopen'):
        p = sub.add_parser(command); p.add_argument('id'); p.add_argument('--dry-run', action='store_true')
        if command == 'done':
            p.add_argument('--by'); p.add_argument('--evidence')
    p = sub.add_parser('assign'); p.add_argument('id'); p.add_argument('--implementer', required=True); p.add_argument('--reviewer', required=True)
    p = sub.add_parser('depend'); p.add_argument('id'); p.add_argument('dependency'); p.add_argument('--remove', action='store_true')
    args = parser.parse_args()
    if args.command == 'setup':
        setup(TOOLKIT, args.bin_dir); return
    if args.command == 'install':
        install(TOOLKIT, args.target); return
    if args.command == 'init':
        initialize(args.root.resolve()); return
    root = root_at(args.root)
    with locked(root):
        items = records(root)
        check(root, items)
        if args.command == 'check':
            print(f'OK: {len(items)} tickets')
        elif args.command == 'create':
            if not args.title.strip() or '\n' in args.title or '\r' in args.title:
                fail('Title must be a nonempty single line')
            create(root, items, args)
        elif args.command == 'list':
            for identity, (path, meta, _) in sorted(items.items()):
                if not args.status or meta['status'] == args.status:
                    print(f'{identity}  {meta["status"]:8}  {meta["title"]}  {path.relative_to(root)}')
        elif args.command == 'show':
            path, _, _ = get(items, args.id)
            print(path.relative_to(root)); print(path.read_text(encoding='utf-8'))
        elif args.command in ('start', 'review', 'done', 'reopen'):
            transition(root, items, args)
        elif args.command in ('assign', 'depend'):
            path, old, body = get(items, args.id)
            meta = dict(old)
            if args.command == 'assign':
                if old['status'] == 'done':
                    fail('Reopen before changing ownership')
                if not args.implementer.strip() or not args.reviewer.strip():
                    fail('Owners must be nonempty')
                meta.update(implementer=args.implementer, reviewer=args.reviewer)
            else:
                get(items, args.dependency)
                deps = list(meta.get('depends_on', []))
                if args.remove:
                    deps = [d for d in deps if d != args.dependency]
                elif args.dependency not in deps:
                    deps.append(args.dependency)
                meta['depends_on'] = deps
            candidate = dict(items); candidate[args.id] = (path, meta, body)
            check(root, candidate)
            write(path, meta, body)
            print(args.id)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError) as error:
        print(f'work: {error}', file=sys.stderr)
        sys.exit(1)
