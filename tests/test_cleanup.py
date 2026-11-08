import importlib.util
import argparse
from contextlib import redirect_stdout, redirect_stderr
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1]
SCRIPT = SOURCE / '.work/tools/work.py'
spec = importlib.util.spec_from_file_location('work_commit', SCRIPT)
work = importlib.util.module_from_spec(spec)
spec.loader.exec_module(work)


class CleanupBackendTests(unittest.TestCase):
    """Post-merge cleanup transaction and recovery, not the commit CLI.

    Keep the former archive writer's safety regressions for the cleanup backend
    now used by work merge. The retained commit CLI has its own test suite.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'repo'
        self.root.mkdir()
        self.git('init', '-b', 'main')
        self.git('config', 'user.name', 'Commit Test')
        self.git('config', 'user.email', 'commit@example.invalid')
        self.git('config', 'commit.gpgsign', 'false')
        self.run_work('init')
        self.git('add', '.work')
        self.git('commit', '-m', 'base')

    def git(self, *args, input=None, ok=True):
        result = subprocess.run(['git', '-C', str(self.root), *args], input=input,
                                capture_output=True, text=True)
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip() if ok else result

    def commit_msg(self, message):
        self.git('commit', '--allow-empty', '-F', '-', input=message)

    def run_work(self, *args, ok=True, env=None):
        # Historical "commit" test operations exercise cleanup_command directly.
        # test_retained.py tests the real public commit/merge CLI end-to-end.
        if args[0] == 'commit' and '--help' not in args:
            return self.cleanup_backend(*args[1:], ok=ok, env=env)
        result = subprocess.run([sys.executable, str(SCRIPT), '--root', str(self.root), *args],
                                capture_output=True, text=True, env=env)
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip() if ok else result.stderr.strip()

    def cleanup_backend(self, *arguments, ok=True, env=None):
        parser = argparse.ArgumentParser()
        parser.add_argument('ids', nargs='*')
        parser.add_argument('-m', '--message')
        for flag in ('dry-run', 'push', 'recover'):
            parser.add_argument('--' + flag, action='store_true')
        out, err = io.StringIO(), io.StringIO()
        failed = False
        with redirect_stdout(out), redirect_stderr(err), mock.patch.dict(os.environ, env or {}):
            try:
                args = parser.parse_args(arguments)
                if args.recover and (args.ids or args.message is not None or args.push or args.dry_run):
                    work.fail('--recover cannot be combined with other flags')
                with work.locked(self.root):
                    if args.recover:
                        work.commit_recover(self.root)
                    else:
                        items, archives = work.records(self.root), work.Archives(self.root)
                        work.check(self.root, items, archives)
                        work.cleanup_command(self.root, items, archives, args)
            except (ValueError, OSError) as error:
                failed = True
                print(str(error), file=err)
        self.assertEqual(failed, not ok, err.getvalue() or out.getvalue())
        return (err.getvalue() if failed else out.getvalue()).strip()

    def create(self, kind, title='Example', parent=None):
        args = ['create', kind, title]
        if parent:
            args += ['--parent', parent]
        return self.run_work(*args)

    def finish(self, identity, evidence='Reviewed evidence'):
        path, meta, body = work.records(self.root)[identity]
        work.write(path, meta, body.replace('- [ ]', '- [x]'))
        self.run_work('assign', identity, '--implementer', 'agent', '--reviewer', 'human')
        self.run_work('start', identity)
        self.run_work('review', identity)
        self.run_work('done', identity, '--by', 'human', '--evidence', evidence)
        # Cleanup consumes retained, committed done records. These fixtures
        # directly construct that historical state before exercising its backend.
        _, meta, body = work.records(self.root)[identity]
        work.persist(self.root, work.records(self.root), identity, dict(meta, status='done'), body)

    def set_branch(self, identity, branch):
        path, meta, body = work.records(self.root)[identity]
        work.write(path, dict(meta, branch=branch), body)

    def head(self):
        return self.git('rev-parse', 'HEAD')

    def stage(self):
        self.git('add', '.work')

    def interrupt(self, publish=False):
        entries, units = work.commit_prepare(self.root, work.records(self.root), 'main')
        message = work.commit_message(None, entries)
        original = work._git

        def interrupted(root, *args, **kwargs):
            if args[0] == 'commit' and kwargs.get('input') == message:
                if publish:
                    result = original(root, *args, **kwargs)
                    self.assertEqual(result.returncode, 0, result.stderr)
                raise SystemExit('simulated interruption')
            return original(root, *args, **kwargs)
        with mock.patch.object(work, '_git', side_effect=interrupted):
            with self.assertRaises(SystemExit):
                work.commit_apply(self.root, 'main', entries, units, message)

    def test_dry_run_shows_selection_and_changes_nothing(self):
        epic = self.create('epic', 'Search')
        task = self.create('task', 'Index titles', epic)
        self.finish(task)
        self.stage()
        head_before = self.head()
        index_before = (self.root / '.git/index').read_bytes()
        board_before = {p.relative_to(self.root).as_posix(): p.read_bytes()
                        for p in (self.root / '.work').rglob('*') if p.is_file()}
        output = self.run_work('commit', '-m', 'feat(search): index titles', '--dry-run')
        self.assertIn('Branch: main', output)
        self.assertIn(task, output)
        self.assertIn('.work/', output)
        self.assertIn('Proposed commit message:', output)
        self.assertIn('## Completed tickets', output)
        self.assertNotIn('Ticket-Archive:', output)
        self.assertIn('- ' + task + ' — Index titles', output)
        self.assertEqual(self.head(), head_before)
        self.assertEqual((self.root / '.git/index').read_bytes(), index_before)
        self.assertEqual(board_before, {p.relative_to(self.root).as_posix(): p.read_bytes()
                                        for p in (self.root / '.work').rglob('*') if p.is_file()})
        self.assertIn(task, work.records(self.root))

    def test_commit_archives_leaf_and_syncs_board(self):
        epic = self.create('epic', 'Search')
        task = self.create('task', 'Index titles', epic)
        self.finish(task)
        (self.root / 'notes.txt').write_text('unrelated unstaged\n')
        self.stage()
        self.run_work('commit', '-m', 'feat(search): index titles')
        self.assertNotIn(task, work.records(self.root))
        self.assertIn(task, work.archive_history(self.root))
        status = self.git('status', '--porcelain')
        self.assertEqual(status, '?? notes.txt')
        self.assertNotIn('Ticket-Archive:', self.git('log', '-1', '--format=%B'))
        self.assertIn('unrelated', (self.root / 'notes.txt').read_text())

    def test_exact_staged_bytes_are_committed_and_unstaged_excluded(self):
        epic = self.create('epic', 'Search')
        task = self.create('task', 'Index titles', epic)
        self.finish(task)
        impl = self.root / 'impl.txt'
        impl.write_text('staged implementation bytes\n')
        self.stage()
        self.git('add', 'impl.txt')
        impl.write_text('UNSTAGED EDIT MUST NOT BE COMMITTED\n')
        self.run_work('commit', '-m', 'feat(search): index titles')
        committed = self.git('show', 'HEAD:impl.txt')
        self.assertEqual(committed, 'staged implementation bytes')

    def test_explicit_branch_matching_current_is_selected(self):
        epic = self.create('epic', 'Search')
        task = self.create('task', 'Index titles', epic)
        self.finish(task)
        self.set_branch(task, 'main')
        self.stage()
        output = self.run_work('commit', '-m', 'feat(search): index titles', '--dry-run')
        self.assertIn(task, output)

    def test_explicit_branch_elsewhere_is_not_selected(self):
        epic = self.create('epic', 'Search')
        task = self.create('task', 'Index titles', epic)
        self.finish(task)
        self.set_branch(task, 'feature/elsewhere')
        self.stage()
        error = self.run_work('commit', '-m', 'feat(other): elsewhere', '--dry-run', ok=False)
        self.assertIn('No accepted done tickets', error)

    def test_unset_branch_matches_current(self):
        epic = self.create('epic', 'Search')
        task = self.create('task', 'Index titles', epic)
        self.finish(task)
        self.stage()
        output = self.run_work('commit', '-m', 'feat(search): index titles', '--dry-run')
        self.assertIn(task, output)

    def test_container_removed_only_when_children_complete(self):
        epic = self.create('epic', 'Container')
        done_child = self.create('task', 'Done child', epic)
        self.create('task', 'Open child', epic)
        self.finish(done_child)
        self.stage()
        output = self.run_work('commit', '-m', 'feat(container): partial', '--dry-run')
        selected_line = next(line for line in output.splitlines() if line.startswith('Selected:'))
        self.assertIn(done_child, selected_line)
        self.assertNotIn(epic, selected_line)

    def test_container_removed_with_all_children_done(self):
        epic = self.create('epic', 'Container')
        done_child = self.create('task', 'Done child', epic)
        open_child = self.create('task', 'Open child', epic)
        self.finish(done_child)
        self.finish(open_child)
        self.finish(epic)
        self.stage()
        self.git('commit', '-m', 'board progress')
        self.run_work('commit', '-m', 'feat(container): complete')
        items = work.records(self.root)
        self.assertNotIn(epic, items)
        self.assertNotIn(done_child, items)
        self.assertNotIn(open_child, items)
        for identity in (epic, done_child, open_child):
            self.assertIn(identity, work.archive_history(self.root))

    def test_multiple_tickets_one_archive_commit(self):
        first = self.create('task', 'First', self.create('epic', 'A'))
        second = self.create('task', 'Second', self.create('epic', 'B'))
        self.finish(first)
        self.finish(second)
        self.stage()
        self.run_work('commit', '-m', 'feat(multi): two tickets')
        history = work.archive_history(self.root)
        self.assertIn(first, history)
        self.assertIn(second, history)
        self.assertEqual(self.git('rev-list', '--count', 'HEAD'), '3')

    def test_empty_selection_errors(self):
        self.create('epic', 'Search')
        self.stage()
        error = self.run_work('commit', '-m', 'chore: nothing', '--dry-run', ok=False)
        self.assertIn('No accepted done tickets', error)

    def test_untracked_board_files_are_rejected(self):
        epic = self.create('epic', 'Search')
        task = self.create('task', 'Index titles', epic)
        self.finish(task)
        error = self.run_work('commit', '-m', 'feat: x', '--dry-run', ok=False)
        self.assertIn('git add .work', error)

    def test_unstaged_board_changes_are_rejected(self):
        epic = self.create('epic', 'Search')
        task = self.create('task', 'Index titles', epic)
        self.finish(task)
        self.stage()
        path = work.records(self.root)[task][0]
        path.write_text(path.read_text() + '\n# unstaged edit\n')
        error = self.run_work('commit', '-m', 'feat: x', '--dry-run', ok=False)
        self.assertIn('unstaged changes', error)

    def test_commit_hook_failure_preserves_files_and_index(self):
        epic = self.create('epic', 'Search')
        task = self.create('task', 'Index titles', epic)
        self.finish(task)
        self.stage()
        hook = self.root / '.git/hooks/pre-commit'
        hook.write_text('#!/bin/sh\necho blocked by hook >&2\nexit 1\n')
        hook.chmod(0o755)
        head_before = self.head()
        index_before = (self.root / '.git/index').read_bytes()
        error = self.run_work('commit', '-m', 'feat(search): index titles', ok=False)
        self.assertIn('blocked by hook', error)
        self.assertEqual(self.head(), head_before)
        self.assertIn(task, work.records(self.root))
        self.assertEqual(self.git('rev-list', '--count', 'HEAD'), '1')
        self.assertEqual((self.root / '.git/index').read_bytes(), index_before)

    def test_detached_head_errors(self):
        self.git('checkout', '--detach')
        epic = self.create('epic', 'Search')
        task = self.create('task', 'Index titles', epic)
        self.finish(task)
        self.stage()
        error = self.run_work('commit', '-m', 'feat: x', '--dry-run', ok=False)
        self.assertIn('detached HEAD', error)

    def test_missing_identity_errors_before_removal(self):
        epic = self.create('epic', 'Search')
        task = self.create('task', 'Index titles', epic)
        self.finish(task)
        self.stage()
        self.git('config', '--unset-all', 'user.name')
        self.git('config', '--unset-all', 'user.email')
        env = dict(os.environ, GIT_CONFIG_GLOBAL='/dev/null', GIT_CONFIG_SYSTEM='/dev/null')
        error = self.run_work('commit', '-m', 'feat: x', '--dry-run', ok=False, env=env)
        self.assertIn('identity', error)
        self.assertIn(task, work.records(self.root))

    def test_recover_restores_interrupted_commit(self):
        epic = self.create('epic', 'Search')
        task = self.create('task', 'Index titles', epic)
        self.finish(task)
        self.stage()
        self.commit_msg('track board')
        task_path = work.records(self.root)[task][0]
        relpath = task_path.relative_to(self.root).as_posix()
        content = task_path.read_text(encoding='utf-8')
        self.interrupt()
        self.assertNotIn(task, work.records(self.root))
        output = self.run_work('commit', '--recover')
        self.assertIn('restored', output)
        self.assertIn(task, work.records(self.root))
        self.assertEqual(work.records(self.root)[task][0].read_text(encoding='utf-8'), content)

    def test_recover_after_published_commit_clears_journal(self):
        epic = self.create('epic', 'Search')
        task = self.create('task', 'Index titles', epic)
        self.finish(task)
        self.stage()
        self.interrupt(publish=True)
        output = self.run_work('commit', '--recover')
        self.assertIn('already published', output)
        self.assertFalse((self.root / '.work/.commit-journal.json').exists())
        self.assertNotIn(task, work.records(self.root))

    def test_generated_messages_and_override(self):
        epic = self.create('epic', 'Search')
        task = self.create('task', 'Index titles', epic)
        self.finish(task)
        self.stage()
        preview = self.run_work('commit', task, '--dry-run')
        self.assertIn('task: Index titles', preview)
        self.run_work('commit', task)
        self.assertEqual(self.git('log', '-1', '--format=%s'), 'task: Index titles')
        self.finish(epic)
        self.stage()
        preview = self.run_work('commit', '--dry-run')
        self.assertIn('feat: Search', preview)
        self.assertIn('custom subject', self.run_work('commit', '-m', 'custom subject', '--dry-run'))

    def test_subset_leaves_other_done_ticket_and_container(self):
        epic = self.create('epic', 'Search')
        a = self.create('task', 'First', epic)
        b = self.create('task', 'Second', epic)
        for identity in (a, b, epic):
            self.finish(identity)
        self.stage()
        self.assertIn('select all live descendants', self.run_work('commit', epic, '--dry-run', ok=False))
        self.run_work('commit', a)
        self.assertNotIn(a, work.records(self.root))
        self.assertIn(b, work.records(self.root))
        self.assertIn(epic, work.records(self.root))
        self.run_work('commit', b, epic)
        self.assertNotIn(epic, work.records(self.root))
        self.run_work('check')

    def test_invalid_subset_fails_before_commit(self):
        epic = self.create('epic', 'Search')
        done = self.create('task', 'Done', epic)
        self.finish(done)
        other = self.create('task', 'Open', epic)
        self.stage()
        head = self.head()
        for identity in ('T-00000000', other, epic):
            self.assertIn('not eligible', self.run_work('commit', identity, ok=False))
        self.assertEqual(self.head(), head)
        self.assertIn(done, work.records(self.root))

    def test_rearchive_interruption_restores_latest_content_not_old_archive(self):
        epic = self.create('epic', 'Search')
        task = self.create('task', 'Index titles', epic)
        self.finish(task, 'first acceptance')
        self.stage()
        self.run_work('commit')
        self.run_work('reopen', task)
        self.finish(task, 'second acceptance')
        self.stage()
        latest = work.records(self.root)[task][0].read_bytes()
        head = self.head()
        index = (self.root / '.git/index').read_bytes()
        self.interrupt()
        self.assertIn('restored', self.run_work('commit', '--recover'))
        self.assertEqual(work.records(self.root)[task][0].read_bytes(), latest)
        self.assertIn(b'second acceptance', latest)
        self.assertNotEqual(self.head(), head)  # Preserving the latest acceptance is a real snapshot commit.
        self.assertEqual((self.root / '.git/index').read_bytes(), index)

    def test_recovery_preserves_concurrent_file_edit_and_journal(self):
        task = self.create('task', 'Index', self.create('epic', 'Search'))
        self.finish(task)
        self.stage()
        path = work.records(self.root)[task][0]
        self.interrupt()
        path.write_text('new concurrent content')
        self.assertIn('file changed', self.run_work('commit', '--recover', ok=False))
        self.assertEqual(path.read_text(), 'new concurrent content')
        self.assertTrue((self.root / '.work/.commit-journal.json').exists())

    def test_recovery_preserves_concurrent_index_and_blocks_mutations(self):
        task = self.create('task', 'Index', self.create('epic', 'Search'))
        self.finish(task)
        self.stage()
        self.interrupt(publish=True)
        (self.root / 'new.txt').write_text('staged later')
        self.git('add', 'new.txt')
        index = (self.root / '.git/index').read_bytes()
        self.assertIn('index changed', self.run_work('commit', '--recover', ok=False))
        self.assertEqual((self.root / '.git/index').read_bytes(), index)
        self.assertIn('journal needs attention', self.run_work('create', 'epic', 'Blocked', ok=False))

    def test_unknown_ancillary_file_is_not_swept(self):
        epic = self.create('epic', 'Search')
        self.finish(epic)
        path = work.records(self.root)[epic][0].parent / 'notes.txt'
        path.write_text('not a ticket')
        self.stage()
        self.assertIn('ancillary file', self.run_work('commit', ok=False))
        self.assertEqual(path.read_text(), 'not a ticket')

    def test_push_requires_upstream_and_dry_run_never_contacts_remote(self):
        task = self.create('task', 'Index', self.create('epic', 'Search'))
        self.finish(task)
        self.stage()
        head = self.head()
        self.run_work('commit', '--push', ok=False)
        self.assertEqual(self.head(), head)
        self.git('remote', 'add', 'origin', str(self.root / 'missing-remote'))
        self.git('config', 'branch.main.remote', 'origin')
        self.git('config', 'branch.main.merge', 'refs/heads/main')
        self.assertIn('no network', self.run_work('commit', '--push', '--dry-run'))
        self.assertEqual(self.head(), head)
        error = self.run_work('commit', '--push', ok=False)
        self.assertIn('succeeded locally; push failed', error)
        self.assertNotEqual(self.head(), head)
        self.assertIn(task, work.archive_history(self.root))

    def test_push_to_local_bare_remote(self):
        remote = Path(self.tmp.name) / 'remote.git'
        subprocess.run(['git', 'init', '--bare', str(remote)], capture_output=True, check=True)
        self.git('remote', 'add', 'origin', str(remote))
        self.git('push', '-u', 'origin', 'main')
        self.git('branch', 'unrelated')
        self.git('tag', '-a', 'unrelated-tag', '-m', 'Do not publish this tag')
        self.git('config', 'push.followTags', 'true')
        self.git('config', 'remote.origin.mirror', 'true')
        task = self.create('task', 'Index', self.create('epic', 'Search'))
        self.finish(task)
        self.stage()
        head = self.head()
        self.assertIn('mirror remote', self.run_work('commit', '--push', ok=False))
        self.assertEqual(self.head(), head)
        self.git('config', 'remote.origin.mirror', 'false')
        self.run_work('commit', '--push')
        self.assertEqual(self.git('rev-parse', 'origin/main'), self.head())
        remote_refs = self.git('ls-remote', 'origin')
        self.assertNotIn('unrelated', remote_refs)

    def test_recover_rejects_ambiguous_flags_and_legacy_journal(self):
        for flags in (('--dry-run',), ('--push',), ('-m', 'x'), ('T-1234abcd',)):
            self.assertIn('cannot be combined', self.run_work('commit', '--recover', *flags, ok=False))
        (self.root / '.work/.commit-journal.json').write_text('{"version":1}')
        self.assertIn('recover files manually', self.run_work('commit', '--recover', ok=False))

    def test_help_explains_commands_options_and_examples(self):
        help_text = self.run_work('--help')
        self.assertIn('Validate hierarchy', help_text)
        self.assertIn('Examples:', help_text)
        help_text = self.run_work('commit', '--help')
        for text in ('Implemented tickets', 'Override the autogenerated', 'configured upstream', 'Examples:'):
            self.assertIn(text, help_text)

    def test_signing_failure_preserves_files_index_and_head(self):
        task = self.create('task', 'Index', self.create('epic', 'Search'))
        self.finish(task)
        self.stage()
        self.git('config', 'commit.gpgsign', 'true')
        self.git('config', 'gpg.program', '/bin/false')
        before = (self.root / '.git/index').read_bytes()
        head = self.head()
        self.assertIn('git commit failed', self.run_work('commit', ok=False))
        self.assertEqual(self.head(), head)
        self.assertEqual((self.root / '.git/index').read_bytes(), before)
        self.assertIn(task, work.records(self.root))
        self.assertEqual(self.git('config', 'commit.gpgsign'), 'true')

    def test_successful_hook_is_honored_with_private_index(self):
        task = self.create('task', 'Index', self.create('epic', 'Search'))
        self.finish(task)
        self.stage()
        hook = self.root / '.git/hooks/pre-commit'
        hook.write_text('#!/bin/sh\nprintf "%s" "$GIT_INDEX_FILE" > hook-index.txt\n')
        hook.chmod(0o755)
        self.run_work('commit')
        self.assertNotEqual((self.root / 'hook-index.txt').read_text(), str(self.root / '.git/index'))
        self.assertIn('work-commit-', (self.root / 'hook-index.txt').read_text())

    @unittest.skipUnless(shutil.which('ssh-keygen'), 'SSH signing requires ssh-keygen')
    def test_successful_ssh_signing_preserves_policy_and_verifies_both_commits(self):
        key = Path(self.tmp.name) / 'signing-key'
        subprocess.run(['ssh-keygen', '-q', '-t', 'ed25519', '-N', '', '-f', str(key)],
                       capture_output=True, check=True)
        allowed = Path(self.tmp.name) / 'allowed-signers'
        allowed.write_text('commit@example.invalid ' + key.with_suffix('.pub').read_text())
        self.git('config', 'gpg.format', 'ssh')
        self.git('config', 'user.signingkey', str(key))
        self.git('config', 'gpg.ssh.allowedSignersFile', str(allowed))
        self.git('config', 'commit.gpgsign', 'true')
        task = self.create('task', 'Signed archive', self.create('epic', 'Signing'))
        self.finish(task)
        self.stage()
        before = self.head()
        self.run_work('commit', task)
        for revision in ('HEAD', 'HEAD^'):
            self.git('verify-commit', revision)
        self.assertEqual(self.git('rev-parse', 'HEAD^^'), before)
        self.assertEqual(self.git('config', 'commit.gpgsign'), 'true')
        self.assertEqual(self.git('config', 'user.signingkey'), str(key))
        self.assertIn(task, work.archive_history(self.root))
        self.assertEqual(self.git('status', '--porcelain'), '')

    def test_recovery_preserves_concurrent_mode_edit_and_journal(self):
        task = self.create('task', 'Index', self.create('epic', 'Search'))
        self.finish(task)
        self.stage()
        path = work.records(self.root)[task][0]
        content = path.read_bytes()
        self.interrupt()
        path.write_bytes(content)
        path.chmod(0o755)
        self.assertIn('file changed', self.run_work('commit', '--recover', ok=False))
        self.assertEqual(path.stat().st_mode & 0o777, 0o755)
        self.assertTrue((self.root / '.work/.commit-journal.json').exists())

    def test_recovery_refuses_unrelated_head_advance(self):
        task = self.create('task', 'Index', self.create('epic', 'Search'))
        self.finish(task)
        self.stage()
        self.interrupt()
        self.git('commit', '--allow-empty', '-m', 'unrelated')
        head = self.head()
        self.assertIn('HEAD differs', self.run_work('commit', '--recover', ok=False))
        self.assertEqual(self.head(), head)
        self.assertTrue((self.root / '.work/.commit-journal.json').exists())

    def test_crlf_ticket_archives_exact_bytes(self):
        task = self.create('task', 'Index', self.create('epic', 'Search'))
        self.finish(task)
        path = work.records(self.root)[task][0]
        content = path.read_bytes().replace(b'\n', b'\r\n')
        path.write_bytes(content)
        self.git('config', 'core.autocrlf', 'false')
        self.stage()
        self.run_work('commit')
        self.assertEqual(work.archive_history(self.root)[task]['content'].encode('utf-8'), content)

    def test_stale_selected_content_fails_before_removal(self):
        task = self.create('task', 'Index', self.create('epic', 'Search'))
        self.finish(task)
        self.stage()
        entries, units = work.commit_prepare(self.root, work.records(self.root), 'main')
        path = work.records(self.root)[task][0]
        path.write_text(path.read_text() + '\nConcurrent edit\n')
        latest = path.read_bytes()
        with self.assertRaisesRegex(ValueError, 'Stale selection'):
            work.commit_apply(self.root, 'main', entries, units, work.commit_message(None, entries))
        self.assertEqual(path.read_bytes(), latest)
        self.assertFalse((self.root / '.work/.commit-journal.json').exists())

    def test_modifying_hook_is_reported_without_reset_or_discarding_journal(self):
        task = self.create('task', 'Index', self.create('epic', 'Search'))
        self.finish(task)
        self.stage()
        before = (self.root / '.git/index').read_bytes()
        hook = self.root / '.git/hooks/commit-msg'
        hook.write_text('#!/bin/sh\necho "modified by unsupported hook" >> "$1"\n')
        hook.chmod(0o755)
        head = self.head()
        error = self.run_work('commit', ok=False)
        self.assertIn('Recovery needs attention', error)
        self.assertNotEqual(self.head(), head)
        self.assertEqual((self.root / '.git/index').read_bytes(), before)
        self.assertTrue((self.root / '.work/.commit-journal.json').exists())

    def test_readable_message_has_bounded_subject_and_no_embedded_records(self):
        epic = self.create('epic', 'Search')
        ids = [self.create('task', 'Long title ' * 12, epic) for _ in range(3)]
        for identity in ids:
            self.finish(identity)
            path, meta, body = work.records(self.root)[identity]
            work.write(path, meta, body + '\nLarge historical handoff\n' + 'noise ' * 5000)
        self.stage()
        self.run_work('commit')
        message = self.git('log', '-1', '--format=%B')
        self.assertLessEqual(len(message.splitlines()[0]), 72)
        self.assertLess(len(message), 1000)
        for identity in ids:
            self.assertEqual(message.count(identity), 1)
        for noise in ('\\n', '\\"', '"content":', 'Large historical handoff', 'Acceptance record'):
            self.assertNotIn(noise, message)
        self.assertIn('## Completed tickets', message)
        self.assertNotIn('Ticket-Archive:', message)

    def test_never_committed_records_are_preserved_in_normal_parent_files(self):
        task = self.create('task', 'Index', self.create('epic', 'Search'))
        self.finish(task)
        path = work.records(self.root)[task][0]
        content = path.read_bytes()
        self.stage()
        self.assertIn('Snapshot commit required', self.run_work('commit', '--dry-run'))
        self.run_work('commit')
        raw = subprocess.check_output(['git', '-C', str(self.root), 'show', 'HEAD^:' + str(path.relative_to(self.root))])
        self.assertEqual(raw, content)
        source_message = self.git('log', '-1', '--format=%B', 'HEAD^')
        self.assertNotIn('## Completed tickets', source_message)
        self.assertEqual(source_message.count(task), 1)
        self.assertEqual(work.archive_history(self.root)[task]['content'].encode(), content)
        self.run_work('reopen', task)
        self.assertIn('Acceptance record', work.records(self.root)[task][0].read_text())
        self.run_work('check')

    def test_already_preserved_accepted_records_need_only_one_commit(self):
        task = self.create('task', 'Index', self.create('epic', 'Search'))
        self.finish(task)
        self.stage()
        self.git('commit', '-m', 'Record accepted ticket')
        count = int(self.git('rev-list', '--count', 'HEAD'))
        self.assertIn('no extra commit', self.run_work('commit', '--dry-run'))
        self.run_work('commit')
        self.assertEqual(int(self.git('rev-list', '--count', 'HEAD')), count + 1)
        self.assertIn(task, work.archive_history(self.root))

    def test_archive_hook_failure_retains_snapshot_and_restores_files(self):
        task = self.create('task', 'Index', self.create('epic', 'Search'))
        self.finish(task)
        self.stage()
        path = work.records(self.root)[task][0]
        content = path.read_bytes()
        before = (self.root / '.git/index').read_bytes()
        hook = self.root / '.git/hooks/pre-commit'
        hook.write_text(f'#!/bin/sh\nif [ ! -f "{path.relative_to(self.root)}" ]; then echo archive-blocked >&2; exit 1; fi\n')
        hook.chmod(0o755)
        original = self.head()
        error = self.run_work('commit', ok=False)
        self.assertIn('archive-blocked', error)
        self.assertNotEqual(self.head(), original)
        self.assertEqual(path.read_bytes(), content)
        self.assertEqual((self.root / '.git/index').read_bytes(), before)
        self.assertFalse((self.root / '.work/.commit-journal.json').exists())
        self.assertEqual(self.git('rev-list', '--count', 'HEAD'), '2')
        hook.unlink()
        self.run_work('commit')
        self.assertEqual(self.git('rev-list', '--count', 'HEAD'), '3')
        self.assertIn(task, work.archive_history(self.root))

    def test_interruption_before_snapshot_keeps_original_head_and_files(self):
        task = self.create('task', 'Index', self.create('epic', 'Search'))
        self.finish(task)
        self.stage()
        path = work.records(self.root)[task][0]
        content = path.read_bytes()
        head = self.head()
        entries, units = work.commit_prepare(self.root, work.records(self.root), 'main')
        original = work._git
        def interrupt(root, *args, **kwargs):
            if args[0] == 'commit':
                raise SystemExit('before snapshot')
            return original(root, *args, **kwargs)
        with mock.patch.object(work, '_git', side_effect=interrupt):
            with self.assertRaises(SystemExit):
                work.commit_apply(self.root, 'main', entries, units, work.commit_message(None, entries))
        self.run_work('commit', '--recover')
        self.assertEqual(self.head(), head)
        self.assertEqual(path.read_bytes(), content)

    def test_message_only_ids_do_not_create_archive_records(self):
        for marker in ('Ticket-Archive: 2', 'Ticket-Archive: 3'):
            self.commit_msg('task: missing record\n\n## Completed tickets\n\n- T-1234abcd — Missing\n\n' + marker)
            self.assertEqual(work.archive_history(self.root), {})

    def test_rearchive_after_reopen_uses_latest_saved_files(self):
        task = self.create('task', 'Index', self.create('epic', 'Search'))
        self.finish(task, 'earlier evidence')
        self.stage()
        path = work.records(self.root)[task][0]
        self.git('commit', '-m', 'Record accepted files')
        path.unlink()
        self.stage()
        self.git('commit', '-m', 'Clean up accepted work')
        self.assertIn(task, work.archive_history(self.root))
        self.run_work('reopen', task)
        self.finish(task, 'new evidence')
        self.stage()
        self.run_work('commit')
        self.assertIn('new evidence', work.archive_history(self.root)[task]['content'])

    def test_interruption_just_after_snapshot_retains_it_without_deleting_files(self):
        task = self.create('task', 'Index', self.create('epic', 'Search'))
        self.finish(task)
        self.stage()
        path = work.records(self.root)[task][0]
        content = path.read_bytes()
        entries, units = work.commit_prepare(self.root, work.records(self.root), 'main')
        original = work._git
        def interrupt(root, *args, **kwargs):
            result = original(root, *args, **kwargs)
            if args[0] == 'commit':
                self.assertEqual(result.returncode, 0, result.stderr)
                raise SystemExit('after snapshot')
            return result
        with mock.patch.object(work, '_git', side_effect=interrupt):
            with self.assertRaises(SystemExit):
                work.commit_apply(self.root, 'main', entries, units, work.commit_message(None, entries))
        head = self.head()
        self.assertEqual(path.read_bytes(), content)
        output = self.run_work('commit', '--recover')
        self.assertIn('Snapshot commit', output)
        self.assertIn('retained', output)
        self.assertEqual(self.head(), head)
        self.run_work('commit')
        self.assertEqual(self.git('rev-list', '--count', 'HEAD'), '3')

    def test_message_summaries_do_not_archive_live_records(self):
        task = self.create('task', 'Index', self.create('epic', 'Search'))
        self.finish(task)
        self.stage()
        self.git('commit', '-m', 'record accepted files')
        entries, _ = work.commit_prepare(self.root, work.records(self.root), 'main')
        message = work.commit_message(None, entries) + '\nTicket-Archive: 2\n'
        self.commit_msg(message)
        self.assertEqual(work.archive_history(self.root), {})
        duplicate = message.replace(f'- {task} — Index', f'- {task} — Index\n- {task} — Index')
        self.commit_msg(duplicate)
        self.assertEqual(work.archive_history(self.root), {})
        self.assertIn(task, work.records(self.root))

    def test_group_container_archive_restores_from_file_history(self):
        group = self.create('group', 'Delivery')
        epic = self.create('epic', 'Search', group)
        task = self.create('task', 'Index', epic)
        for identity in (task, epic, group):
            self.finish(identity)
        self.stage()
        self.run_work('commit')
        history = work.archive_history(self.root)
        self.assertEqual(set(history), {group, epic, task})
        self.run_work('reopen', task)
        items = work.records(self.root)
        self.assertEqual(items[group][1]['status'], 'wip')
        self.assertEqual(items[epic][1]['status'], 'wip')
        self.assertEqual(items[task][1]['status'], 'backlog')
        self.run_work('check')

    def test_installed_cli_reads_and_reopens_file_history_from_unrelated_cwd(self):
        task = self.create('task', 'Index', self.create('epic', 'Search'))
        self.finish(task)
        self.stage()
        self.run_work('commit')
        self.run_work('install', str(self.root))
        launcher = self.root / '.workkit/work'
        for args in (('show', task), ('reopen', task), ('check',)):
            result = subprocess.run([str(launcher), '--root', str(self.root), *args],
                                    cwd=self.tmp.name, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(work.records(self.root)[task][1]['status'], 'backlog')

    def test_in_progress_git_operations_are_refused_before_publication(self):
        task = self.create('task', 'Index', self.create('epic', 'Search'))
        self.finish(task)
        self.stage()
        head = self.head()
        before = (self.root / '.git/index').read_bytes()
        for state in ('MERGE_HEAD', 'CHERRY_PICK_HEAD', 'REVERT_HEAD'):
            marker = self.root / '.git' / state
            marker.write_text(head + '\n')
            try:
                self.assertIn('in-progress Git operation', self.run_work('commit', ok=False))
                self.assertEqual(self.head(), head)
                self.assertEqual((self.root / '.git/index').read_bytes(), before)
                self.assertIn(task, work.records(self.root))
            finally:
                marker.unlink()


if __name__ == '__main__':
    unittest.main()
