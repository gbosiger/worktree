"""Public implemented -> retained done -> squash merge/cleanup workflow."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1]
SCRIPT = SOURCE / '.work/tools/work.py'
spec = importlib.util.spec_from_file_location('retained_work', SCRIPT)
work = importlib.util.module_from_spec(spec)
spec.loader.exec_module(work)


class RetainedWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'feature'
        self.root.mkdir()
        self.git('init', '-b', 'main')
        self.git('config', 'user.name', 'Workflow Test')
        self.git('config', 'user.email', 'workflow@example.invalid')
        self.git('config', 'commit.gpgsign', 'false')
        self.run_work('init')
        self.epic = self.run_work('create', 'epic', 'Retained feature')
        self.task = self.run_work('create', 'task', 'First change', '--parent', self.epic)
        path, meta, body = work.records(self.root)[self.epic]
        work.write(path, dict(meta, branch='feature/example', base_branch='main'), body)
        (self.root / 'app.txt').write_text('base\n')
        self.git('add', '.')
        self.git('commit', '-m', 'Base')
        self.base = self.git('rev-parse', 'HEAD')
        self.git('checkout', '-b', 'feature/example')
        self.addCleanup(self.clean_merge_worktrees)

    def clean_merge_worktrees(self):
        # Remove only worktrees created by this disposable fixture's merge.
        folder = self.root / '.git/worktree-tickets'
        for path in folder.glob('merge-*.json'):
            data = json.loads(path.read_text())
            target = data.get('target_root')
            if data.get('owned') and target and Path(target).name.startswith('work-merge-'):
                self.git('worktree', 'remove', '--force', '--', target, ok=False)

    def git(self, *args, ok=True, root=None):
        result = subprocess.run(['git', '-C', str(root or self.root), *args], capture_output=True, text=True)
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip() if ok else result

    def run_work(self, *args, ok=True, root=None):
        result = subprocess.run([sys.executable, str(SCRIPT), '--root', str(root or self.root), *args],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode == 0, ok, result.stderr or result.stdout)
        return (result.stdout if ok else result.stderr).strip()

    def approve(self, identity):
        path, meta, body = work.records(self.root)[identity]
        work.write(path, meta, body.replace('- [ ]', '- [x]'))
        self.run_work('assign', identity, '--implementer', 'agent', '--reviewer', 'agent')
        self.run_work('start', identity)
        self.run_work('review', identity)
        self.run_work('done', identity, '--by', 'agent', '--evidence', 'Reviewed test fixture')

    def commit_queue(self, *ids):
        self.git('add', '.work')
        return self.run_work('commit', *ids)

    def prepare_epic(self):
        self.approve(self.task)
        self.approve(self.epic)
        self.commit_queue(self.epic)
        self.source_head = self.git('rev-parse', 'HEAD')

    def snapshot(self):
        return {path.relative_to(self.root).as_posix(): path.read_bytes()
                for path in self.root.rglob('*') if path.is_file()}

    def test_approval_queues_and_commit_retains_exact_handoff(self):
        self.approve(self.task)
        path, meta, body = work.records(self.root)[self.task]
        self.assertEqual(meta['status'], 'implemented')
        self.assertEqual(path.parent.name, 'implemented')
        (self.root / 'app.txt').write_text('staged\n')
        self.git('add', 'app.txt', '.work')
        (self.root / 'app.txt').write_text('unstaged\n')
        head = self.git('rev-parse', 'HEAD')
        self.run_work('commit')
        path, meta, after = work.records(self.root)[self.task]
        self.assertEqual(meta['status'], 'done')
        self.assertEqual(path.parent.name, 'done')
        self.assertEqual(body, after)
        self.assertEqual(self.git('rev-list', '--count', f'{head}..HEAD'), '1')
        self.assertIn(self.task, self.git('log', '-1', '--format=%B'))
        self.assertEqual(self.git('show', 'HEAD:app.txt'), 'staged')
        self.assertEqual((self.root / 'app.txt').read_text(), 'unstaged\n')
        self.assertEqual(work.archive_history(self.root), {})
        self.assertIn('No implemented tickets', self.run_work('commit', ok=False))

    def test_commit_message_only_uses_newly_implemented_work(self):
        self.approve(self.task)
        self.commit_queue()
        second = self.run_work('create', 'task', 'Second change', '--parent', self.epic)
        self.approve(second)
        self.commit_queue()
        message = self.git('log', '-1', '--format=%B')
        self.assertIn(second, message)
        self.assertNotIn(self.task, message)
        self.assertEqual(work.records(self.root)[self.task][1]['status'], 'done')

    def test_implemented_prerequisite_and_reopen_guards(self):
        second = self.run_work('create', 'task', 'Dependent', '--parent', self.epic)
        self.run_work('depend', second, self.task)
        self.approve(self.task)
        self.approve(second)
        self.assertIn(second, self.run_work('reopen', self.task, ok=False))
        self.run_work('reopen', second)
        self.run_work('reopen', self.task)
        self.run_work('check')

    def test_container_commit_carries_previously_done_children(self):
        self.approve(self.task)
        self.commit_queue()
        content = work.records(self.root)[self.task][0].read_bytes()
        self.approve(self.epic)
        self.commit_queue(self.epic)
        items = work.records(self.root)
        self.assertEqual(items[self.epic][1]['status'], 'done')
        self.assertEqual(items[self.task][0].read_bytes(), content)
        self.assertEqual(items[self.task][0].parent, items[self.epic][0].parent / 'done')

    def test_commit_dry_run_changes_no_files_objects_or_index(self):
        self.approve(self.task)
        self.git('add', '.work')
        before = self.snapshot()
        self.assertIn('no deletions', self.run_work('commit', '--dry-run'))
        self.assertEqual(before, self.snapshot())

    def test_failed_commit_restores_implemented_files_and_index(self):
        self.approve(self.task)
        self.git('add', '.work')
        before = work.records(self.root)[self.task][0].read_bytes()
        index = (self.root / '.git/index').read_bytes()
        hook = self.root / '.git/hooks/pre-commit'
        hook.write_text('#!/bin/sh\nexit 1\n')
        hook.chmod(0o755)
        self.assertIn('git commit failed', self.run_work('commit', ok=False))
        path, meta, _ = work.records(self.root)[self.task]
        self.assertEqual(meta['status'], 'implemented')
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual((self.root / '.git/index').read_bytes(), index)
        self.assertFalse((self.root / '.work/.commit-journal.json').exists())

    def test_commit_dry_run_lists_exact_retained_leaf_path(self):
        self.approve(self.task)
        self.git('add', '.work')
        source = work.records(self.root)[self.task][0]
        destination = source.parent.parent / 'done' / source.name
        before = self.snapshot()
        output = self.run_work('commit', '--dry-run')
        self.assertIn(f'  {self.task} -> {destination.relative_to(self.root).as_posix()}\n', output)
        self.assertEqual(before, self.snapshot())

    def test_commit_dry_run_lists_only_selected_retained_paths(self):
        second = self.run_work('create', 'task', 'Not selected', '--parent', self.epic)
        self.approve(self.task)
        self.approve(second)
        self.git('add', '.work')
        before = self.snapshot()
        output = self.run_work('commit', self.task, '--dry-run')
        paths = output.split('Retained ticket paths:\n', 1)[1].split('Staged changes:\n', 1)[0]
        self.assertIn(self.task, paths)
        self.assertNotIn(second, paths)
        self.assertEqual(len(paths.splitlines()), 1)
        self.assertEqual(before, self.snapshot())

    def test_commit_dry_run_lists_nested_container_destinations(self):
        group = self.run_work('create', 'group', 'Release group')
        epic = self.run_work('create', 'epic', 'Nested feature', '--parent', group)
        task = self.run_work('create', 'task', 'Nested change', '--parent', epic)
        for identity in (task, epic, group):
            self.approve(identity)
        items = work.records(self.root)
        group_name = items[group][0].parent.name
        epic_name = items[epic][0].parent.name
        base = Path('.work/done') / group_name
        expected = {
            group: base / 'README.md',
            epic: base / 'done' / epic_name / 'README.md',
            task: base / 'done' / epic_name / 'done' / items[task][0].name,
        }
        self.git('add', '.work')
        before = self.snapshot()
        output = self.run_work('commit', group, '--dry-run')
        paths = output.split('Retained ticket paths:\n', 1)[1].split('Staged changes:\n', 1)[0]
        self.assertEqual(set(paths.splitlines()),
                         {f'  {identity} -> {path.as_posix()}' for identity, path in expected.items()})
        self.assertEqual(before, self.snapshot())

    def test_interrupted_retained_commit_recovers_before_and_after_publication(self):
        for published in (False, True):
            with self.subTest(published=published):
                if published:
                    self.run_work('reopen', self.task)
                self.approve(self.task)
                self.git('add', '.work')
                items = work.records(self.root)
                selected = work.completed_queue(items, 'feature/example', [])
                _, units = work.commit_prepare(self.root, items, 'feature/example', selection=selected)
                before, after, entries = work.retained_plan(self.root, items, selected, units)
                message = work.commit_message(None, entries, verb='complete')
                original = work._git

                def interrupted(root, *args, **kwargs):
                    if args[0] == 'commit':
                        if published:
                            original(root, *args, **kwargs)
                        raise SystemExit('interrupted')
                    return original(root, *args, **kwargs)

                with patch.object(work, '_git', side_effect=interrupted):
                    with self.assertRaises(SystemExit):
                        work.retained_apply(self.root, 'feature/example', before, after, message)
                self.run_work('commit', '--recover')
                self.assertEqual(work.records(self.root)[self.task][1]['status'], 'done' if published else 'implemented')

    def test_merge_preserves_parent_snapshot_and_automatically_cleans_once(self):
        self.prepare_epic()
        before = self.snapshot()
        self.assertIn('cleanup commit', self.run_work('merge', self.epic, '--dry-run'))
        self.assertEqual(before, self.snapshot())
        self.run_work('merge', self.epic)
        self.assertEqual(self.git('rev-parse', 'HEAD'), self.source_head)
        self.assertEqual(self.git('branch', '--show-current'), 'feature/example')
        self.assertEqual(self.git('rev-list', '--count', f'{self.base}..main'), '2')
        history = work.archive_history(self.root, 'main')
        self.assertEqual(set(history), {self.epic, self.task})
        self.assertEqual(self.git('merge-base', '--is-ancestor', self.source_head, 'main', ok=False).returncode, 1)
        self.assertEqual(work.records(self.root)[self.task][1]['status'], 'done')
        self.assertIn('already merged and cleaned', self.run_work('merge', self.epic, ok=False))

    def test_fresh_main_only_clone_can_show_and_reopen_without_feature_history(self):
        self.prepare_epic()
        self.run_work('merge', self.epic)
        clone = Path(self.temp.name) / 'main-only'
        self.git('clone', '--single-branch', '--branch', 'main', self.root.as_uri(), str(clone))
        self.assertNotIn('feature/example', self.git('branch', '-a', root=clone))
        self.assertIn('Acceptance record', self.run_work('show', self.task, root=clone))
        self.run_work('reopen', self.task, root=clone)
        items = work.records(clone)
        self.assertEqual(items[self.task][1]['status'], 'backlog')
        self.assertEqual(items[self.epic][1]['status'], 'wip')

    def test_merge_restores_previously_archived_children_before_squashing(self):
        old = self.run_work('create', 'task', 'Earlier archived work', '--parent', self.epic)
        self.approve(old)
        _, meta, body = work.records(self.root)[old]
        work.persist(self.root, work.records(self.root), old, dict(meta, status='done'), body)
        self.git('add', '.work')
        self.git('commit', '-m', 'Old accepted snapshot')
        work.records(self.root)[old][0].unlink()
        self.git('add', '-u')
        self.git('commit', '-m', 'Old archival')
        self.prepare_epic()
        self.run_work('merge', self.epic)
        self.assertEqual(set(work.archive_history(self.root, 'main')), {self.epic, self.task, old})

    def test_merge_requires_done_epic_and_clean_source(self):
        self.assertIn('approved and committed', self.run_work('merge', self.epic, ok=False))
        self.prepare_epic()
        (self.root / 'app.txt').write_text('Uncommitted progress\n')
        before = (self.root / 'app.txt').read_bytes()
        self.assertIn('clean checkout', self.run_work('merge', self.epic, ok=False))
        self.assertEqual((self.root / 'app.txt').read_bytes(), before)

    def test_standalone_merge_keeps_nonconflicting_unrelated_board_additions(self):
        other = self.run_work('create', 'epic', 'Separate planned feature')
        self.prepare_epic()
        other_path = work.records(self.root)[other][0].relative_to(self.root).as_posix()
        content = (self.root / other_path).read_text()
        self.run_work('merge', self.epic)
        self.assertEqual(self.git('show', f'main:{other_path}'), content.rstrip())
        self.assertEqual(set(work.archive_history(self.root, 'main')), {self.epic, self.task})

    def test_reapproved_standalone_followup_can_restore_a_cleaned_tree(self):
        self.prepare_epic()
        self.run_work('merge', self.epic)
        self.run_work('reopen', self.task)
        self.approve(self.task)
        self.run_work('review', self.epic)
        self.run_work('done', self.epic, '--by', 'agent', '--evidence', 'Reviewed follow-up')
        self.commit_queue(self.epic)
        self.run_work('merge', self.epic)
        self.assertEqual(self.git('rev-list', '--count', f'{self.base}..main'), '4')
        self.assertIn('Reviewed follow-up', work.archive_history(self.root, 'main')[self.epic]['content'])

    def test_failed_cleanup_resumes_without_another_merge_commit(self):
        self.prepare_epic()
        path = work.records(self.root)[self.epic][0].relative_to(self.root)
        hook = self.root / '.git/hooks/pre-commit'
        hook.write_text(f'#!/bin/sh\ntest -f "{path}"\n')
        hook.chmod(0o755)
        self.assertIn('git commit failed', self.run_work('merge', self.epic, ok=False))
        self.assertEqual(self.git('rev-list', '--count', f'{self.base}..main'), '1')
        hook.unlink()
        self.run_work('merge', self.epic, '--recover')
        self.assertEqual(self.git('rev-list', '--count', f'{self.base}..main'), '2')
        self.assertEqual(set(work.archive_history(self.root, 'main')), {self.epic, self.task})

    def test_failed_integration_commit_can_retry(self):
        self.prepare_epic()
        hook = self.root / '.git/hooks/pre-commit'
        hook.write_text('#!/bin/sh\nexit 1\n')
        hook.chmod(0o755)
        self.assertIn('Merge commit failed', self.run_work('merge', self.epic, ok=False))
        self.assertEqual(self.git('rev-parse', 'main'), self.base)
        hook.unlink()
        self.run_work('merge', self.epic, '--recover')
        self.assertEqual(self.git('rev-list', '--count', f'{self.base}..main'), '2')

    def test_existing_dirty_target_is_not_modified(self):
        self.prepare_epic()
        target = Path(self.temp.name) / 'main-target'
        self.git('worktree', 'add', str(target), 'main')
        (target / 'app.txt').write_text('Keep target work\n')
        self.assertIn('clean checkout', self.run_work('merge', self.epic, ok=False))
        self.assertEqual((target / 'app.txt').read_text(), 'Keep target work\n')
        self.assertFalse(work.merge_journal_path(self.root, self.epic).exists())

    def test_merge_conflict_leaves_source_untouched_and_can_resume(self):
        (self.root / 'app.txt').write_text('feature\n')
        self.git('add', 'app.txt')
        self.prepare_epic()
        target = Path(self.temp.name) / 'main-target'
        self.git('worktree', 'add', str(target), 'main')
        (target / 'app.txt').write_text('main\n')
        self.git('add', 'app.txt', root=target)
        self.git('commit', '-m', 'Main changed', root=target)
        self.assertIn('Merge stopped', self.run_work('merge', self.epic, ok=False))
        self.assertEqual(self.git('rev-parse', 'HEAD'), self.source_head)
        (target / 'app.txt').write_text('resolved\n')
        self.git('add', 'app.txt', root=target)
        self.run_work('merge', self.epic, '--recover')
        self.assertEqual(self.git('show', 'main:app.txt'), 'resolved')

    def interrupt_queued_commit(self):
        self.approve(self.task)
        self.git('add', '.work')
        items = work.records(self.root)
        selected = work.completed_queue(items, 'feature/example', [])
        _, units = work.commit_prepare(self.root, items, 'feature/example', selection=selected)
        before, after, entries = work.retained_plan(self.root, items, selected, units)
        original = work._git

        def stop(root, *args, **kwargs):
            if args[0] == 'commit':
                raise SystemExit('interrupted')
            return original(root, *args, **kwargs)

        with patch.object(work, '_git', side_effect=stop):
            with self.assertRaises(SystemExit):
                work.retained_apply(self.root, 'feature/example', before, after,
                                    work.commit_message(None, entries, verb='complete'))

    def test_retained_recovery_preserves_concurrent_file_edit(self):
        self.interrupt_queued_commit()
        path = work.records(self.root)[self.task][0]
        path.write_text('Concurrent user content\n')
        self.assertIn('file changed', self.run_work('commit', '--recover', ok=False))
        self.assertEqual(path.read_text(), 'Concurrent user content\n')
        self.assertTrue((self.root / '.work/.commit-journal.json').exists())

    def test_retained_recovery_preserves_concurrent_staging(self):
        self.interrupt_queued_commit()
        (self.root / 'later.txt').write_text('Staged after interruption\n')
        self.git('add', 'later.txt')
        index = (self.root / '.git/index').read_bytes()
        self.assertIn('index changed', self.run_work('commit', '--recover', ok=False))
        self.assertEqual((self.root / '.git/index').read_bytes(), index)

    def test_interruption_before_git_merge_can_resume(self):
        self.prepare_epic()
        original = work._git

        def stop(root, *args, **kwargs):
            if args[0] == 'merge':
                raise SystemExit('before git merge')
            return original(root, *args, **kwargs)

        with patch.object(work, '_git', side_effect=stop):
            with self.assertRaises(SystemExit):
                work.merge_command(self.root, work.records(self.root), work.Archives(self.root),
                                   SimpleNamespace(id=self.epic, dry_run=False, recover=False))
        self.run_work('merge', self.epic, '--recover')
        self.assertEqual(self.git('rev-list', '--count', f'{self.base}..main'), '2')

    def test_existing_version_one_epic_journal_remains_recoverable(self):
        self.prepare_epic()
        original = work._git

        def stop(root, *args, **kwargs):
            if args[0] == 'merge':
                raise SystemExit('before merge')
            return original(root, *args, **kwargs)

        with patch.object(work, '_git', side_effect=stop):
            with self.assertRaises(SystemExit):
                work.merge_command(self.root, work.records(self.root), work.Archives(self.root),
                                   SimpleNamespace(id=self.epic, dry_run=False, recover=False))
        path = work.merge_journal_path(self.root, self.epic)
        data = json.loads(path.read_text())
        data['version'] = 1
        del data['retain'], data['board']
        path.write_text(json.dumps(data))
        self.run_work('merge', self.epic, '--recover')
        self.assertEqual(self.git('rev-list', '--count', f'{self.base}..main'), '2')

    def test_interruption_after_cleanup_does_not_repeat_commits(self):
        self.prepare_epic()
        original = work._git

        def stop(root, *args, **kwargs):
            if args[:2] == ('worktree', 'remove'):
                raise SystemExit('after cleanup')
            return original(root, *args, **kwargs)

        with patch.object(work, '_git', side_effect=stop):
            with self.assertRaises(SystemExit):
                work.merge_command(self.root, work.records(self.root), work.Archives(self.root),
                                   SimpleNamespace(id=self.epic, dry_run=False, recover=False))
        after = self.git('rev-parse', 'main')
        self.run_work('merge', self.epic, '--recover')
        self.assertEqual(self.git('rev-parse', 'main'), after)
        self.assertFalse(work.merge_journal_path(self.root, self.epic).exists())

    def test_modifying_merge_hook_retains_worktree_and_ref_for_inspection(self):
        self.prepare_epic()
        hook = self.root / '.git/hooks/commit-msg'
        hook.write_text('#!/bin/sh\necho unexpected-message >> "$1"\n')
        hook.chmod(0o755)
        self.assertIn('Unexpected integration commit', self.run_work('merge', self.epic, ok=False))
        changed = self.git('rev-parse', 'main')
        self.assertNotEqual(changed, self.base)
        self.assertEqual(self.git('rev-parse', 'HEAD'), self.source_head)
        self.assertTrue(work.merge_journal_path(self.root, self.epic).exists())
        hook.unlink()
        self.assertIn('Unexpected integration commit', self.run_work('merge', self.epic, '--recover', ok=False))
        self.assertEqual(self.git('rev-parse', 'main'), changed)


if __name__ == '__main__':
    unittest.main()
