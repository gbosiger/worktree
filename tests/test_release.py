"""Shared container integration, with focused two-level release regressions."""
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

import test_retained as retained
from test_retained import work


class ReleaseWorkflowTests(unittest.TestCase):
    git = retained.RetainedWorkflowTests.git
    run_work = retained.RetainedWorkflowTests.run_work
    commit_queue = retained.RetainedWorkflowTests.commit_queue
    snapshot = retained.RetainedWorkflowTests.snapshot
    clean_merge_worktrees = retained.RetainedWorkflowTests.clean_merge_worktrees

    def approve(self, identity):
        path, meta, body = work.records(self.root)[identity]
        work.write(path, meta, body.replace('- [ ]', '- [x]'))
        self.run_work('assign', identity, '--implementer', 'agent', '--reviewer', 'agent')
        if meta['status'] != 'wip':
            self.run_work('start', identity)
        self.run_work('review', identity)
        self.run_work('done', identity, '--by', 'agent', '--evidence', 'Reviewed release fixture')

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'release'
        self.root.mkdir()
        self.git('init', '-b', 'main')
        for key, value in (('user.name', 'Release Test'), ('user.email', 'test@example.invalid'),
                           ('commit.gpgsign', 'false')):
            self.git('config', key, value)
        self.run_work('init')
        self.group = self.run_work('create', 'group', 'Release')
        self.run_work('start', self.group)
        self.epics, self.tasks = [], []
        for name in ('alpha', 'beta'):
            epic = self.run_work('create', 'epic', name, '--parent', self.group)
            task = self.run_work('create', 'task', name + ' change', '--parent', epic)
            path, meta, body = work.records(self.root)[epic]
            work.write(path, dict(meta, branch='epic/' + name, base_branch='release/next'), body)
            self.epics.append(epic)
            self.tasks.append(task)
        path, meta, body = work.records(self.root)[self.group]
        work.write(path, dict(meta, branch='release/next', base_branch='main'), body)
        (self.root / 'app.txt').write_text('base\n')
        self.git('add', '.')
        self.git('commit', '-m', 'Release plan')
        self.base = self.git('rev-parse', 'HEAD')
        for branch in ('release/next', 'epic/alpha', 'epic/beta'):
            self.git('branch', branch)
        self.git('checkout', 'epic/alpha')
        self.addCleanup(self.clean_merge_worktrees)

    def prepare(self, index):
        self.git('checkout', ('epic/alpha', 'epic/beta')[index])
        self.approve(self.tasks[index])
        self.approve(self.epics[index])
        self.commit_queue(self.epics[index])

    def land(self, index):
        self.prepare(index)
        self.run_work('merge', self.epics[index])

    def finish_group(self):
        self.git('checkout', 'release/next')
        self.approve(self.group)
        self.commit_queue(self.group)

    def target(self, identity):
        return Path(json.loads(work.merge_journal_path(self.root, identity).read_text())['target_root'])

    def test_two_epics_then_final_group_and_base_only_restoration(self):
        self.prepare(0)
        source = self.git('rev-parse', 'HEAD')
        before = self.snapshot()
        self.assertIn('no cleanup', self.run_work('merge', self.epics[0], '--dry-run'))
        self.assertEqual(before, self.snapshot())
        self.run_work('merge', self.epics[0])
        self.assertEqual(self.git('rev-parse', 'HEAD'), source)
        self.assertEqual(self.git('show', '-s', '--format=%P', 'release/next'), f'{self.base} {source}')
        self.assertIn('already integrated', self.run_work('merge', self.epics[0], ok=False))
        self.git('checkout', 'release/next')
        items = work.records(self.root)
        self.assertEqual(items[self.group][1]['status'], 'wip')
        self.assertEqual(items[self.epics[0]][1]['status'], 'done')
        self.assertEqual(items[self.epics[1]][1]['status'], 'backlog')
        self.land(1)  # The stale beta checkout must not undo alpha's done move.
        self.finish_group()
        before = self.snapshot()
        self.assertIn('cleanup commit', self.run_work('merge', self.group, '--dry-run'))
        self.assertEqual(before, self.snapshot())
        self.run_work('merge', self.group)
        self.assertEqual(self.git('rev-list', '--count', f'{self.base}..main'), '2')
        ids = {self.group, *self.epics, *self.tasks}
        self.assertEqual(set(work.archive_history(self.root, 'main')), ids)
        self.assertIn('already merged and cleaned', self.run_work('merge', self.group, ok=False))
        clone = Path(self.temp.name) / 'final-only'
        self.git('clone', '--single-branch', '--branch', 'main', self.root.as_uri(), str(clone))
        self.assertNotIn('epic/alpha', self.git('branch', '-a', root=clone))
        self.run_work('check', root=clone)
        for identity in (self.group, self.epics[0], self.tasks[0]):
            self.assertIn('Acceptance record', self.run_work('show', identity, root=clone))
        self.run_work('reopen', self.tasks[0], root=clone)
        items = work.records(clone)
        self.assertEqual(items[self.group][1]['status'], 'wip')
        self.assertEqual(items[self.epics[0]][1]['status'], 'wip')
        self.assertEqual(items[self.tasks[0]][1]['status'], 'backlog')
        dependent = self.run_work('create', 'task', 'Archived prerequisite', '--parent', self.epics[0], root=clone)
        self.run_work('depend', dependent, self.tasks[1], root=clone)
        self.run_work('start', dependent, root=clone)
        self.run_work('check', root=clone)
        for identity in (self.group, self.epics[1]):
            fresh = Path(self.temp.name) / identity
            self.git('clone', '--single-branch', '--branch', 'main', self.root.as_uri(), str(fresh))
            self.run_work('reopen', identity, root=fresh)
            self.run_work('check', root=fresh)

    def test_followup_epic_preserves_sibling_and_does_not_replay_old_changes(self):
        self.land(0)
        self.land(1)
        self.git('checkout', 'epic/alpha')
        self.run_work('reopen', self.tasks[0])
        (self.root / 'followup.txt').write_text('new work\n')
        self.git('add', 'followup.txt')
        self.approve(self.tasks[0])
        self.approve(self.epics[0])
        self.commit_queue(self.epics[0])
        source = self.git('rev-parse', 'HEAD')
        self.run_work('merge', self.epics[0])
        self.assertEqual(self.git('merge-base', '--is-ancestor', source, 'release/next', ok=False).returncode, 0)
        self.assertEqual(self.git('show', 'release/next:followup.txt'), 'new work')
        self.git('checkout', 'release/next')
        self.assertTrue(all(work.records(self.root)[e][1]['status'] == 'done' for e in self.epics))
        self.run_work('check')

    def test_divergent_sibling_move_rejected_without_writes(self):
        self.land(0)
        self.prepare(1)
        self.run_work('start', self.epics[0])
        self.git('add', '.work')
        self.git('commit', '-m', 'Conflicting sibling progress')
        before = self.snapshot()
        self.assertIn('unrelated board state', self.run_work('merge', self.epics[1], ok=False))
        self.assertEqual(before, self.snapshot())

    def test_unintegrated_accepted_revision_blocks_final_release(self):
        self.land(0)
        self.land(1)
        self.git('checkout', 'epic/alpha')
        self.run_work('reopen', self.tasks[0])
        self.approve(self.tasks[0])
        self.approve(self.epics[0])
        self.commit_queue(self.epics[0])
        self.finish_group()
        self.assertIn('not integrated', self.run_work('merge', self.group, ok=False))
        self.assertFalse(work.merge_journal_path(self.root, self.group).exists())

    def test_deleted_epic_branches_still_allow_final_group_merge(self):
        self.land(0)
        self.land(1)
        self.finish_group()
        self.git('branch', '-D', 'epic/alpha', 'epic/beta')
        self.run_work('merge', self.group)
        self.assertIn(self.group, work.archive_history(self.root, 'main'))

    def test_intermediate_conflict_and_hook_failure_recover_once(self):
        self.prepare(0)
        target = Path(self.temp.name) / 'target'
        self.git('worktree', 'add', str(target), 'release/next')
        (target / 'app.txt').write_text('release\n')
        self.git('add', 'app.txt', root=target)
        self.git('commit', '-m', 'Release edit', root=target)
        (self.root / 'app.txt').write_text('epic\n')
        self.git('add', 'app.txt')
        self.git('commit', '-m', 'Epic edit')
        source = self.git('rev-parse', 'HEAD')
        self.assertIn('Merge stopped', self.run_work('merge', self.epics[0], ok=False))
        (target / 'app.txt').write_text('resolved\n')
        self.git('add', 'app.txt', root=target)
        hook = self.root / '.git/hooks/pre-commit'
        hook.write_text('#!/bin/sh\nexit 1\n')
        hook.chmod(0o755)
        self.assertIn('Merge commit failed', self.run_work('merge', self.epics[0], '--recover', ok=False))
        hook.unlink()
        self.run_work('merge', self.epics[0], '--recover')
        self.assertEqual(self.git('rev-parse', 'HEAD'), source)
        self.assertEqual(self.git('show', 'release/next:app.txt'), 'resolved')
        self.assertEqual(len(self.git('show', '-s', '--format=%P', 'release/next').split()), 2)

    def test_intermediate_interruption_after_commit_recovers_without_duplicate(self):
        self.prepare(0)
        original = work.commit_journal

        def stop(path, data):
            if data.get('stage') == 'merged':
                raise SystemExit('after integration commit')
            return original(path, data)

        with patch.object(work, 'commit_journal', side_effect=stop):
            with self.assertRaises(SystemExit):
                work.merge_command(self.root, work.records(self.root), work.Archives(self.root),
                                   SimpleNamespace(id=self.epics[0], dry_run=False, recover=False))
        head = self.git('rev-parse', 'release/next')
        self.run_work('merge', self.epics[0], '--recover')
        self.assertEqual(self.git('rev-parse', 'release/next'), head)

    def test_final_group_cleanup_hook_failure_and_interruption_resume(self):
        self.land(0)
        self.land(1)
        self.finish_group()
        path = work.records(self.root)[self.group][0].relative_to(self.root)
        hook = self.root / '.git/hooks/pre-commit'
        hook.write_text(f'#!/bin/sh\ntest -f "{path}"\n')
        hook.chmod(0o755)
        self.assertIn('git commit failed', self.run_work('merge', self.group, ok=False))
        self.assertEqual(self.git('rev-list', '--count', f'{self.base}..main'), '1')
        hook.unlink()
        original = work._git

        def stop(root, *args, **kwargs):
            if args[:2] == ('worktree', 'remove'):
                raise SystemExit('after group cleanup')
            return original(root, *args, **kwargs)

        with patch.object(work, '_git', side_effect=stop):
            with self.assertRaises(SystemExit):
                work.merge_command(self.root, work.records(self.root), work.Archives(self.root),
                                   SimpleNamespace(id=self.group, dry_run=False, recover=True))
        head = self.git('rev-parse', 'main')
        self.run_work('merge', self.group, '--recover')
        self.assertEqual(self.git('rev-parse', 'main'), head)
        self.assertEqual(self.git('rev-list', '--count', f'{self.base}..main'), '2')

    def test_final_squash_materializes_archived_epic_and_leaf(self):
        self.land(0)
        self.land(1)
        self.git('checkout', 'release/next')
        items = work.records(self.root)
        folder = items[self.epics[0]][0].parent
        # Model a previously manually archived epic tree on the release branch.
        self.git('rm', '-r', str(folder.relative_to(self.root)))
        self.git('commit', '-m', 'Earlier accepted archive')
        self.finish_group()
        self.run_work('merge', self.group)
        self.assertEqual(set(work.archive_history(self.root, 'main')), {self.group, *self.epics, *self.tasks})

    def test_intermediate_materializes_old_leaf_and_rejects_duplicate(self):
        self.prepare(0)
        path = work.records(self.root)[self.tasks[0]][0].relative_to(self.root).as_posix()
        self.git('rm', path)
        self.git('commit', '-m', 'Earlier leaf archive')
        self.run_work('merge', self.epics[0])
        self.assertIn('already integrated', self.run_work('merge', self.epics[0], ok=False))
        self.land(1)
        self.finish_group()
        self.run_work('merge', self.group)
        self.assertEqual(set(work.archive_history(self.root, 'main')), {self.group, *self.epics, *self.tasks})

    def test_final_conflict_hook_retry_and_unrelated_board_preservation(self):
        self.land(0)
        self.land(1)
        self.finish_group()
        (self.root / 'app.txt').write_text('release\n')
        self.git('add', 'app.txt')
        self.git('commit', '-m', 'Release implementation')
        source = self.git('rev-parse', 'HEAD')
        target = Path(self.temp.name) / 'main-target'
        self.git('worktree', 'add', str(target), 'main')
        unrelated = self.run_work('create', 'epic', 'Other feature', root=target)
        unrelated_path = work.records(target)[unrelated][0]
        unrelated_content = unrelated_path.read_bytes()
        (target / 'app.txt').write_text('main\n')
        self.git('add', '.', root=target)
        self.git('commit', '-m', 'Unrelated base progress', root=target)
        self.assertIn('Merge stopped', self.run_work('merge', self.group, ok=False))
        before = self.snapshot()
        target_before = {p.relative_to(target): p.read_bytes() for p in target.rglob('*') if p.is_file()}
        self.run_work('merge', self.group, '--recover', '--dry-run')
        self.assertEqual(before, self.snapshot())
        self.assertEqual(target_before, {p.relative_to(target): p.read_bytes() for p in target.rglob('*') if p.is_file()})
        (target / 'app.txt').write_text('resolved\n')
        self.git('add', 'app.txt', root=target)
        hook = self.root / '.git/hooks/pre-commit'
        hook.write_text('#!/bin/sh\nexit 1\n')
        hook.chmod(0o755)
        self.assertIn('Merge commit failed', self.run_work('merge', self.group, '--recover', ok=False))
        hook.unlink()
        self.run_work('merge', self.group, '--recover')
        self.assertEqual(self.git('rev-parse', 'HEAD'), source)
        self.assertEqual(unrelated_path.read_bytes(), unrelated_content)
        self.assertEqual(self.git('show', 'main:app.txt'), 'resolved')
        self.run_work('check', root=target)

    def test_dirty_intermediate_target_is_preserved(self):
        self.prepare(0)
        target = Path(self.temp.name) / 'release-target'
        self.git('worktree', 'add', str(target), 'release/next')
        (target / 'app.txt').write_text('user work\n')
        self.assertIn('clean checkout', self.run_work('merge', self.epics[0], ok=False))
        self.assertEqual((target / 'app.txt').read_text(), 'user work\n')
        self.assertFalse(work.merge_journal_path(self.root, self.epics[0]).exists())

    def test_wrong_group_target_and_missing_branch_are_rejected(self):
        self.prepare(0)
        path, meta, body = work.records(self.root)[self.epics[0]]
        work.write(path, dict(meta, base_branch='main'), body)
        self.git('add', '.work')
        self.git('commit', '-m', 'Wrong epic target')
        self.assertIn('parent-group branch', self.run_work('merge', self.epics[0], ok=False))
        work.write(path, dict(meta, branch=None), body)
        self.git('add', '.work')
        self.git('commit', '-m', 'Missing source metadata')
        self.assertIn('branch must match', self.run_work('merge', self.epics[0], ok=False))

    def test_unfinished_group_cannot_merge(self):
        self.land(0)
        self.git('checkout', 'release/next')
        self.assertIn('approved and committed', self.run_work('merge', self.group, ok=False))
        # Even manually claiming group completion cannot bypass descendant checks.
        path, meta, body = work.records(self.root)[self.group]
        work.persist(self.root, work.records(self.root), self.group, dict(meta, status='done'), body)
        self.git('add', '.work')
        self.git('commit', '-m', 'Invalid premature completion')
        self.assertIn('unfinished', self.run_work('merge', self.group, ok=False))

    def test_interruption_after_owned_target_removal_recovers(self):
        self.prepare(0)
        original = work._git

        def stop(root, *args, **kwargs):
            result = original(root, *args, **kwargs)
            if args[:2] == ('worktree', 'remove') and result.returncode == 0:
                raise SystemExit('after removing target')
            return result

        with patch.object(work, '_git', side_effect=stop):
            with self.assertRaises(SystemExit):
                work.merge_command(self.root, work.records(self.root), work.Archives(self.root),
                                   SimpleNamespace(id=self.epics[0], dry_run=False, recover=False))
        head = self.git('rev-parse', 'release/next')
        self.run_work('merge', self.epics[0], '--recover')
        self.assertEqual(self.git('rev-parse', 'release/next'), head)
        self.assertFalse(work.merge_journal_path(self.root, self.epics[0]).exists())


if __name__ == '__main__':
    unittest.main()
