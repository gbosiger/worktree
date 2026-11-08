"""Offline checks for release preparation, source assets, and publication retries."""
import gzip
import importlib.util
import io
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tarfile
import tempfile
import unittest
import zipfile

SOURCE = Path(__file__).resolve().parents[1]
SCRIPTS = SOURCE / '.github/scripts'
spec = importlib.util.spec_from_file_location('prepare_release', SCRIPTS / 'prepare-release.py')
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class PublishingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'source'
        self.root.mkdir()
        self.git('init', '-b', 'master')
        self.git('config', 'user.name', 'Release Test')
        self.git('config', 'user.email', 'release@example.invalid')
        self.git('config', 'commit.gpgsign', 'false')
        (self.root / '.work/tools').mkdir(parents=True)
        (self.root / '.work/tools/work.py').write_text("VERSION = '0.1.0'\n")
        (self.root / 'CHANGELOG.md').write_text(
            '# Changelog\n\n## Unreleased\n\n- Future work\n\n'
            '## 0.1.0 - 2026-11-08\n\n- First release\n\n## 0.0.1 - 2026-01-01\n\n- Old\n')
        (self.root / 'work').write_text('#!/bin/sh\necho 0.1.0\n')
        (self.root / 'work').chmod(0o755)
        (self.root / 'link').symlink_to('work')
        self.save()

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), *args],
                                       stderr=subprocess.PIPE).decode().strip()

    def save(self):
        self.git('add', '.')
        self.git('commit', '-m', 'Fixture')

    def tag(self, name='v0.1.0'):
        self.git('-c', 'tag.gpgsign=false', 'tag', '-a', name, '-m', name)

    def prepare(self, tag='v0.1.0', name='assets'):
        return release.prepare(self.root, tag, Path(self.temp.name) / name)

    def test_notes_and_archives_use_tagged_files_not_dirty_checkout(self):
        self.tag()
        (self.root / 'CHANGELOG.md').write_text('dirty notes')
        (self.root / 'untracked').write_text('not part of release')
        notes, tar, zip_path = self.prepare()
        self.assertEqual(notes.read_text(), '- First release\n')
        prefix = 'worktree-tickets-0.1.0/'
        with tarfile.open(fileobj=io.BytesIO(gzip.decompress(tar.read_bytes()))) as archive:
            self.assertEqual(archive.getmember(prefix + 'work').mode & 0o777, 0o755)
            self.assertEqual(archive.getmember(prefix + 'link').linkname, 'work')
            self.assertIn(b'First release', archive.extractfile(prefix + 'CHANGELOG.md').read())
            self.assertFalse(any('/.git/' in p or p.endswith('/untracked') for p in archive.getnames()))
        with zipfile.ZipFile(zip_path) as archive:
            self.assertEqual(archive.getinfo(prefix + 'work').external_attr >> 16 & 0o777, 0o755)
            self.assertTrue(stat.S_ISLNK(archive.getinfo(prefix + 'link').external_attr >> 16))
            self.assertEqual(archive.read(prefix + 'link'), b'work')
        with self.assertRaisesRegex(ValueError, 'already exist'):
            self.prepare()

    def test_tag_version_annotation_and_head_guards(self):
        for tag in ('--help', 'v0.1.0/escape', 'v0.1.0-rc1', 'v01.1.0'):
            with self.subTest(tag=tag), self.assertRaisesRegex(ValueError, 'stable version'):
                self.prepare(tag)
        self.git('-c', 'tag.gpgsign=false', 'tag', 'v0.1.0')
        with self.assertRaisesRegex(ValueError, 'annotated'):
            self.prepare()
        self.tag('v0.2.0')
        with self.assertRaisesRegex(ValueError, 'VERSION'):
            self.prepare('v0.2.0')
        self.git('tag', '-d', 'v0.1.0')
        self.tag()
        (self.root / 'new').write_text('new commit')
        self.save()
        with self.assertRaisesRegex(ValueError, 'HEAD'):
            self.prepare()

    def test_missing_empty_and_invalid_date_notes_fail_before_outputs(self):
        for index, text in enumerate(('## Unreleased\n', '## 0.1.0 - 2026-11-08\n\n',
                                      '## 0.1.0 - 2026-99-99\n\n- Bad date\n')):
            (self.root / 'CHANGELOG.md').write_text(text)
            self.save()
            self.tag()
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.prepare(name=str(index))
            self.assertFalse((Path(self.temp.name) / str(index)).exists())
            self.git('tag', '-d', 'v0.1.0')

    @unittest.skipUnless(shutil.which('unzip'), 'Unix unzip required for ZIP smoke test')
    def test_real_toolkit_installs_from_both_source_formats_without_history(self):
        for name in ('work', 'AGENTS.md', 'CONVENTION.md', 'LICENSE'):
            shutil.copy2(SOURCE / name, self.root / name)
        for name in ('docs', 'skills', 'templates', 'commands', '.agents', '.opencode'):
            shutil.copytree(SOURCE / name, self.root / name, symlinks=True)
        shutil.copy2(SOURCE / '.work/tools/work.py', self.root / '.work/tools/work.py')
        self.save()
        self.tag()
        self.prepare()
        result = subprocess.run(['bash', str(SCRIPTS / 'smoke-release.sh'), 'v0.1.0',
                                 str(Path(self.temp.name) / 'assets')],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_publish_retry_updates_same_release_after_upload_failure(self):
        self.tag()
        self.prepare()
        bin_dir = Path(self.temp.name) / 'bin'
        bin_dir.mkdir()
        stub = bin_dir / 'gh'
        stub.write_text('''#!/usr/bin/env python3
import os, pathlib, sys
root = pathlib.Path(os.environ['STUB_ROOT'])
with (root / 'calls').open('a') as log:
    log.write(' '.join(sys.argv[1:]) + '\\n')
command = sys.argv[2]
if command == 'view':
    sys.exit(0 if (root / 'exists').exists() else 1)
if command == 'create':
    (root / 'exists').touch()
if command == 'upload' and not (root / 'failed').exists():
    (root / 'failed').touch()
    sys.exit(1)
''')
        stub.chmod(0o755)
        env = dict(os.environ, PATH=str(bin_dir) + os.pathsep + os.environ['PATH'],
                   STUB_ROOT=self.temp.name)
        command = ['bash', str(SCRIPTS / 'publish-release.sh'), 'v0.1.0',
                   str(Path(self.temp.name) / 'assets')]
        self.assertNotEqual(subprocess.run(command, env=env).returncode, 0)
        calls = (Path(self.temp.name) / 'calls').read_text()
        self.assertNotIn('release edit', calls)
        subprocess.run(command, env=env, check=True)
        calls = (Path(self.temp.name) / 'calls').read_text()
        self.assertEqual(calls.count('release create'), 1)
        self.assertEqual(calls.count('release upload'), 2)
        self.assertEqual(calls.count('release edit'), 1)
        self.assertIn('--draft=false --prerelease=false --latest', calls)


if __name__ == '__main__':
    unittest.main()
