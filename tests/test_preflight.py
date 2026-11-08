import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_work import SCRIPT, work


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='work-preflight-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'project'
        self.root.mkdir()
        self.run_work('init')

    def run_work(self, *args, ok=True, script=SCRIPT, root=None):
        result = subprocess.run([sys.executable, str(script), '--root', str(root or self.root), *args],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0 if ok else 1, result.stdout + result.stderr)
        return result.stdout + result.stderr

    def create(self, kind, parent=None):
        return self.run_work('create', kind, kind, *(['--parent', parent] if parent else [])).strip()

    def edit(self, identity, **changes):
        path, meta, body = work.records(self.root)[identity]
        work.write(path, dict(meta, **changes), body)

    def git(self, *args):
        result = subprocess.run(['git', '-C', str(self.root), *args], capture_output=True, text=True,
                                env=dict(os.environ, GIT_CONFIG_NOSYSTEM='1'))
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def initialize_git(self):
        self.git('init', '-b', 'main')
        self.git('config', 'user.name', 'Preflight Test')
        self.git('config', 'user.email', 'preflight@example.test')
        self.git('config', 'commit.gpgsign', 'false')
        self.git('add', '.')
        self.git('commit', '-m', 'Initial board')
        self.git('switch', '-c', 'feature')

    def setup_epic(self):
        epic = self.create('epic')
        task = self.create('task', epic)
        self.edit(epic, branch='feature', base_branch='main')
        self.initialize_git()
        return epic, task

    def snapshot(self):
        return {str(p.relative_to(self.root)): ('dir' if p.is_dir() else p.read_bytes())
                for p in self.root.rglob('*') if not p.is_symlink()}

    def observe(self, identity, *args, ok=True):
        before = self.snapshot()
        output = self.run_work('preflight', identity, *args, ok=ok)
        self.assertEqual(self.snapshot(), before)
        return output

    def test_non_git_hierarchy_start_order_and_roles_without_writes(self):
        group = self.create('group')
        epic = self.create('epic', group)
        task = self.create('task', epic)
        output = self.observe(task)
        self.assertIn('not a Git repository', output)
        self.assertIn('Start order (not performed): ' + ' -> '.join((group, epic, task)), output)
        self.assertIn('Establish unset implementer/reviewer', output)
        self.assertNotIn('BLOCKED', output)
        self.assertIn('Target: branch=unset', output)

    def test_epic_fallback_dirty_decision_and_worktree_context(self):
        epic, task = self.setup_epic()
        (self.root / 'unrelated.txt').write_text('User work')
        output = self.observe(task)
        self.assertIn('branch: feature', output)
        self.assertIn(f'Target: branch=feature; base=main; from={epic}', output)
        self.assertIn('unrelated.txt', output)
        self.assertIn('Confirm dirty-work ownership', output)
        self.assertIn(f'Worktree: {self.root} [feature]', output)
        self.assertEqual(work.records(self.root)[task][1]['status'], 'backlog')

    def test_explicit_task_and_story_override_with_base_fallback(self):
        epic, task = self.setup_epic()
        story = self.create('story', epic)
        self.git('branch', 'leaf')
        for identity in (task, story):
            with self.subTest(kind=identity):
                self.edit(identity, branch='leaf')
                output = self.observe(identity, ok=False)
                self.assertIn('actual \'feature\', expected \'leaf\'', output)
                self.assertIn(f'branch=leaf; base=main; from={identity}', output)
        self.git('switch', 'leaf')
        self.edit(task, base_branch='feature')
        self.assertIn('branch=leaf; base=feature', self.observe(task))

    def test_group_context_and_missing_epic_does_not_inherit_group_branch(self):
        group = self.create('group')
        epic = self.create('epic', group)
        task = self.create('task', epic)
        self.edit(group, branch='feature', base_branch='main')
        self.initialize_git()
        self.assertIn(f'from={group}', self.observe(group))
        output = self.observe(task, ok=False)
        self.assertIn('Missing branch;', output)
        self.assertIn('Missing base_branch;', output)

    def test_detached_missing_targets_and_invalid_metadata(self):
        epic, task = self.setup_epic()
        self.git('checkout', '--detach')
        self.assertIn('Detached HEAD', self.observe(task, ok=False))
        self.git('switch', 'feature')
        for changes, expected in ((dict(branch=None), 'Missing branch;'),
                                  (dict(branch='absent'), "Missing local branch 'absent'"),
                                  (dict(branch='bad name'), 'Invalid branch:'),
                                  (dict(branch=['feature']), 'must be a nonempty string'),
                                  (dict(branch='feature', base_branch='absent'), 'Missing local base_branch')):
            with self.subTest(changes=changes):
                self.edit(epic, branch='feature', base_branch='main')
                self.edit(epic, **changes)
                self.assertIn(expected, self.observe(task, ok=False))

    def test_lifecycle_and_dependency_gates_and_commit_mode(self):
        epic, task = self.setup_epic()
        dependency = self.create('task', epic)
        self.edit(task, depends_on=[dependency])
        self.assertIn(f'unfinished dependency {dependency}', self.observe(task, ok=False))
        self.edit(task, depends_on=[])
        self.run_work('start', epic)
        self.run_work('review', epic)
        self.assertIn(f'Ancestor {epic} is review', self.observe(task, ok=False))
        self.assertIn('Commit context only', self.observe(task, '--for', 'commit'))
        self.run_work('start', epic)
        path, meta, body = work.records(self.root)[task]
        work.write(path, meta, body.replace('- [ ]', '- [x]'))
        self.run_work('assign', task, '--implementer', 'agent', '--reviewer', 'human')
        self.run_work('start', task)
        self.run_work('review', task)
        self.run_work('done', task, '--by', 'human', '--evidence', 'Reviewed')
        self.assertIn('reopen before implementation', self.observe(task, ok=False))
        self.assertIn('Commit context only', self.observe(task, '--for', 'commit'))
        self.assertEqual(work.records(self.root)[task][1]['status'], 'implemented')

    def test_invalid_board_unknown_ticket_and_pending_transactions(self):
        epic, task = self.setup_epic()
        self.assertIn('Unknown ticket:', self.observe('T-00000000', ok=False))
        path, meta, body = work.records(self.root)[task]
        self.edit(task, status='wip')  # Deliberately leave it in the backlog folder.
        self.assertIn('parent/directory/status disagree', self.observe(task, ok=False))
        work.write(path, meta, body)
        for relative in ('.work/.lock', '.work/.commit-journal.json'):
            with self.subTest(relative=relative):
                pending = self.root / relative
                if pending.name == '.lock':
                    pending.mkdir()
                else:
                    pending.write_text('{}')
                self.assertIn(f'BLOCKED: {relative} needs attention', self.observe(task, ok=False))
                if pending.is_dir():
                    pending.rmdir()
                else:
                    pending.unlink()

    def test_multiple_worktrees_and_linked_checkout_read_only(self):
        epic, task = self.setup_epic()
        target = Path(self.tmp.name) / 'linked'
        self.git('worktree', 'add', str(target), 'main')
        output = self.observe(task)
        self.assertIn(f'Worktree: {target} [main]', output)
        linked_before = {str(p.relative_to(target)): p.read_bytes() for p in target.rglob('*') if p.is_file()}
        self.run_work('preflight', task, root=target, ok=False)
        self.assertEqual(linked_before, {str(p.relative_to(target)): p.read_bytes()
                                        for p in target.rglob('*') if p.is_file()})

    def test_installed_launcher_and_skill_use_shared_command(self):
        target = Path(self.tmp.name) / 'installed'
        target.mkdir()
        self.run_work('install', str(target))
        installed = target / '.workkit/.work/tools/work.py'
        identity = self.run_work('create', 'epic', 'Installed', script=installed, root=target).strip()
        output = subprocess.run([str(target / '.workkit/work'), '--root', str(target), 'preflight', identity],
                                capture_output=True, text=True)
        self.assertEqual(output.returncode, 0, output.stderr)
        self.assertIn('not a Git repository', output.stdout)
        for name in ('work-execute', 'work-commit', 'work-prepare'):
            text = (target / '.workkit/skills' / name / 'SKILL.md').read_text()
            self.assertIn('./.workkit/work preflight ID', text)


if __name__ == '__main__':
    unittest.main()
