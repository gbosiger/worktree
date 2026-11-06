import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1]
SCRIPT = SOURCE / '.work' / 'tools' / 'work.py'
spec = importlib.util.spec_from_file_location('work', SCRIPT)
work = importlib.util.module_from_spec(spec)
spec.loader.exec_module(work)


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.run_work('init')

    def run_work(self, *args, ok=True, script=SCRIPT):
        result = subprocess.run([sys.executable, str(script), '--root', str(self.root), *args],
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

    def finish(self, identity):
        self.ready(identity)
        self.run_work('done', identity, '--by', 'human', '--evidence', 'Reviewed acceptance evidence')

    def test_full_lifecycle_moves_container_preserves_body_and_ids(self):
        epic = self.create('epic', 'Search')
        story = self.create('story', 'Find titles', epic)
        self.finish(story)
        original = work.records(self.root)[story][2]
        self.finish(epic)
        items = work.records(self.root)
        self.assertIn('/done/', str(items[story][0]))
        self.assertEqual(original, items[story][2])
        self.run_work('reopen', story)
        items = work.records(self.root)
        self.assertEqual(items[epic][1]['status'], 'wip')
        self.assertEqual(items[story][1]['status'], 'backlog')
        self.assertIn('/wip/', str(items[story][0]))
        self.run_work('check')

    def test_group_moves_tree_without_starting_children(self):
        group = self.create('group')
        epic = self.create('epic', parent=group)
        story = self.create('story', parent=epic)
        before = work.records(self.root)[story][0]
        self.run_work('start', group, '--dry-run')
        self.assertTrue(before.exists())
        self.run_work('start', group)
        items = work.records(self.root)
        self.assertFalse(before.exists())
        self.assertEqual(items[epic][1]['status'], 'backlog')
        self.assertEqual(items[story][1]['status'], 'backlog')
        self.run_work('check')

    def test_child_files_move_through_nested_status_folders(self):
        epic = self.create('epic')
        epic_dir = work.records(self.root)[epic][0].parent
        for kind in ('story', 'task'):
            with self.subTest(kind=kind):
                identity = self.create(kind, parent=epic)
                path, meta, body = work.records(self.root)[identity]
                filename = path.name
                self.assertEqual(path.parent, epic_dir / 'backlog')
                work.write(path, dict(meta, custom='preserved'), body.replace('- [ ]', '- [x]'))
                self.run_work('assign', identity, '--implementer', 'agent', '--reviewer', 'human')
                for command, state in (('start', 'wip'), ('review', 'review'),
                                       ('start', 'wip'), ('review', 'review'),
                                       ('done', 'done'), ('reopen', 'backlog')):
                    extra = ('--by', 'human', '--evidence', 'Reviewed') if command == 'done' else ()
                    before = {p: p.read_bytes() for p in (self.root / '.work').rglob('*.md')}
                    self.run_work(command, identity, *extra, '--dry-run')
                    self.assertEqual(before, {p: p.read_bytes() for p in (self.root / '.work').rglob('*.md')})
                    self.run_work(command, identity, *extra)
                    new_path, new_meta, new_body = work.records(self.root)[identity]
                    self.assertFalse(path.exists())
                    self.assertEqual(new_path, epic_dir / state / filename)
                    self.assertEqual(new_meta['status'], state)
                    self.assertEqual(new_meta['custom'], 'preserved')
                    self.assertIn('# Example', new_body)
                    self.assertIn(str(new_path.relative_to(self.root)), self.run_work('show', identity))
                    self.assertIn(identity, self.run_work('list', '--status', state))
                    self.assertEqual(work.records(self.root)[epic][1]['status'], 'backlog')
                    self.run_work('check')
                    path = new_path
                self.assertIn('## Acceptance record', new_body)

    def test_grouped_epic_moves_with_children_and_reopens_from_done(self):
        group = self.create('group')
        epic = self.create('epic', parent=group)
        story = self.create('story', parent=epic)
        group_dir = work.records(self.root)[group][0].parent
        epic_dir = work.records(self.root)[epic][0].parent
        self.assertEqual(epic_dir.parent, group_dir / 'backlog')
        self.run_work('start', epic)
        items = work.records(self.root)
        self.assertEqual(items[epic][0].parent.parent, group_dir / 'wip')
        self.assertEqual(items[story][0].parent, items[epic][0].parent / 'backlog')
        self.finish(story)
        path, meta, body = work.records(self.root)[epic]
        work.write(path, meta, body.replace('- [ ]', '- [x]'))
        self.run_work('assign', epic, '--implementer', 'agent', '--reviewer', 'human')
        self.run_work('review', epic)
        self.run_work('done', epic, '--by', 'human', '--evidence', 'Reviewed')
        self.finish(group)
        self.run_work('reopen', story)
        items = work.records(self.root)
        self.assertEqual(items[group][0].parent.parent, self.root / '.work' / 'wip')
        self.assertEqual(items[epic][0].parent.parent, items[group][0].parent / 'wip')
        self.assertEqual(items[story][0].parent, items[epic][0].parent / 'backlog')
        self.run_work('check')

    def test_check_rejects_legacy_child_layout_and_status_mismatch(self):
        epic = self.create('epic')
        story = self.create('story', parent=epic)
        path, meta, body = work.records(self.root)[story]
        legacy = path.parent.parent / path.name
        path.rename(legacy)
        error = self.run_work('check', ok=False)
        self.assertIn('disagree', error)
        self.assertIn('migration', error)
        legacy.rename(path)
        work.write(path, dict(meta, status='wip'), body)
        self.assertIn('disagree', self.run_work('check', ok=False))
        destination = path.parent.parent / 'wip' / path.name
        path.rename(destination)
        self.run_work('check')

    def test_nested_move_collision_and_failure_preserve_original(self):
        group = self.create('group')
        epic = self.create('epic', parent=group)
        story = self.create('story', parent=epic)
        for identity in (epic, story):
            with self.subTest(identity=identity):
                items = work.records(self.root)
                path, meta, body = items[identity]
                original = path.read_bytes()
                base = items[meta['parent']][0].parent
                source = path.parent if meta['kind'] == 'epic' else path
                destination = base / 'wip' / source.name
                with patch.object(Path, 'rename', side_effect=OSError('Injected move failure')):
                    with self.assertRaisesRegex(OSError, 'Injected'):
                        work.persist(self.root, items, identity, dict(meta, status='wip'), body)
                self.assertEqual(path.read_bytes(), original)
                self.assertFalse(destination.exists())
                destination.write_text('Existing destination')
                with self.assertRaisesRegex(ValueError, 'Destination exists'):
                    work.persist(self.root, items, identity, dict(meta, status='wip'), body)
                self.assertEqual(destination.read_text(), 'Existing destination')
                self.assertEqual(path.read_bytes(), original)
                destination.unlink()
                self.run_work('check')

    def test_missing_child_status_folders_are_created_when_needed(self):
        epic = self.create('epic')
        epic_dir = work.records(self.root)[epic][0].parent
        for state in work.STATES:
            (epic_dir / state / '.gitkeep').unlink()
            (epic_dir / state).rmdir()
        story = self.create('story', parent=epic)
        self.assertEqual(work.records(self.root)[story][0].parent, epic_dir / 'backlog')
        self.run_work('start', story, '--dry-run')
        self.assertFalse((epic_dir / 'wip').exists())
        self.run_work('start', story)
        self.assertEqual(work.records(self.root)[story][0].parent, epic_dir / 'wip')
        self.run_work('check')

    def test_repository_skills_link_to_canonical_sources(self):
        for skill in (SOURCE / 'skills').iterdir():
            with self.subTest(skill=skill.name):
                link = SOURCE / '.agents' / 'skills' / skill.name
                self.assertTrue(link.is_symlink())
                self.assertFalse(link.readlink().is_absolute())
                self.assertEqual(link.resolve(), skill.resolve())
                self.assertTrue((link / 'SKILL.md').samefile(skill / 'SKILL.md'))
        self.assertEqual(len(list((SOURCE / '.agents' / 'skills').glob('*/SKILL.md'))), 3)

    def test_opencode_commands_have_canonical_links_and_safe_templates(self):
        expected = {'work', 'work-group', 'work-epic', 'work-story', 'work-task',
                    'work-list', 'work-show', 'work-check', 'work-start',
                    'work-review', 'work-done', 'work-reopen', 'work-assign', 'work-depend'}
        commands = list((SOURCE / 'commands').glob('*.md'))
        self.assertEqual({p.stem for p in commands}, expected)
        for command in commands:
            with self.subTest(command=command.name):
                link = SOURCE / '.opencode' / 'commands' / command.name
                self.assertTrue(link.is_symlink())
                self.assertFalse(link.readlink().is_absolute())
                self.assertTrue(link.samefile(command))
                text = command.read_text()
                metadata, body = text.removeprefix('---\n').split('---\n', 1)
                self.assertIn('description:', metadata)
                self.assertNotIn('agent:', metadata)
                self.assertNotIn('model:', metadata)
                self.assertIn('$ARGUMENTS', body)
                self.assertNotIn('!`', text)
        self.assertIn('work-prepare', (SOURCE / 'commands' / 'work-task.md').read_text())
        self.assertIn('work-execute', (SOURCE / 'commands' / 'work-start.md').read_text())
        self.assertIn('never invent', (SOURCE / 'commands' / 'work-done.md').read_text())

    def test_executable_launcher_and_command_setup(self):
        unrelated = self.root / 'no-board'
        unrelated.mkdir()
        bin_dir = self.root / 'command bin with spaces'
        result = subprocess.run([str(SOURCE / 'work'), 'setup', '--bin-dir', str(bin_dir)],
                                cwd=unrelated, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        command = bin_dir / 'work'
        self.assertTrue(command.is_symlink())
        self.assertEqual(command.resolve(), SOURCE / 'work')
        self.assertIn('PATH', result.stdout)
        # Setup needs no board, can be repeated, and the symlink resolves the
        # runtime relative to its checkout, not relative to the command directory.
        result = subprocess.run([str(command), 'setup', '--bin-dir', str(bin_dir)],
                                cwd=unrelated, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = subprocess.run([str(command), '--version'], cwd=unrelated,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), work.VERSION)
        result = subprocess.run([str(command), '--root', str(self.root), 'check'],
                                cwd=unrelated, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((unrelated / '.work').exists())

    def test_runtime_layout_and_tools_do_not_become_tickets(self):
        self.assertTrue(SCRIPT.is_file())
        self.assertFalse((SOURCE / 'work.py').exists())
        self.assertEqual(work.TOOLKIT, SOURCE)
        tools = self.root / '.work' / 'tools'
        tools.mkdir()
        (tools / 'README.md').write_text('Runtime documentation, not a ticket.')
        (tools / 'work.py').write_text('# Runtime, not a ticket.\n')
        self.assertEqual(work.records(self.root), {})
        self.run_work('check')
        epic = self.create('epic', 'Tooling coexists with tickets')
        self.assertEqual(set(work.records(self.root)), {epic})

    def test_setup_refuses_existing_commands_and_dangling_links(self):
        bin_dir = self.root / 'bin'
        bin_dir.mkdir()
        command = bin_dir / 'work'
        command.write_text('existing command')
        self.assertIn('already exists', self.run_work('setup', '--bin-dir', str(bin_dir), ok=False))
        self.assertEqual(command.read_text(), 'existing command')
        command.unlink()
        other = self.root / 'missing-launcher'
        command.symlink_to(other)
        self.assertIn('already exists', self.run_work('setup', '--bin-dir', str(bin_dir), ok=False))
        self.assertEqual(command.readlink(), other)

    def test_focused_references_are_selected_by_skills(self):
        required = {'work-prepare': ('AUTHORING', 'FORMAT'),
                    'work-execute': ('LIFECYCLE',), 'work-commit': ('GIT',)}
        for name, references in required.items():
            text = (SOURCE / 'skills' / name / 'SKILL.md').read_text()
            for reference in references:
                self.assertIn(f'docs/{reference}.md', text)
                self.assertTrue((SOURCE / 'docs' / f'{reference}.md').is_file())
            self.assertNotIn('Read `.workkit/CONVENTION.md`', text)
            self.assertIn('Do not preload', text)

    def test_completion_requires_criteria_evidence_and_reviewer(self):
        epic = self.create('epic')
        self.run_work('done', epic, ok=False)
        self.run_work('start', epic)
        self.run_work('review', epic)
        self.run_work('done', epic, ok=False)
        self.run_work('assign', epic, '--implementer', 'agent', '--reviewer', 'human')
        error = self.run_work('done', epic, '--by', 'agent', '--evidence', 'ok', ok=False)
        self.assertIn('recorded reviewer', error)
        error = self.run_work('done', epic, '--by', 'human', '--evidence', 'ok', ok=False)
        self.assertIn('Unchecked', error)

    def test_parent_cannot_complete_with_open_children(self):
        epic = self.create('epic')
        self.create('task', parent=epic)
        self.ready(epic)
        error = self.run_work('done', epic, '--by', 'human', '--evidence', 'ok', ok=False)
        self.assertIn('Unfinished children', error)

    def test_dependencies_cycles_and_reopen_order(self):
        first = self.create('epic', 'First')
        second = self.create('epic', 'Second')
        self.run_work('depend', second, first)
        self.run_work('start', second, ok=False)
        self.assertIn('cycle', self.run_work('depend', first, second, ok=False))
        self.assertEqual(work.records(self.root)[first][1]['depends_on'], [])
        self.finish(first)
        self.finish(second)
        self.assertIn('dependents', self.run_work('reopen', first, ok=False))
        self.run_work('reopen', second)
        self.run_work('reopen', first)
        self.run_work('check')

    def test_invalid_parents_duplicates_and_status_mismatch(self):
        epic = self.create('epic')
        self.run_work('create', 'story', 'No parent', ok=False)
        self.run_work('create', 'epic', 'Nested epic', '--parent', epic, ok=False)
        path, meta, body = work.records(self.root)[epic]
        work.write(path, dict(meta, status='done'), body)
        self.assertIn('disagree', self.run_work('check', ok=False))
        work.write(path, meta, body)
        duplicate = self.root / '.work' / 'backlog' / f'{epic}-duplicate'
        duplicate.mkdir()
        work.write(duplicate / 'README.md', meta, body)
        self.assertIn('Duplicate', self.run_work('check', ok=False))

    def test_reopen_checks_dependents_of_all_completed_ancestors(self):
        group = self.create('group')
        epic = self.create('epic', parent=group)
        story = self.create('story', parent=epic)
        self.finish(story)
        self.finish(epic)
        self.finish(group)
        dependent = self.create('epic', 'Dependent')
        for prerequisite in (epic, group):
            with self.subTest(prerequisite=prerequisite):
                self.run_work('depend', dependent, prerequisite)
                self.finish(dependent)
                before = {p: p.read_bytes() for p in (self.root / '.work').rglob('*.md')}
                for extra in (('--dry-run',), ()):
                    error = self.run_work('reopen', story, *extra, ok=False)
                    self.assertIn(dependent, error)
                    self.assertIn('dependents', error)
                    self.assertEqual(before, {p: p.read_bytes() for p in (self.root / '.work').rglob('*.md')})
                    self.run_work('check')
                self.run_work('reopen', dependent)
                self.run_work('depend', dependent, prerequisite, '--remove')
        self.run_work('reopen', story, '--dry-run')
        self.run_work('reopen', story)
        items = work.records(self.root)
        self.assertEqual(items[group][1]['status'], 'wip')
        self.assertEqual(items[epic][1]['status'], 'wip')
        self.assertEqual(items[story][1]['status'], 'backlog')
        self.run_work('check')

    def test_completion_cycles_include_parent_child_prerequisites(self):
        group = self.create('group')
        epic = self.create('epic', parent=group)
        story = self.create('story', parent=epic)
        other = self.create('epic', 'Other')
        self.run_work('depend', other, group)
        for prerequisite in (epic, group, other):
            with self.subTest(prerequisite=prerequisite):
                error = self.run_work('depend', story, prerequisite, ok=False)
                self.assertIn('cycle', error)
                self.assertEqual(work.records(self.root)[story][1]['depends_on'], [])
                self.run_work('check')
        # Direct Markdown edits must be validated too.
        path, meta, body = work.records(self.root)[story]
        work.write(path, dict(meta, depends_on=[epic]), body)
        self.assertIn('cycle', self.run_work('check', ok=False))

    def test_parent_can_explicitly_depend_on_child(self):
        epic = self.create('epic')
        story = self.create('story', parent=epic)
        self.run_work('depend', epic, story)
        self.finish(story)
        self.finish(epic)
        # Both completed tickets reopen together, so neither blocks the other.
        self.run_work('reopen', story)
        self.run_work('check')

    def test_completion_recognizes_markdown_checkbox_markers(self):
        epic = self.create('epic')
        self.ready(epic)
        path, meta, _ = work.records(self.root)[epic]
        for marker in ('-', '*', '+', '1.', '2)', '    *', '\t+', '10.'):
            with self.subTest(marker=marker):
                body = f'## Acceptance criteria\n\n{marker} [ ]\n'
                work.write(path, meta, body)
                error = self.run_work('done', epic, '--by', 'human', '--evidence', 'Reviewed', ok=False)
                self.assertIn('Unchecked', error)
                self.assertEqual(work.read(path), (meta, body))
        work.write(path, meta, '## Acceptance criteria\n\n* [x] First\n+ [X] Second\n1. [x] Third\n')
        self.run_work('done', epic, '--by', 'human', '--evidence', 'Reviewed')
        self.run_work('check')

    def test_install_and_use_from_unrelated_cwd_preserves_instructions(self):
        target = self.root / 'module'
        target.mkdir()
        (target / 'AGENTS.md').write_text('# Existing\nDo useful work.\n')
        self.run_work('install', str(target))
        self.assertTrue((target / 'AGENTS.md').read_text().startswith('# Existing\nDo useful work.\n'))
        self.assertEqual(len(list((target / '.agents' / 'skills').glob('*/SKILL.md'))), 3)
        self.assertTrue((target / '.workkit' / 'LICENSE').exists())
        self.assertEqual((target / '.workkit' / 'VERSION').read_text().strip(), work.VERSION)
        for reference in ('FORMAT', 'AUTHORING', 'LIFECYCLE', 'GIT', 'INSTALLATION', 'MIGRATIONS'):
            self.assertTrue((target / '.workkit' / 'docs' / f'{reference}.md').is_file())
        self.assertTrue((target / '.workkit' / 'CHANGELOG.md').is_file())
        installed = target / '.workkit' / '.work' / 'tools' / 'work.py'
        self.assertTrue(installed.is_file())
        self.assertFalse((target / '.workkit' / 'work.py').exists())
        result = subprocess.run([sys.executable, str(installed), '--root', str(target), 'create', 'epic', 'Installed'],
                                capture_output=True, text=True, cwd=self.root)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(result.stdout.strip(), work.records(target))
        epic = result.stdout.strip()
        result = subprocess.run([sys.executable, str(installed), '--root', str(target),
                                 'create', 'task', 'Installed child', '--parent', epic],
                                capture_output=True, text=True, cwd=self.root)
        self.assertEqual(result.returncode, 0, result.stderr)
        items = work.records(target)
        self.assertEqual(items[result.stdout.strip()][0].parent, items[epic][0].parent / 'backlog')
        result = subprocess.run([str(target / '.workkit' / 'work'), '--root', str(target), 'check'],
                                cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.run_work('install', str(target), ok=False)

    def test_install_conflict_changes_nothing(self):
        target = self.root / 'module'
        conflict = target / '.agents' / 'skills' / 'work-prepare'
        conflict.mkdir(parents=True)
        (conflict / 'SKILL.md').write_text('custom')
        self.run_work('install', str(target), ok=False)
        self.assertFalse((target / '.workkit').exists())
        self.assertFalse((target / '.work').exists())
        self.assertEqual((conflict / 'SKILL.md').read_text(), 'custom')

    def test_installed_skill_links_are_local_live_and_relocatable(self):
        target = self.root / 'module'
        target.mkdir()
        self.run_work('install', str(target))
        for skill in (target / '.workkit' / 'skills').iterdir():
            link = target / '.agents' / 'skills' / skill.name
            self.assertTrue(link.is_symlink())
            self.assertFalse(link.readlink().is_absolute())
            self.assertEqual(link.resolve(), skill.resolve())
            self.assertTrue((link / 'SKILL.md').samefile(skill / 'SKILL.md'))
            source_text = (SOURCE / 'skills' / skill.name / 'SKILL.md').read_text()
            changed = source_text + '\nLocal project customization.\n'
            (skill / 'SKILL.md').write_text(changed)
            self.assertEqual((link / 'SKILL.md').read_text(), changed)
            self.assertEqual((SOURCE / 'skills' / skill.name / 'SKILL.md').read_text(), source_text)
        relocated = self.root / 'relocated module'
        shutil.copytree(target, relocated, symlinks=True)
        for skill in (relocated / '.workkit' / 'skills').iterdir():
            link = relocated / '.agents' / 'skills' / skill.name
            self.assertEqual(link.resolve(), skill.resolve())
            self.assertTrue((link / 'SKILL.md').samefile(skill / 'SKILL.md'))
        self.assertEqual(len(list((relocated / '.agents' / 'skills').glob('*/SKILL.md'))), 3)

    def test_install_refuses_dangling_skill_or_toolkit_links(self):
        for relative in ('.agents/skills/work-prepare', '.workkit'):
            with self.subTest(relative=relative):
                target = self.root / relative.replace('/', '-')
                target.mkdir()
                conflict = target / relative
                conflict.parent.mkdir(parents=True, exist_ok=True)
                conflict.symlink_to('missing-directory', target_is_directory=True)
                self.assertIn('already exists', self.run_work('install', str(target), ok=False))
                self.assertTrue(conflict.is_symlink())
                self.assertEqual(conflict.readlink(), Path('missing-directory'))
                self.assertFalse((target / '.work').exists())
                if relative != '.workkit':
                    self.assertFalse((target / '.workkit').exists())

    def test_installed_opencode_command_links_survive_relocation(self):
        target = self.root / 'module'
        custom = target / '.opencode' / 'commands' / 'custom.md'
        custom.parent.mkdir(parents=True)
        custom.write_text('Unrelated command')
        config = target / 'opencode.jsonc'
        config.write_text('{"commands": {"custom-json": {"template": "Keep me"}}}')
        self.run_work('install', str(target))
        self.assertEqual(custom.read_text(), 'Unrelated command')
        self.assertIn('Keep me', config.read_text())
        for command in (target / '.workkit' / 'commands').glob('*.md'):
            link = target / '.opencode' / 'commands' / command.name
            self.assertTrue(link.is_symlink())
            self.assertFalse(link.readlink().is_absolute())
            self.assertTrue(link.samefile(command))
        canonical = target / '.workkit' / 'commands' / 'work-task.md'
        canonical.write_text(canonical.read_text() + '\nProject-specific guidance.\n')
        self.assertIn('Project-specific', (target / '.opencode' / 'commands' / 'work-task.md').read_text())
        relocated = self.root / 'relocated project'
        shutil.copytree(target, relocated, symlinks=True)
        for command in (relocated / '.workkit' / 'commands').glob('*.md'):
            self.assertTrue((relocated / '.opencode' / 'commands' / command.name).samefile(command))
        launcher = relocated / '.workkit' / 'work'
        result = subprocess.run([str(launcher), '--root', str(relocated),
                                 'create', 'epic', 'Relocated runtime'],
                                cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(result.stdout.strip(), work.records(relocated))
        bin_dir = self.root / 'relocated bin'
        result = subprocess.run([str(launcher), 'setup', '--bin-dir', str(bin_dir)],
                                cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((bin_dir / 'work').resolve(), launcher)
        result = subprocess.run([str(bin_dir / 'work'), '--root', str(relocated), 'check'],
                                cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        # An installed runtime can in turn install its own canonical templates.
        another = self.root / 'another project'
        another.mkdir()
        result = subprocess.run([str(relocated / '.workkit' / 'work'), 'install', str(another)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Project-specific', (another / '.opencode' / 'commands' / 'work-task.md').read_text())

    def test_install_command_conflicts_change_nothing(self):
        for dangling in (False, True):
            with self.subTest(dangling=dangling):
                target = self.root / f'project-{dangling}'
                conflict = target / '.opencode' / 'commands' / 'work-task.md'
                conflict.parent.mkdir(parents=True)
                if dangling:
                    conflict.symlink_to('missing-template.md')
                else:
                    conflict.write_text('Custom task command')
                self.assertIn('command already exists', self.run_work('install', str(target), ok=False))
                self.assertFalse((target / '.workkit').exists())
                self.assertFalse((target / '.agents').exists())
                self.assertFalse((target / '.work').exists())
                self.assertFalse((target / 'AGENTS.md').exists())
                if dangling:
                    self.assertEqual(conflict.readlink(), Path('missing-template.md'))
                else:
                    self.assertEqual(conflict.read_text(), 'Custom task command')

    def test_lock_blocks_mutation_and_unknown_fields_survive(self):
        epic = self.create('epic')
        path, meta, body = work.records(self.root)[epic]
        work.write(path, dict(meta, custom={'preserve': True}), body)
        self.run_work('start', epic)
        self.assertEqual(work.records(self.root)[epic][1]['custom'], {'preserve': True})
        (self.root / '.work' / '.lock').mkdir()
        self.assertIn('Another work', self.run_work('review', epic, ok=False))


if __name__ == '__main__':
    unittest.main()
