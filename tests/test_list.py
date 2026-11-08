import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SOURCE = Path(__file__).resolve().parents[1]
SCRIPT = SOURCE / '.work/tools/work.py'


class ListTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.cli('init')

    def cli(self, *args, ok=True):
        result = subprocess.run([sys.executable, str(SCRIPT), '--root', str(self.root), *args],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode == 0, ok, result.stdout + result.stderr)
        return result.stdout if ok else result.stderr

    def git(self, *args):
        result = subprocess.run(['git', '-C', str(self.root), *args], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def init_git(self):
        self.git('init', '-b', 'feature/current')
        self.git('config', 'user.name', 'Test')
        self.git('config', 'user.email', 'test@example.invalid')
        self.git('config', 'commit.gpgsign', 'false')

    def create(self, kind, title='Example', parent=None, **metadata):
        args = ('--parent', parent) if parent else ()
        identity = self.cli('create', kind, title, *args).strip()
        if metadata:
            self.edit(identity, **metadata)
        return identity

    def path(self, identity):
        return next(p for p in (self.root / '.work').rglob('*.md')
                    if p.name.startswith(identity + '-') or p.parent.name.startswith(identity + '-'))

    def edit(self, identity, **metadata):
        path = self.path(identity)
        _, raw, body = path.read_text().split('---', 2)
        meta = json.loads(raw)
        meta.update(metadata)
        path.write_text('---\n' + json.dumps(meta, indent=2) + '\n---' + body)

    def ids(self, *args):
        return {line.split()[0] for line in self.cli('list', *args).splitlines()}

    def test_default_backlog_and_status_queues_respect_leaf_branches(self):
        self.init_git()
        epic = self.create('epic', branch='feature/current')
        task = self.create('task', parent=epic)
        other_branch = self.create('task', parent=epic, branch='feature/other')
        review = self.create('task', parent=epic)
        self.cli('start', review)
        self.cli('review', review)
        other_epic = self.create('epic', branch='feature/later')
        other_task = self.create('task', parent=other_epic)
        self.assertEqual(self.ids(), {task})
        self.assertEqual(self.ids('--status', 'review'), {review})
        self.assertEqual(self.ids('--epic', epic), {task, other_branch})
        self.assertEqual(self.ids('--all'), {epic, task, other_branch, review, other_epic, other_task})
        self.assertEqual(self.ids('--all', '--status', 'review'), {review})
        self.cli('start', epic)
        self.assertEqual(self.ids('--status', 'wip'), {epic})

    def test_explicit_scope_in_non_git_and_empty_result(self):
        epic = self.create('epic')
        self.assertIn('--epic ID or --all', self.cli('list', ok=False))
        self.assertEqual(self.ids('--epic', epic), set())
        self.assertEqual(self.ids('--epic', epic, '--status', 'backlog'), {epic})
        self.assertEqual(self.ids('--all'), {epic})
        task = self.create('task', parent=epic)
        self.assertIn('live epic ID', self.cli('list', '--epic', task, ok=False))
        self.assertIn('Unknown ticket', self.cli('list', '--epic', 'E-00000000', ok=False))

    def test_unmapped_shared_and_detached_branches_require_scope(self):
        self.init_git()
        epic = self.create('epic', branch='feature/other')
        self.assertIn('matches: none', self.cli('list', ok=False))
        self.edit(epic, branch='feature/current')
        second = self.create('epic', branch='feature/current')
        error = self.cli('list', ok=False)
        self.assertIn(epic, error)
        self.assertIn(second, error)
        self.assertEqual(self.ids('--epic', epic), set())
        self.git('add', '.')
        self.git('commit', '-m', 'Board')
        self.git('checkout', '--detach')
        self.assertIn('Detached HEAD', self.cli('list', ok=False))
        self.assertEqual(self.ids('--all'), {epic, second})

    def test_child_branch_discovers_grouped_epic_without_group_inheritance(self):
        self.init_git()
        group = self.create('group', branch='feature/current')
        epic = self.create('epic', parent=group, branch='feature/epic')
        inherited = self.create('task', parent=epic)
        child = self.create('story', parent=epic, branch='feature/current')
        self.assertEqual(self.ids(), {child})
        self.edit(child, branch=None)
        self.assertIn('matches: none', self.cli('list', ok=False))
        self.assertEqual(self.ids('--epic', epic), {inherited, child})

    def test_ready_checks_selected_and_ancestor_dependencies_and_status(self):
        group = self.create('group')
        epic = self.create('epic', parent=group)
        dependency = self.create('task', parent=epic)
        task = self.create('task', parent=epic, depends_on=[dependency])
        self.assertEqual(self.ids('--all', '--ready'), {dependency})
        self.cli('start', dependency)
        self.cli('review', dependency)
        self.assertEqual(self.ids('--epic', epic, '--ready'), set())
        unblocked = self.create('task', 'Unblocked', parent=epic)
        self.assertEqual(self.ids('--all', '--ready'), {unblocked})
        self.cli('start', group)
        self.cli('review', group)
        self.assertEqual(self.ids('--all', '--ready'), set())
        self.cli('start', group)
        self.assertEqual(self.ids('--all', '--ready'), {unblocked})
        self.cli('start', epic)
        self.cli('review', epic)
        self.assertEqual(self.ids('--all', '--ready'), set())
        self.cli('start', epic)
        self.cli('reopen', dependency)
        self.edit(epic, depends_on=[self.create('epic', 'Gate')])
        self.assertEqual(self.ids('--all', '--ready'), set())
        self.assertEqual(self.ids('--epic', epic), {dependency, task, unblocked})

    def test_ready_accepts_implemented_done_and_archived_prerequisites(self):
        self.init_git()
        epic = self.create('epic', branch='feature/current')
        prerequisite_epic = self.create('epic', 'Prerequisites', branch='feature/other')
        dependency = self.create('task', parent=prerequisite_epic)
        task = self.create('task', parent=epic, depends_on=[dependency])
        self.edit(epic, depends_on=[dependency])
        path = self.path(dependency)
        path.write_text(path.read_text().replace('- [ ]', '- [x]'))
        self.cli('assign', dependency, '--implementer', 'agent', '--reviewer', 'human')
        self.cli('start', dependency)
        self.cli('review', dependency)
        self.cli('done', dependency, '--by', 'human', '--evidence', 'Test acceptance')
        self.assertEqual(self.ids('--ready'), {task})
        path = self.path(dependency)
        self.edit(dependency, status='done')
        destination = path.parent.parent / 'done' / path.name
        path.rename(destination)
        self.assertEqual(self.ids('--ready'), {task})
        self.git('add', '.')
        self.git('commit', '-m', 'Accepted prerequisite')
        destination.unlink()
        self.git('add', '.')
        self.git('commit', '-m', 'Archive prerequisite')
        self.assertEqual(self.ids('--ready'), {task})

    def test_filter_errors_and_no_persistent_writes(self):
        self.init_git()
        epic = self.create('epic', branch='feature/current')
        task = self.create('task', parent=epic)
        self.git('add', '.')
        self.git('commit', '-m', 'Board')
        before = {str(p.relative_to(self.root)): p.read_bytes()
                  for p in self.root.rglob('*') if p.is_file()}
        status = self.git('status', '--porcelain')
        for args in ((), ('--ready',), ('--status', 'review'), ('--epic', epic), ('--all',)):
            self.ids(*args)
        self.assertIn('--ready requires backlog', self.cli('list', '--ready', '--status', 'review', ok=False))
        self.cli('list', '--all', '--epic', epic, ok=False)
        self.assertEqual(self.ids('--ready', '--status', 'backlog'), {task})
        self.assertEqual(status, self.git('status', '--porcelain'))
        self.assertEqual(before, {str(p.relative_to(self.root)): p.read_bytes()
                                  for p in self.root.rglob('*') if p.is_file()})

    def test_help_and_canonical_skill_discovery_guidance(self):
        help_text = self.cli('list', '--help')
        for option in ('--epic', '--all', '--status', '--ready'):
            self.assertIn(option, help_text)
        execute = (SOURCE / 'skills/work-execute/SKILL.md').read_text()
        for command in ('list --ready', 'list --status review', 'list --status wip', 'list --all'):
            self.assertIn(command, execute)
        prepare = (SOURCE / 'skills/work-prepare/SKILL.md').read_text()
        self.assertIn('list --all', prepare)
