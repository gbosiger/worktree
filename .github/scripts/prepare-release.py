"""Prepare notes and source assets from an annotated stable-version tag; no network."""
import argparse
import ast
import datetime
import gzip
from pathlib import Path
import re
import subprocess


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args])


def prepare(root, tag, output):
    if not re.fullmatch(r'v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)', tag):
        raise ValueError('Expected a stable version tag, e.g. v0.1.0')
    ref = 'refs/tags/' + tag
    if git(root, 'cat-file', '-t', ref).strip() != b'tag':
        raise ValueError('Release tag must be annotated (signed when available)')
    commit = git(root, 'rev-parse', ref + '^{commit}').strip().decode('ascii')
    if git(root, 'rev-parse', 'HEAD').strip().decode('ascii') != commit:
        raise ValueError('HEAD must be the exact tagged commit that passed validation')
    version = tag[1:]
    source = git(root, 'show', commit + ':.work/tools/work.py').decode('utf-8')
    versions = [node.value.value for node in ast.parse(source).body
                if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant)
                and any(isinstance(target, ast.Name) and target.id == 'VERSION'
                        for target in node.targets)]
    if versions != [version]:
        raise ValueError('Tag and toolkit VERSION must match')
    changelog = git(root, 'show', commit + ':CHANGELOG.md').decode('utf-8')
    section = re.search(r'^## ' + re.escape(version) + r' - (\d{4}-\d{2}-\d{2})\n'
                        r'(.*?)(?=^## |\Z)', changelog, re.MULTILINE | re.DOTALL)
    if not section or not section[2].strip():
        raise ValueError('Changelog needs a nonempty dated section for this version')
    datetime.date.fromisoformat(section[1])
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    stem = 'worktree-tickets-' + version
    paths = [output / name for name in ('notes.md', stem + '.tar.gz', stem + '.zip')]
    if any(path.exists() or path.is_symlink() for path in paths):
        raise ValueError('Output files already exist; use a fresh output directory')
    tar = git(root, '-c', 'tar.umask=0022', 'archive', '--format=tar',
              '--prefix=' + stem + '/', commit)
    zip_data = git(root, 'archive', '--format=zip', '--prefix=' + stem + '/', commit)
    paths[0].write_text(section[2].strip() + '\n', encoding='utf-8')
    paths[1].write_bytes(gzip.compress(tar, mtime=0))
    paths[2].write_bytes(zip_data)
    return paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('tag')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    try:
        for path in prepare(Path.cwd(), args.tag, args.output):
            print(path)
    except (ValueError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f'Release preparation failed: {exc}\n')


if __name__ == '__main__':
    main()
