#!/usr/bin/env bash
set -euo pipefail
tag=${1:?version tag required}
assets=${2:?asset directory required}
[[ $tag =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]
assets=$(realpath "$assets")
scratch=$(mktemp -d)
trap 'rm -rf -- "$scratch"' EXIT
version=${tag#v}
for format in tar.gz zip; do
  destination="$scratch/$format"
  mkdir -p "$destination"
  if [[ $format == tar.gz ]]; then
    tar -xzf "$assets/worktree-tickets-$version.tar.gz" -C "$destination"
  else
    unzip -q "$assets/worktree-tickets-$version.zip" -d "$destination"
  fi
  source="$destination/worktree-tickets-$version"
  [[ -x $source/work ]]
  [[ $(cd / && "$source/work" --version) == "$version" ]]
  # Isolate PATH setup as well as project installation from the real user's HOME.
  mkdir -p "$destination/home"
  HOME="$destination/home" "$source/work" setup
  [[ $("$destination/home/.local/bin/work" --version) == "$version" ]]
  mkdir -p "$destination/project"
  "$source/work" install "$destination/project"
  local_work="$destination/project/.workkit/work"
  [[ $("$local_work" --version) == "$version" ]]
  [[ $(cat "$destination/project/.workkit/VERSION") == "$version" ]]
  epic=$("$local_work" --root "$destination/project" create epic 'Artifact smoke test')
  "$local_work" --root "$destination/project" create task 'Install works' --parent "$epic"
  "$local_work" --root "$destination/project" check
  python3 - "$source" "$destination/project" <<'PY'
from pathlib import Path
import sys
for root in map(Path, sys.argv[1:]):
    for directory in ('.agents/skills', '.opencode/commands'):
        links = list((root / directory).iterdir())
        assert links, directory
        assert all(p.is_symlink() and p.exists() and not p.readlink().is_absolute()
                   for p in links), (root, directory)
PY
done
