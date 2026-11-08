import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1]
SCRIPT = SOURCE / '.work/tools/work.py'
spec = importlib.util.spec_from_file_location('work_archive', SCRIPT)
work = importlib.util.module_from_spec(spec)
spec.loader.exec_module(work)


def ticket(identity='T-1234abcd', status='done', extra='', **metadata):
    meta = dict(id=identity, kind='task', title='Archive example', status=status,
                parent='E-1234abcd', depends_on=[], implementer='agent', reviewer='human')
    meta.update(metadata)
    return ('---\n' + json.dumps(meta, ensure_ascii=False) + '\n---\n# Archive example\n'
            '\n## Acceptance criteria\n\n- [x] Tested\n' + extra +
            '\n## Acceptance record\n\n2026-11-06T12:00:00+00:00 — human: Reviewed tests\n')


def path_for(identity='T-1234abcd'):
    return f'.work/wip/E-1234abcd-example/done/{identity}-example.md'


class ArchiveRecordTests(unittest.TestCase):
    def record(self, content=None, path=None):
        content = content if content is not None else ticket()
        meta, _ = work._archive_ticket(content)
        record = dict(id=meta['id'], path=path or path_for(), content=content,
                      sha256=hashlib.sha256(content.encode('utf-8')).hexdigest())
        work._archive_record(record)
        return record

    def test_full_file_content_and_metadata_are_preserved(self):
        content = ticket(extra='\nUnicode café 日本語 🙂, "quotes", \\slashes, NUL \x00\n'
                         + 'Arbitrary prose including old marker names\n',
                         future={'nested': [None, True, 'unknown']})
        crlf = ticket('T-87654321').replace('\n', '\r\n').rstrip('\r\n')
        source = {path_for('T-87654321'): crlf, path_for(): content}
        records = [self.record(content, path) for path, content in source.items()]
        self.assertEqual({r['path']: r['content'] for r in records}, source)
        for record in records:
            self.assertEqual(record['sha256'], hashlib.sha256(record['content'].encode('utf-8')).hexdigest())

    def test_rejects_corruption_and_unsafe_paths(self):
        record = self.record()
        for key, value in [('content', ticket(extra='changed')), ('id', 'T-00000000'),
                           ('sha256', '0' * 64), ('path', '/tmp/example.md'),
                           ('path', '.work/../outside.md'), ('path', '.work//done/example.md'),
                           ('path', '.work\\done\\example.md'), ('path', path_for('T-00000000')),
                           ('path', path_for().replace('/done/', '/review/')),
                           ('path', path_for().replace('E-1234abcd-example', 'E-00000000-example'))]:
            with self.subTest(key=key, value=value[:50]), self.assertRaises(ValueError):
                work._archive_record(dict(record, **{key: value}))

    def test_requires_real_acceptance_content_not_just_done_metadata(self):
        content = ticket()
        invalid = [ticket(status='review'), ticket(status='backlog'), ticket(reviewer=None),
                   ticket(reviewer='other'), content.replace('- [x]', '* [ ]'),
                   content.split('\n## Acceptance record')[0],
                   content.replace('human: Reviewed tests', 'human: '),
                   content.replace('2026-11-06T12:00:00+00:00', 'yesterday'),
                   content.replace('2026-11-06T12:00:00+00:00', '2026-11-06T12:00:00'),
                   content.replace('"kind": "task"', '"kind": "epic"'),
                   content.replace('"status": "done"', '"status": "done", "status": "done"'),
                   ticket(depends_on=['T-1234abcd']), ticket(depends_on='T-00000000'),
                   ticket(parent=None), ticket(title=''), ticket(extra='\ud800'),
                   ticket(future=1).replace('"future": 1', '"future": 1e9999'),
                   ticket(future=1).replace('"future": 1', '"future": NaN')]
        for value in invalid:
            with self.subTest(value=repr(value[-80:])), self.assertRaises(ValueError):
                self.record(value)
        reaccepted = content + '\n## Acceptance record\n\n2026-11-06T13:00:00+00:00 — human: Accepted again\n'
        self.assertEqual(self.record(reaccepted)['content'], reaccepted)

    def test_container_paths_and_parent_metadata(self):
        for identity, kind, parent, path in (
                ('E-1234abcd', 'epic', None, '.work/done/E-1234abcd-example/README.md'),
                ('G-1234abcd', 'group', None, '.work/done/G-1234abcd-example/README.md'),
                ('E-1234abcd', 'epic', 'G-1234abcd',
                 '.work/wip/G-1234abcd-example/done/E-1234abcd-example/README.md')):
            with self.subTest(kind=kind, parent=parent):
                content = ticket(identity, kind=kind, parent=parent)
                self.assertEqual(self.record(content, path)['content'], content)

    def test_live_reopened_content_overrides_historical_completion(self):
        record = dict(self.record(), commits=['a' * 40])
        history = {record['id']: record}
        live = ticket(status='backlog', future='preserved')
        result = work.resolve_archive(history, record['id'], {record['id']: live})
        self.assertEqual(result['source'], 'live')
        self.assertEqual(result['content'], live)
        self.assertIsNone(result['path'])
        self.assertEqual(work.resolve_archive(history, record['id'])['source'], 'archive')
        self.assertEqual(history[record['id']], record)
        with self.assertRaisesRegex(ValueError, 'Unresolved ticket'):
            work.resolve_archive(history, 'T-00000000')
        with self.assertRaisesRegex(ValueError, 'Live ID disagrees'):
            work.resolve_archive(history, 'T-00000000', {'T-00000000': live})


class ArchiveHistoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'repo'
        self.root.mkdir()
        self.git('init', '-b', 'main')
        self.git('config', 'user.name', 'Archive Test')
        self.git('config', 'user.email', 'archive@example.invalid')
        self.git('config', 'commit.gpgsign', 'false')
        self.git('config', 'core.hooksPath', '/dev/null')
        self.commit('Base commit')
        self.base = self.git('rev-parse', 'HEAD')

    def git(self, *args, input=None, env=None):
        result = subprocess.run(['git', '-C', str(self.root), *args], input=input,
                                capture_output=True, text=True, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def commit(self, message):
        self.git('commit', '--allow-empty', '-F', '-', input=message)
        return self.git('rev-parse', 'HEAD')

    def archive(self, content=None, path=None):
        """Stage a deletion with a committed accepted-file parent, not a payload."""
        path = self.saved_file(content, path)
        path.unlink()
        self.git('add', '-u')
        return 'Clean up completed work'

    def test_head_reachability_and_rearchive_precedence(self):
        self.git('checkout', '-b', 'unreachable')
        self.commit(self.archive(ticket(extra='unreachable different record')))
        self.git('checkout', 'main')
        self.assertEqual(work.archive_history(self.root), {})
        older = self.commit(self.archive())
        newer_content = ticket(extra='reopened, implemented, and accepted again')
        newer = self.commit(self.archive(newer_content))
        entry = work.archive_history(self.root)['T-1234abcd']
        self.assertEqual(entry['commits'], [newer])
        self.assertNotIn(older, entry['commits'])
        self.assertEqual(entry['content'], newer_content)

    def test_merged_side_branch_is_read_and_equal_copies_coalesce(self):
        self.git('checkout', '-b', 'side')
        side = self.commit('side\n\n' + self.archive())
        self.git('checkout', 'main')
        main = self.commit('main\n\n' + self.archive())
        self.git('merge', '--no-ff', 'side', '-m', 'Merge side')
        entry = work.archive_history(self.root)['T-1234abcd']
        self.assertEqual(entry['commits'], sorted([side, main]))
        self.assertEqual(entry['content'], ticket())

    def test_side_branch_and_separate_snapshot_cleanup(self):
        self.git('checkout', '-b', 'side')
        side = self.commit(self.archive())
        self.git('checkout', 'main')
        self.commit('Unrelated main work')
        self.git('merge', '--no-ff', 'side', '-m', 'Merge side without copying archive')
        self.assertEqual(work.archive_history(self.root)['T-1234abcd']['commits'], [side])
        self.git('checkout', '-b', 'squashed', self.base)
        squashed = self.commit('Squashed change\n\n' + self.archive())
        entry = work.archive_history(self.root)['T-1234abcd']
        self.assertEqual(entry['commits'], [squashed])

    def test_conflicting_branches_require_descendant_reconciliation(self):
        self.git('checkout', '-b', 'side')
        self.commit(self.archive(ticket(extra='side change')))
        self.git('checkout', 'main')
        self.commit(self.archive(ticket(extra='main change')))
        self.git('merge', '--no-ff', 'side', '-m', 'Merge conflict in archive records')
        with self.assertRaisesRegex(ValueError, 'T-1234abcd: conflicting archive records'):
            work.archive_history(self.root)
        content = ticket(extra='reviewed reconciliation')
        resolution = self.commit(self.archive(content))
        self.assertEqual(work.archive_history(self.root)['T-1234abcd']['commits'], [resolution])

    def test_message_only_prototype_cannot_supply_completion(self):
        self.commit('Worktree-Tickets-Archive: 1\n' + json.dumps({'version': 1, 'tickets': [
            dict(id='T-1234abcd', path=path_for(), content=ticket(),
                 sha256=hashlib.sha256(ticket().encode()).hexdigest())]})
                    + '\nWorktree-Tickets-Archive-End')
        self.assertEqual(work.archive_history(self.root), {})
        with self.assertRaisesRegex(ValueError, 'Message-only prototype archives are unsupported'):
            work.lookup({}, work.Archives(self.root), 'T-1234abcd')
        self.assertEqual(work.archive_history(self.root), {})  # No implicit conversion.

    def test_ancestry_not_timestamps_selects_latest_record(self):
        self.commit(self.archive())
        content = ticket(extra='newer in ancestry, older timestamp')
        env = dict(os.environ, GIT_AUTHOR_DATE='2001-01-01T00:00:00+00:00',
                   GIT_COMMITTER_DATE='2001-01-01T00:00:00+00:00')
        self.git('commit', '--allow-empty', '-F', '-', input=self.archive(content), env=env)
        self.assertEqual(work.archive_history(self.root)['T-1234abcd']['content'], content)

    def test_non_utf8_ordinary_messages_do_not_break_history(self):
        raw = (f'tree {self.git("rev-parse", "HEAD^{tree}")}\nparent {self.base}\n'
               'author Test <archive@example.invalid> 1793966400 +0000\n'
               'committer Test <archive@example.invalid> 1793966400 +0000\n\n').encode('ascii')
        raw += b'Legacy message \xff\nInline Worktree-Tickets-Archive: 1\n'
        result = subprocess.run(['git', '-C', str(self.root), 'hash-object', '-t', 'commit', '-w', '--stdin'],
                                input=raw,
                                capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.git('update-ref', 'refs/heads/main', result.stdout.decode('ascii').strip())
        self.assertEqual(work.archive_history(self.root), {})

    def test_installed_runtime_has_self_contained_archive_api(self):
        archived = self.commit(self.archive())
        target = Path(self.tmp.name) / 'installed project'
        target.mkdir()
        result = subprocess.run([str(SOURCE / 'work'), 'install', str(target)],
                                cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        installed = target / '.workkit/.work/tools/work.py'
        installed_spec = importlib.util.spec_from_file_location('installed_archive', installed)
        runtime = importlib.util.module_from_spec(installed_spec)
        installed_spec.loader.exec_module(runtime)
        self.assertFalse(hasattr(runtime, 'encode_archive'))
        self.assertFalse(hasattr(runtime, 'decode_archive'))
        self.assertEqual(runtime.archive_history(self.root)['T-1234abcd']['commits'], [archived])

    def test_shallow_history_and_linked_worktree_diagnose_incompleteness(self):
        self.commit(self.archive())
        clone = Path(self.tmp.name) / 'shallow'
        self.git('clone', '--depth', '1', self.root.as_uri(), str(clone))
        with self.assertRaisesRegex(ValueError, 'shallow repository; obtain full history'):
            work.archive_history(clone)
        linked = Path(self.tmp.name) / 'linked'
        subprocess.run(['git', '-C', str(clone), 'worktree', 'add', '--detach', str(linked)],
                       check=True, capture_output=True)
        with self.assertRaisesRegex(ValueError, 'shallow repository'):
            work.archive_history(linked)

    def test_missing_object_and_non_git_repository_fail_clearly(self):
        archived = self.commit(self.archive())
        self.commit('Descendant')
        obj = self.root / '.git/objects' / archived[:2] / archived[2:]
        obj.unlink()  # Only this disposable fixture's object is removed.
        with self.assertRaisesRegex(ValueError, 'available Git objects; no fetch was attempted'):
            work.archive_history(self.root)
        empty = Path(self.tmp.name) / 'empty'
        empty.mkdir()
        with self.assertRaisesRegex(ValueError, 'Cannot read archive history'):
            work.archive_history(empty)
        subprocess.run(['git', '-C', str(empty), 'init'], check=True, capture_output=True)
        self.assertEqual(work.archive_history(empty), {})

    def test_lookup_is_read_only_and_ignores_foreign_git_routing(self):
        archived = self.commit(self.archive())
        (self.root / 'tracked').write_bytes(b'original staged bytes\n')
        self.git('add', 'tracked')
        (self.root / 'tracked').write_bytes(b'unstaged different bytes\n')
        (self.root / 'untracked').write_bytes(b'leave alone\n')
        def snapshot():
            return {path.relative_to(self.root).as_posix(): path.read_bytes()
                    for path in self.root.rglob('*') if path.is_file()}
        before = snapshot()
        with patch.dict(os.environ, {'GIT_DIR': '/does/not/exist', 'GIT_INDEX_FILE': '/does/not/exist'}):
            entry = work.archive_history(self.root)['T-1234abcd']
        self.assertEqual(entry['commits'], [archived])
        self.assertEqual(before, snapshot())

    def test_same_contents_on_different_paths_have_all_maximal_provenance(self):
        self.git('checkout', '-b', 'side')
        alternate = path_for().replace('-example.md', '-renamed.md')
        side = self.commit(self.archive(path=alternate))
        self.git('checkout', 'main')
        main = self.commit(self.archive())
        self.git('merge', '--no-ff', 'side', '-m', 'Merge copied record')
        self.assertEqual(work.archive_history(self.root)['T-1234abcd']['commits'], sorted([side, main]))

    def saved_file(self, content=None, path=None):
        path = self.root / (path or path_for())
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((content if content is not None else ticket()).encode('utf-8'))
        self.git('add', '.work')
        self.commit('Save ticket files')
        return path

    def remove_file(self, path, message='Clean up completed work'):
        path.unlink()
        self.git('add', '-u')
        return self.commit(message)

    def test_ordinary_deleted_file_needs_no_message_marker_or_id(self):
        content = ticket(extra='\nUnicode café 日本語\n', future={'preserve': True}).replace('\n', '\r\n')
        path = self.saved_file(content)
        removal = self.remove_file(path)
        before = self.git('status', '--porcelain')
        entry = work.archive_history(self.root)['T-1234abcd']
        self.assertEqual(entry['content'], content)
        self.assertEqual(entry['path'], path_for())
        self.assertEqual(entry['commits'], [removal])
        self.assertEqual(before, self.git('status', '--porcelain'))

    def test_ordinary_deletion_does_not_accept_unfinished_or_invalid_tickets(self):
        for content in (ticket(status='review'), ticket(reviewer=None),
                        ticket().replace('- [x]', '- [ ]'),
                        ticket().split('\n## Acceptance record')[0],
                        'not a ticket', ticket(parent='E-00000000')):
            with self.subTest(content=content[:90]):
                path = self.saved_file(content)
                self.remove_file(path)
                self.assertEqual(work.archive_history(self.root), {})

    def test_status_moves_and_renames_are_not_archives(self):
        path = self.saved_file()
        moved = path.with_name('T-1234abcd-renamed.md')
        path.rename(moved)
        self.git('add', '.work')
        self.commit('Rename completed ticket')
        self.assertEqual(work.archive_history(self.root), {})
        target = Path(str(moved).replace('/done/', '/backlog/'))
        target.parent.mkdir(parents=True)
        target.write_text(ticket(status='backlog'))
        moved.unlink()
        self.git('add', '.work')
        self.commit('Reopen with an editor')
        self.assertEqual(work.archive_history(self.root), {})

    def test_ordinary_rearchive_uses_latest_accepted_file(self):
        path = self.saved_file()
        self.remove_file(path)
        content = ticket(extra='Second approved implementation')
        path = self.saved_file(content)
        removal = self.remove_file(path)
        entry = work.archive_history(self.root)['T-1234abcd']
        self.assertEqual(entry['content'], content)
        self.assertEqual(entry['commits'], [removal])

    def test_unfinished_deletion_cannot_reuse_an_older_approval(self):
        path = self.saved_file()
        self.remove_file(path)
        pending_path = path_for().replace('/done/', '/backlog/')
        path = self.saved_file(ticket(status='backlog'), pending_path)
        self.remove_file(path)
        with self.assertRaisesRegex(ValueError, 'deletion.*lacks accepted done evidence'):
            work.archive_history(self.root)
        path = self.saved_file(ticket(extra='Approved after reconciliation'))
        removal = self.remove_file(path)
        self.assertEqual(work.archive_history(self.root)['T-1234abcd']['commits'], [removal])

    def test_markerless_archive_is_branch_local_and_survives_merge(self):
        path = self.saved_file()
        self.git('checkout', '-b', 'side')
        self.remove_file(path)
        self.git('checkout', 'main')
        self.assertEqual(work.archive_history(self.root), {})
        self.commit('Main work')
        self.git('merge', '--no-ff', 'side', '-m', 'Merge cleanup')
        self.assertEqual(work.archive_history(self.root)['T-1234abcd']['content'], ticket())

    def test_markerless_conflicting_branches_need_reconciliation(self):
        self.git('checkout', '-b', 'side')
        path = self.saved_file(ticket(extra='Side acceptance'))
        self.remove_file(path)
        self.git('checkout', 'main')
        path = self.saved_file(ticket(extra='Main acceptance'))
        self.remove_file(path)
        self.git('merge', '--no-ff', 'side', '-m', 'Merge cleanup')
        with self.assertRaisesRegex(ValueError, 'conflicting archive records'):
            work.archive_history(self.root)
        path = self.saved_file(ticket(extra='Reviewed reconciliation'))
        removal = self.remove_file(path)
        self.assertEqual(work.archive_history(self.root)['T-1234abcd']['commits'], [removal])

    def test_ordinary_deletion_rejects_duplicate_source_ids(self):
        first = self.saved_file()
        second = self.saved_file(path=path_for().replace('-example.md', '-duplicate.md'))
        first.unlink()
        second.unlink()
        self.git('add', '-u')
        self.commit('Delete duplicated completed files')
        with self.assertRaisesRegex(ValueError, 'duplicate snapshot records'):
            work.archive_history(self.root)

    def test_prototype_trailer_has_no_effect_on_native_file_lookup(self):
        path = self.saved_file()
        removal = self.remove_file(path, 'Archive\n\n## Completed tickets\n\n'
                                   '- T-1234abcd — Archive example\n\nTicket-Archive: 2\n')
        self.assertEqual(work.archive_history(self.root)['T-1234abcd']['commits'], [removal])

    def test_history_reads_do_not_spawn_a_git_process_per_commit(self):
        path = self.saved_file()
        self.remove_file(path)
        original = work._archive_git
        with patch.object(work, '_archive_git', wraps=original) as calls:
            work.archive_history(self.root)
            small = calls.call_count
        for index in range(40):
            self.commit(f'Unrelated change {index}')
        with patch.object(work, '_archive_git', wraps=original) as calls:
            work.archive_history(self.root)
            self.assertEqual(calls.call_count, small)
            self.assertLess(calls.call_count, 20)


class ArchiveLifecycleTests(unittest.TestCase):
    """CLI lifecycle behavior with tickets archived in Git history.

    Fixtures preserve accepted files in a commit before ordinary deletion,
    matching the current file-history contract in docs/GIT.md.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'repo'
        self.root.mkdir()
        self.git('init', '-b', 'main')
        self.git('config', 'user.name', 'Archive Test')
        self.git('config', 'user.email', 'archive@example.invalid')
        self.git('config', 'commit.gpgsign', 'false')
        self.git('config', 'core.hooksPath', '/dev/null')
        self.commit('Base commit')
        self.run_work('init')

    def git(self, *args, input=None, env=None):
        result = subprocess.run(['git', '-C', str(self.root), *args], input=input,
                                capture_output=True, text=True, env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def commit(self, message):
        self.git('commit', '--allow-empty', '-F', '-', input=message)
        return self.git('rev-parse', 'HEAD')

    def run_work(self, *args, ok=True):
        result = subprocess.run([sys.executable, str(SCRIPT), '--root', str(self.root), *args],
                                capture_output=True, text=True)
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
        return result.stdout.strip() if ok else result.stderr

    def create(self, kind, title='Example', parent=None):
        args = ['create', kind, title]
        if parent:
            args += ['--parent', parent]
        return self.run_work(*args)

    def ready(self, identity):
        path, meta, body = work.records(self.root)[identity]
        work.write(path, meta, body.replace('- [ ]', '- [x]'))
        self.run_work('assign', identity, '--implementer', 'agent', '--reviewer', 'human')
        self.run_work('start', identity)
        self.run_work('review', identity)

    def finish(self, identity, evidence='Reviewed acceptance evidence'):
        self.ready(identity)
        self.run_work('done', identity, '--by', 'human', '--evidence', evidence)
        # Construct retained done fixtures before testing file-history lookup.
        path, meta, body = work.records(self.root)[identity]
        work.persist(self.root, work.records(self.root), identity, dict(meta, status='done'), body)

    def archive(self, *identities):
        """Commit accepted ticket files, then commit their removal."""
        self.git('add', '.work')
        self.commit('Record approved work')
        for identity in identities:
            path, meta, _ = work.records(self.root)[identity]
            if meta['kind'] in ('group', 'epic'):
                shutil.rmtree(path.parent)
            else:
                path.unlink()
        self.git('add', '-u')
        self.commit('Clean up completed work')

    def ordinary_archive(self, *identities):
        """Save accepted files, then remove them in an unmarked ordinary commit."""
        paths = [work.records(self.root)[identity][0] for identity in identities]
        self.git('add', '.work')
        self.commit('Record approved work')
        for path in paths:
            path.unlink()
        self.git('add', '-u')
        return self.commit('Clean up completed work')

    def test_markerless_reopen_follows_parent_ids_through_missing_epic_and_group(self):
        group = self.create('group', 'Delivery')
        epic = self.create('epic', 'Search', group)
        task = self.create('task', 'Index titles', epic)
        sibling = self.create('task', 'Other work', epic)
        for identity in (task, sibling, epic, group):
            self.finish(identity)
        path, meta, body = work.records(self.root)[task]
        work.write(path, dict(meta, custom={'preserve': True}), body + '\nImportant handoff\n')
        # Parents and children can disappear in separate commits; links are IDs,
        # not a shared archive message or paths that must still exist on disk.
        self.ordinary_archive(task, sibling)
        self.ordinary_archive(epic)
        self.ordinary_archive(group)
        shown = self.run_work('show', task)
        self.assertIn('Important handoff', shown)
        before = self.board_files()
        head = self.git('rev-parse', 'HEAD')
        index = (self.root / '.git/index').read_bytes()
        preview = self.run_work('reopen', task, '--dry-run')
        for identity in (group, epic, task):
            self.assertIn(identity, preview)
        self.assertEqual(before, self.board_files())
        self.assertEqual(head, self.git('rev-parse', 'HEAD'))
        self.assertEqual(index, (self.root / '.git/index').read_bytes())
        self.run_work('reopen', task)
        items = work.records(self.root)
        self.assertEqual(items[group][1]['status'], 'wip')
        self.assertEqual(items[epic][1]['status'], 'wip')
        self.assertEqual(items[task][1]['status'], 'backlog')
        self.assertEqual(items[task][1]['parent'], epic)
        self.assertEqual(items[epic][1]['parent'], group)
        self.assertEqual(items[task][1]['custom'], {'preserve': True})
        self.assertIn('Acceptance record', items[task][2])
        self.assertNotIn(sibling, items)
        self.run_work('check')

    def test_markerless_dependents_still_block_reopening(self):
        epic = self.create('epic', 'Search')
        first = self.create('task', 'Prerequisite', epic)
        second = self.create('task', 'Dependent', epic)
        self.run_work('depend', second, first)
        self.finish(first)
        self.finish(second)
        self.ordinary_archive(first, second)
        before = self.board_files()
        self.assertIn(second, self.run_work('reopen', first, ok=False))
        self.assertEqual(before, self.board_files())
        self.run_work('reopen', second)
        self.run_work('reopen', first)
        self.run_work('check')

    def test_markerless_reopen_reports_missing_parent_without_writing(self):
        epic = self.create('epic', 'Search')
        task = self.create('task', 'Index', epic)
        self.finish(task)
        self.ordinary_archive(task)
        work.records(self.root)[epic][0].unlink()  # Never approved or archived.
        before = self.board_files()
        self.assertIn(epic, self.run_work('reopen', task, ok=False))
        self.assertEqual(before, self.board_files())

    def board_files(self):
        return {p.relative_to(self.root).as_posix(): p.read_bytes()
                for p in (self.root / '.work').rglob('*') if p.is_file()}

    def test_show_resolves_archived_record_with_provenance(self):
        epic = self.create('epic', 'Search')
        task = self.create('task', 'Index titles', epic)
        self.finish(task)
        self.archive(task)
        self.assertNotIn(task, work.records(self.root))
        output = self.run_work('show', task)
        self.assertIn('archived: .work/', output)
        self.assertIn('commits: ', output)
        self.assertIn('## Acceptance record', output)
        self.assertIn('Reviewed acceptance evidence', output)
        live = self.run_work('show', epic)
        self.assertIn(str(work.records(self.root)[epic][0].relative_to(self.root)), live)
        self.assertIn('Unknown ticket', self.run_work('show', 'T-00000000', ok=False))
        self.run_work('check')

    def test_create_and_install_in_repository_with_unborn_head(self):
        for installed in (False, True):
            with self.subTest(installed=installed):
                root = Path(self.tmp.name) / ('installed' if installed else 'fresh')
                root.mkdir()
                subprocess.run(['git', '-C', str(root), 'init', '-b', 'main'],
                               check=True, capture_output=True)
                if installed:
                    result = subprocess.run([str(SOURCE / 'work'), 'install', str(root)],
                                            capture_output=True, text=True)
                    script = root / '.workkit/.work/tools/work.py'
                else:
                    script = SCRIPT
                    result = subprocess.run([sys.executable, str(script), '--root', str(root), 'init'],
                                            capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(work.archive_history(root), {})
                result = subprocess.run([sys.executable, str(script), '--root', str(root),
                                         'create', 'epic', 'First'], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                epic = result.stdout.strip()
                result = subprocess.run([sys.executable, str(script), '--root', str(root),
                                         'create', 'task', 'Child', '--parent', epic],
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(len(work.records(root)), 2)
                self.assertFalse((root / '.git/refs/heads/main').exists())

    def test_cycle_detection_follows_archived_dependencies(self):
        epic = self.create('epic', 'Container')
        first = self.create('task', 'First', epic)
        second = self.create('task', 'Second', epic)
        self.finish(first)
        self.run_work('depend', second, first)
        self.finish(second)
        self.archive(second)
        # Hand-edited live metadata must not close a cycle through the archive.
        path, meta, body = work.records(self.root)[first]
        work.write(path, dict(meta, depends_on=[second]), body)
        self.assertIn('Dependency cycle', self.run_work('check', ok=False))

    def test_archived_dependencies_satisfy_start_check_and_done(self):
        first = self.create('task', 'Prerequisite', self.create('epic', 'First'))
        second = self.create('task', 'Dependent', self.create('epic', 'Second'))
        self.run_work('depend', second, first)
        self.finish(first)
        self.archive(first)
        self.run_work('check')
        self.ready(second)
        self.run_work('done', second, '--by', 'human', '--evidence', 'Reviewed')
        self.run_work('check')

    def test_container_completes_with_mixed_active_and_archived_children(self):
        epic = self.create('epic', 'Container')
        archived_child = self.create('task', 'Archived child', epic)
        active_child = self.create('task', 'Active child', epic)
        self.finish(archived_child)
        self.archive(archived_child)
        self.finish(active_child)
        self.finish(epic)
        self.assertEqual(work.records(self.root)[epic][1]['status'], 'done')
        self.run_work('check')

    def test_reopen_restores_chain_content_metadata_and_structure(self):
        group = self.create('group', 'Delivery')
        epic = self.create('epic', 'Search', group)
        task = self.create('task', 'Index titles', epic)
        path, meta, body = work.records(self.root)[task]
        work.write(path, dict(meta, custom={'preserve': True}), body)
        self.finish(task)
        self.finish(epic)
        self.finish(group)
        self.archive(task, epic, group)
        for identity in (task, epic, group):
            self.assertNotIn(identity, work.records(self.root))
        self.run_work('reopen', task)
        items = work.records(self.root)
        self.assertEqual(items[group][1]['status'], 'wip')
        self.assertEqual(items[epic][1]['status'], 'wip')
        self.assertEqual(items[task][1]['status'], 'backlog')
        self.assertIn('/wip/', str(items[group][0]))
        self.assertEqual(items[epic][0].parent.parent, items[group][0].parent / 'wip')
        self.assertEqual(items[task][0].parent, items[epic][0].parent / 'backlog')
        self.assertEqual(items[task][1]['custom'], {'preserve': True})
        self.assertIn('## Acceptance record', items[task][2])
        self.assertIn('Reviewed acceptance evidence', items[task][2])
        self.run_work('check')

    def test_reopen_dry_run_leaves_board_index_and_history_unchanged(self):
        group = self.create('group', 'Delivery')
        epic = self.create('epic', 'Search', group)
        task = self.create('task', 'Index titles', epic)
        self.finish(task)
        self.finish(epic)
        self.finish(group)
        self.archive(task, epic, group)
        before = self.board_files()
        head = self.git('rev-parse', 'HEAD')
        output = self.run_work('reopen', task, '--dry-run')
        self.assertIn(f'{task}: archived -> backlog', output)
        self.assertIn(f'{epic}: archived -> wip', output)
        self.assertIn(f'{group}: archived -> wip', output)
        self.assertEqual(before, self.board_files())
        self.assertEqual(self.git('rev-parse', 'HEAD'), head)
        self.assertNotIn(task, work.records(self.root))
        self.run_work('check')

    def test_reopen_blocks_on_archived_dependents_until_reopened(self):
        first = self.create('task', 'Prerequisite', self.create('epic', 'First'))
        second = self.create('task', 'Dependent', self.create('epic', 'Second'))
        self.run_work('depend', second, first)
        self.finish(first)
        self.finish(second)
        self.archive(second)
        for extra in (('--dry-run',), ()):
            error = self.run_work('reopen', first, *extra, ok=False)
            self.assertIn('dependents', error)
            self.assertIn(second, error)
        self.run_work('check')
        self.run_work('reopen', second)
        self.run_work('reopen', first)
        self.run_work('check')

    def test_restore_refuses_to_overwrite_active_files(self):
        epic = self.create('epic', 'Search')
        task = self.create('task', 'Index titles', epic)
        self.finish(task)
        self.archive(task)
        items = work.records(self.root)
        record = work.Archives(self.root).read()[task]
        destination = items[epic][0].parent / 'backlog' / Path(record['path']).name
        destination.mkdir(parents=True)  # Squat on the restore path.
        # A path squat makes the board itself unreadable, so the guard is the
        # last resort inside restore; exercise it at the API level.
        with self.assertRaisesRegex(ValueError, 'Destination exists'):
            work.restore(self.root, items, work.Archives(self.root), record, 'backlog')
        shutil.rmtree(destination)
        self.assertNotIn(task, work.records(self.root))
        self.run_work('reopen', task)
        self.run_work('check')

    def test_restore_completes_existing_container_in_place(self):
        epic = self.create('epic', 'Search')
        task = self.create('task', 'Index titles', epic)
        self.finish(task)
        self.finish(epic)
        self.archive(task)
        self.archive(epic)
        container = self.root / '.work' / 'wip' / f'{epic}-search'
        container.mkdir(parents=True)
        self.run_work('reopen', task)
        items = work.records(self.root)
        self.assertEqual(items[epic][1]['status'], 'wip')
        self.assertEqual(items[task][1]['status'], 'backlog')
        self.assertEqual(items[epic][0], container / 'README.md')
        self.assertEqual(items[task][0].parent, container / 'backlog')
        self.run_work('check')

    def test_repeated_reopen_accept_archive_cycles_preserve_history(self):
        epic = self.create('epic', 'Search')
        task = self.create('task', 'Index titles', epic)
        self.finish(task, evidence='First acceptance')
        self.archive(task)
        self.run_work('reopen', task)
        restored = work.records(self.root)[task]
        self.assertEqual(restored[1]['status'], 'backlog')
        self.assertIn('First acceptance', restored[2])
        self.finish(task, evidence='Second acceptance')
        self.archive(task)
        self.run_work('reopen', task)
        body = work.records(self.root)[task][2]
        self.assertIn('First acceptance', body)
        self.assertIn('Second acceptance', body)
        self.run_work('check')

    def test_create_never_reuses_archived_ids(self):
        epic = self.create('epic', 'Search')
        task = self.create('task', 'Index titles', epic)
        self.finish(task)
        self.archive(task)
        suffix = task.split('-')[1]
        original = work.uuid.uuid4
        calls = []
        def collide_then_random():
            if not calls:
                calls.append(True)
                return uuid.UUID(hex=suffix * 4)
            return original()
        with patch.object(work.uuid, 'uuid4', side_effect=collide_then_random):
            created = self.create('task', 'Collision', epic)
        self.assertNotEqual(created, task)
        self.run_work('check')

    def test_shallow_history_reports_guidance_instead_of_guessing(self):
        epic = self.create('epic', 'Search')
        task = self.create('task', 'Index titles', epic)
        self.finish(task)
        self.git('add', '.work')
        self.git('commit', '-m', 'Board baseline with done task')
        self.archive(task)
        clone = Path(self.tmp.name) / 'shallow'
        self.git('clone', '--depth', '1', self.root.as_uri(), str(clone))
        self.assertNotIn(task, work.records(clone))
        result = subprocess.run([sys.executable, str(SCRIPT), '--root', str(clone), 'check'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        for args in (('show', task), ('reopen', task),
                     ('create', 'task', 'New task', '--parent', epic)):
            with self.subTest(args=args):
                result = subprocess.run([sys.executable, str(SCRIPT), '--root', str(clone), *args],
                                        capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('shallow', result.stderr)

    def test_forward_commands_and_edits_refuse_archived_tickets(self):
        epic = self.create('epic', 'Search')
        task = self.create('task', 'Index titles', epic)
        self.finish(task)
        self.archive(task)
        for args in (('start', task), ('review', task),
                     ('done', task, '--by', 'human', '--evidence', 'Reviewed'),
                     ('assign', task, '--implementer', 'agent', '--reviewer', 'human'),
                     ('depend', task, epic)):
            with self.subTest(args=args):
                self.assertIn('archived; reopen it first', self.run_work(*args, ok=False))
        self.run_work('check')

    def test_live_child_under_archived_parent_is_tolerated_and_repaired(self):
        epic = self.create('epic', 'Search')
        task = self.create('task', 'Index titles', epic)
        self.finish(task)
        self.finish(epic)
        self.ordinary_archive(epic)  # Container gone; live child remains.
        self.run_work('check')
        self.run_work('reopen', task)
        items = work.records(self.root)
        self.assertEqual(items[epic][1]['status'], 'wip')
        self.assertEqual(items[task][1]['status'], 'backlog')
        self.run_work('check')

    def test_reopen_container_relocates_leftover_children_of_all_statuses(self):
        for status in work.STATES:
            with self.subTest(status=status):
                group = self.create('group', 'Delivery')
                epic = self.create('epic', 'Search', group)
                task = self.create('task', 'Index titles', epic)
                self.finish(task)
                self.finish(epic)
                self.finish(group)
                self.ordinary_archive(group)
                # Simulate a hand-edited child status after interrupted removal.
                items = work.records(self.root)
                ep, em, eb = items[epic]
                source = ep.parent
                target = source.parent.parent / status / source.name
                work.write(ep, dict(em, status=status), eb)
                if source != target:
                    source.rename(target)
                before = self.board_files()
                index = (self.root / '.git/index').read_bytes() if (self.root / '.git/index').exists() else None
                head = self.git('rev-parse', 'HEAD')
                task_bytes = work.records(self.root)[task][0].read_bytes()
                self.run_work('check')
                self.run_work('reopen', group, '--dry-run')
                self.assertEqual(before, self.board_files())
                self.assertEqual(head, self.git('rev-parse', 'HEAD'))
                self.assertEqual(index, (self.root / '.git/index').read_bytes()
                                 if (self.root / '.git/index').exists() else None)
                self.run_work('reopen', group)
                items = work.records(self.root)
                self.assertEqual(items[epic][0].parent.parent, items[group][0].parent / status)
                self.assertEqual(items[epic][1]['status'], status)
                self.assertEqual(items[task][0].read_bytes(), task_bytes)
                self.run_work('check')

    def test_reopen_backlog_child_repairs_archived_parent(self):
        epic = self.create('epic', 'Search')
        task = self.create('task', 'Index titles', epic)
        self.finish(task)
        self.finish(epic)
        self.ordinary_archive(epic)
        tp, tm, tb = work.records(self.root)[task]
        destination = tp.parent.parent / 'backlog' / tp.name
        work.write(tp, dict(tm, status='backlog'), tb)
        tp.rename(destination)
        self.run_work('check')
        before = self.board_files()
        self.run_work('reopen', task, '--dry-run')
        self.assertEqual(before, self.board_files())
        self.run_work('reopen', task)
        items = work.records(self.root)
        self.assertEqual(items[epic][1]['status'], 'wip')
        self.assertEqual(items[task][1]['status'], 'backlog')
        self.run_work('check')
        self.assertIn('Cannot move backlog to backlog', self.run_work('reopen', task, ok=False))

    def test_reopen_epic_relocates_leftover_tasks_of_all_statuses(self):
        for status in work.STATES:
            with self.subTest(status=status):
                epic = self.create('epic', 'Search')
                task = self.create('task', 'Index titles', epic)
                self.finish(task)
                self.finish(epic)
                self.ordinary_archive(epic)
                tp, tm, tb = work.records(self.root)[task]
                destination = tp.parent.parent / status / tp.name
                work.write(tp, dict(tm, status=status), tb)
                if tp != destination:
                    tp.rename(destination)
                original = destination.read_bytes()
                self.run_work('check')
                self.run_work('reopen', epic)
                items = work.records(self.root)
                self.assertEqual(items[task][0].parent, items[epic][0].parent / status)
                self.assertEqual(items[task][0].read_bytes(), original)
                self.run_work('check')

    def test_restore_descendant_collision_preserves_existing_files(self):
        epic = self.create('epic', 'Search')
        task = self.create('task', 'Index titles', epic)
        self.finish(task)
        self.finish(epic)
        path, _, _ = work.records(self.root)[epic]
        self.ordinary_archive(epic)
        items = work.records(self.root)
        record = work.Archives(self.root).read()[epic]
        container = self.root / '.work/backlog' / path.parent.name
        destination = container / 'done' / items[task][0].name
        destination.parent.mkdir(parents=True)
        destination.write_bytes(b'Unrelated content, never overwrite\n')
        before = self.board_files()
        with self.assertRaisesRegex(ValueError, 'Destination exists'):
            work.restore(self.root, items, work.Archives(self.root), record, 'backlog')
        self.assertEqual(before, self.board_files())


if __name__ == '__main__':
    unittest.main()
