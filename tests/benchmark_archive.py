"""Repeatable archive lookup benchmark; no writes outside a disposable repository.

python3 tests/benchmark_archive.py --commits 3000 --tickets 2000 --batches 20
Use --baseline /path/to/work.py to compare native file-history readers.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import statistics
import subprocess
import tempfile
import time
from unittest.mock import patch


def runtime(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def content(identity, kind='task', parent='E-1234abcd', status='done'):
    meta = dict(id=identity, kind=kind, title='Benchmark ticket', status=status,
                parent=parent, depends_on=[], implementer='agent', reviewer='agent')
    return ('---\n' + json.dumps(meta) + '\n---\n# Benchmark ticket\n\n'
            '## Acceptance criteria\n\n- [x] Verified\n\n## Acceptance record\n\n'
            '2026-11-07T12:00:00+00:00 — agent: Benchmark fixture\n').encode()


def fixture(root, args):
    subprocess.run(['git', 'init', '-q', '-b', 'main', str(root)], check=True)
    stream = bytearray()

    def data(value):
        stream.extend(f'data {len(value)}\n'.encode() + value + b'\n')

    def commit(number, message):
        stream.extend(b'commit refs/heads/main\n')
        stream.extend(f'committer Benchmark <bench@example.invalid> {1794052800 + number} +0000\n'.encode())
        data(message.encode())

    ids = [f'T-{number:08x}' for number in range(args.tickets)]
    folder = '.work/wip/E-1234abcd-benchmark'
    commit(0, 'Save accepted tickets')
    stream.extend(f'M 100644 inline {folder}/README.md\n'.encode())
    data(content('E-1234abcd', kind='epic', parent=None, status='wip'))
    for identity in ids:
        stream.extend(f'M 100644 inline {folder}/done/{identity}-benchmark.md\n'.encode())
        data(content(identity))
    stream.extend(b'\n')
    for batch in range(args.batches):
        selected = ids[batch * args.tickets // args.batches:(batch + 1) * args.tickets // args.batches]
        message = 'Clean up completed work'
        commit(batch + 1, message)
        for identity in selected:
            stream.extend(f'D {folder}/done/{identity}-benchmark.md\n'.encode())
        stream.extend(b'\n')
    for number in range(args.batches + 1, args.commits):
        commit(number, f'Unrelated application change {number}')
        stream.extend(b'M 100644 inline application.txt\n')
        data(str(number).encode())
        stream.extend(b'\n')
    subprocess.run(['git', '-C', str(root), 'fast-import', '--quiet'], input=stream,
                   check=True, capture_output=True)
    subprocess.run(['git', '-C', str(root), 'gc', '--quiet'], check=True, capture_output=True)


def measure(module, root, args):
    durations, counts = [], []
    for _ in range(args.repeat):
        # Each call reconstructs the lookup; no persistent or cross-call cache.
        with patch.object(module, '_archive_git', wraps=module._archive_git) as calls:
            started = time.perf_counter()
            records = module.archive_history(root)
            durations.append(time.perf_counter() - started)
            counts.append(calls.call_count)
        if len(records) != args.tickets:
            raise RuntimeError(f'Expected {args.tickets} records, found {len(records)}')
    return f'median {statistics.median(durations):.3f}s; Git processes {counts}; runs ' + ', '.join(f'{n:.3f}s' for n in durations)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--commits', type=int, default=3000)
    parser.add_argument('--tickets', type=int, default=2000)
    parser.add_argument('--batches', type=int, default=20)
    parser.add_argument('--repeat', type=int, default=3)
    parser.add_argument('--baseline', type=Path)
    args = parser.parse_args()
    if not (0 < args.batches <= args.tickets and args.commits > args.batches and args.repeat > 0):
        parser.error('Require 0 < batches <= tickets, commits > batches, and repeat > 0')
    preferred = Path('/tmp/opencode')
    with tempfile.TemporaryDirectory(prefix='archive-benchmark-', dir=preferred if preferred.is_dir() else None) as temp:
        root = Path(temp) / 'repo'
        fixture(root, args)
        print(f'{args.commits} commits; {args.tickets} tickets; {args.batches} deletion commits; packed Git objects')
        source = Path(__file__).resolve().parents[1] / '.work/tools/work.py'
        print('Current: ' + measure(runtime(source, 'benchmark_current'), root, args))
        if args.baseline:
            print('Baseline: ' + measure(runtime(args.baseline, 'benchmark_baseline'), root, args))


if __name__ == '__main__':
    main()
